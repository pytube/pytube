# -*- coding: utf-8 -*-
"""Applies in-place data mutations."""

import json
import logging
import pprint
from typing import Dict

from pytube import cipher
from urllib import request
from urllib.parse import parse_qsl
from urllib.parse import parse_qs
from urllib.parse import unquote
from pytube.exceptions import LiveStreamError


logger = logging.getLogger(__name__)


def apply_signature(config_args: Dict, fmt: str, js: str) -> None:
    """Apply the decrypted signature to the stream manifest.

    :param dict config_args:
        Details of the media streams available.
    :param str fmt:
        Key in stream manifests (``ytplayer_config``) containing progressive
        download or adaptive streams (e.g.: ``url_encoded_fmt_stream_map`` or
        ``adaptive_fmts``).
    :param str js:
        The contents of the base.js asset file.

    """
    stream_manifest = config_args[fmt]
    live_stream = (
        json.loads(config_args["player_response"])
        .get("playabilityStatus", {},)
        .get("liveStreamability")
    )
    for i, stream in enumerate(stream_manifest):
        try:
            url: str = stream["url"]
        except KeyError:
            if live_stream:
                raise LiveStreamError("Video is currently being streamed live")
        # 403 Forbidden fix.
        if "signature" in url or (
            "s" not in stream and ("&sig=" in url or "&lsig=" in url)
        ):
            # For certain videos, YouTube will just provide them pre-signed, in
            # which case there's no real magic to download them and we can skip
            # the whole signature descrambling entirely.
            logger.debug("signature found, skip decipher")
            continue

        if js is not None:
            signature = cipher.get_signature(js, stream["s"])
        else:
            # signature not present in url (line 33), need js to descramble
            # TypeError caught in __main__
            raise TypeError("JS is None")

        logger.debug(
            "finished descrambling signature for itag=%s\n%s",
            stream["itag"],
            pprint.pformat({"s": stream["s"], "signature": signature,}, indent=2,),
        )
        # 403 forbidden fix
        stream_manifest[i]["url"] = url + "&sig=" + signature


def apply_descrambler(stream_data: Dict, key: str) -> None:
    """Apply various in-place transforms to YouTube's media stream data.

    Creates a ``list`` of dictionaries by string splitting on commas, then
    taking each list item, parsing it as a query string, converting it to a
    ``dict`` and unquoting the value.

    :param dict stream_data:
        Dictionary containing query string encoded values.
    :param str key:
        Name of the key in dictionary.

    **Example**:

    >>> d = {'foo': 'bar=1&var=test,em=5&t=url%20encoded'}
    >>> apply_descrambler(d, 'foo')
    >>> print(d)
    {'foo': [{'bar': '1', 'var': 'test'}, {'em': '5', 't': 'url encoded'}]}

    """
    if key == "url_encoded_fmt_stream_map" and not stream_data.get(
        "url_encoded_fmt_stream_map"
    ):
        formats = json.loads(stream_data["player_response"])["streamingData"]["formats"]
        formats.extend(
            json.loads(stream_data["player_response"])["streamingData"][
                "adaptiveFormats"
            ]
        )
        try:
            stream_data[key] = [
                {
                    u"url": format_item[u"url"],
                    u"type": format_item[u"mimeType"],
                    u"quality": format_item[u"quality"],
                    u"itag": format_item[u"itag"],
                }
                for format_item in formats
            ]
        except KeyError:
            cipher_url = [
                parse_qs(formats[i]["cipher"]) for i, data in enumerate(formats)
            ]
            stream_data[key] = [
                {
                    u"url": cipher_url[i][u"url"][0],
                    u"s": cipher_url[i][u"s"][0],
                    u"type": format_item[u"mimeType"],
                    u"quality": format_item[u"quality"],
                    u"itag": format_item[u"itag"],
                }
                for i, format_item in enumerate(formats)
            ]
    else:
        stream_data[key] = [
            {k: unquote(v) for k, v in parse_qsl(i)}
            for i in stream_data[key].split(",")
        ]
    logger.debug(
        "applying descrambler\n%s", pprint.pformat(stream_data[key], indent=2),
    )


def install_proxy(proxy_handler: Dict[str, str]) -> None:
    proxy_support = request.ProxyHandler(proxy_handler)
    opener = request.build_opener(proxy_support)
    request.install_opener(opener)
