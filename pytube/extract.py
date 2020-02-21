# -*- coding: utf-8 -*-
"""This module contains all non-cipher related data extraction logic."""
import json
import logging
import re
from collections import OrderedDict
from html.parser import HTMLParser
from typing import Any, Optional, Tuple, List, Dict
from urllib.parse import quote, parse_qs, unquote, parse_qsl
from urllib.parse import urlencode

from pytube.cipher import Cipher
from pytube.exceptions import RegexMatchError, HTMLParseError, LiveStreamError
from pytube.helpers import regex_search

logger = logging.getLogger(__name__)


class PytubeHTMLParser(HTMLParser):
    in_vid_descr = False
    in_vid_descr_br = False
    vid_descr = ""

    def handle_starttag(self, tag, attrs):
        if tag == "p":
            for attr in attrs:
                if attr[0] == "id" and attr[1] == "eow-description":
                    self.in_vid_descr = True

    def handle_endtag(self, tag):
        if self.in_vid_descr and tag == "p":
            self.in_vid_descr = False

    def handle_startendtag(self, tag, attrs):
        if self.in_vid_descr and tag == "br":
            self.in_vid_descr_br = True

    def handle_data(self, data):
        if self.in_vid_descr_br:
            self.vid_descr += f"\n{data}"
            self.in_vid_descr_br = False
        elif self.in_vid_descr:
            self.vid_descr += data

    def error(self, message):
        raise HTMLParseError(message)


def is_age_restricted(watch_html: str) -> bool:
    """Check if content is age restricted.

    :param str watch_html:
        The html contents of the watch page.
    :rtype: bool
    :returns:
        Whether or not the content is age restricted.
    """
    try:
        regex_search(r"og:restrictions:age", watch_html, group=0)
    except RegexMatchError:
        return False
    return True


def video_id(url: str) -> str:
    """Extract the ``video_id`` from a YouTube url.

    This function supports the following patterns:

    - :samp:`https://youtube.com/watch?v={video_id}`
    - :samp:`https://youtube.com/embed/{video_id}`
    - :samp:`https://youtu.be/{video_id}`

    :param str url:
        A YouTube url containing a video id.
    :rtype: str
    :returns:
        YouTube video id.
    """
    return regex_search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url, group=1)


def video_info_url(video_id: str, watch_url: str) -> str:
    """Construct the video_info url.

    :param str video_id:
        A YouTube video identifier.
    :param str watch_url:
        A YouTube watch url.
    :rtype: str
    :returns:
        :samp:`https://youtube.com/get_video_info` with necessary GET
        parameters.
    """
    params = OrderedDict(
        [
            ("video_id", video_id),
            ("el", "$el"),
            ("ps", "default"),
            ("eurl", quote(watch_url)),
            ("hl", "en_US"),
        ]
    )
    return _video_info_url(params)


def video_info_url_age_restricted(video_id: str, embed_html: str) -> str:
    """Construct the video_info url.

    :param str video_id:
        A YouTube video identifier.
    :param str embed_html:
        The html contents of the embed page (for age restricted videos).
    :rtype: str
    :returns:
        :samp:`https://youtube.com/get_video_info` with necessary GET
        parameters.
    """
    try:
        sts = regex_search(r'"sts"\s*:\s*(\d+)', embed_html, group=1)
    except RegexMatchError:
        sts = ""
    # Here we use ``OrderedDict`` so that the output is consistent between
    # Python 2.7+.
    eurl = f"https://youtube.googleapis.com/v/{video_id}"
    params = OrderedDict([("video_id", video_id), ("eurl", eurl), ("sts", sts),])
    return _video_info_url(params)


def _video_info_url(params: OrderedDict) -> str:
    return "https://youtube.com/get_video_info?" + urlencode(params)


def js_url(html: str) -> str:
    """Get the base JavaScript url.

    Construct the base JavaScript url, which contains the decipher
    "transforms".

    :param str html:
        The html contents of the watch page.
    """
    base_js = get_ytplayer_config(html)["assets"]["js"]
    return "https://youtube.com" + base_js


def mime_type_codec(mime_type_codec: str) -> Tuple[str, List[str]]:
    """Parse the type data.

    Breaks up the data in the ``type`` key of the manifest, which contains the
    mime type and codecs serialized together, and splits them into separate
    elements.

    **Example**:

    mime_type_codec('audio/webm; codecs="opus"') -> ('audio/webm', ['opus'])

    :param str mime_type_codec:
        String containing mime type and codecs.
    :rtype: tuple
    :returns:
        The mime type and a list of codecs.

    """
    pattern = r"(\w+\/\w+)\;\scodecs=\"([a-zA-Z-0-9.,\s]*)\""
    regex = re.compile(pattern)
    results = regex.search(mime_type_codec)
    if not results:
        raise RegexMatchError(caller="mime_type_codec", pattern=pattern)
    mime_type, codecs = results.groups()
    return mime_type, [c.strip() for c in codecs.split(",")]


def get_ytplayer_config(html: str) -> Any:
    """Get the YouTube player configuration data from the watch html.

    Extract the ``ytplayer_config``, which is json data embedded within the
    watch html and serves as the primary source of obtaining the stream
    manifest data.

    :param str html:
        The html contents of the watch page.
    :rtype: str
    :returns:
        Substring of the html containing the encoded manifest data.
    """
    config_patterns = [
        r";ytplayer\.config\s*=\s*({.*?});",
        r";ytplayer\.config\s*=\s*({.+?});ytplayer",
        r";yt\.setConfig\(\{'PLAYER_CONFIG':\s*({.*})}\);",
        r";yt\.setConfig\(\{'PLAYER_CONFIG':\s*({.*})(,'EXPERIMENT_FLAGS'|;)",  # noqa: E501
    ]
    logger.debug("finding initial function name")
    for pattern in config_patterns:
        regex = re.compile(pattern)
        function_match = regex.search(html)
        if function_match:
            logger.debug("finished regex search, matched: %s", pattern)
            yt_player_config = function_match.group(1)
            return json.loads(yt_player_config)

    raise RegexMatchError(caller="get_ytplayer_config", pattern="config_patterns")


def _get_vid_descr(html: Optional[str]) -> str:
    html_parser = PytubeHTMLParser()
    if html:
        html_parser.feed(html)
    return html_parser.vid_descr


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
    cipher = Cipher(js=js)
    stream_manifest = config_args[fmt]

    for i, stream in enumerate(stream_manifest):
        try:
            url: str = stream["url"]
        except KeyError:
            live_stream = (
                json.loads(config_args["player_response"])
                .get("playabilityStatus", {},)
                .get("liveStreamability")
            )
            if live_stream:
                raise LiveStreamError("UNKNOWN")
        # 403 Forbidden fix.
        if "signature" in url or (
            "s" not in stream and ("&sig=" in url or "&lsig=" in url)
        ):
            # For certain videos, YouTube will just provide them pre-signed, in
            # which case there's no real magic to download them and we can skip
            # the whole signature descrambling entirely.
            logger.debug("signature found, skip decipher")
            continue

        signature = cipher.get_signature(ciphered_signature=stream["s"])

        logger.debug("finished descrambling signature for itag=%s", stream["itag"])
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
    otf_type = "FORMAT_STREAM_TYPE_OTF"

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
                    "url": format_item["url"],
                    "type": format_item["mimeType"],
                    "quality": format_item["quality"],
                    "itag": format_item["itag"],
                    "bitrate": format_item.get("bitrate"),
                    "is_otf": (format_item.get("type") == otf_type),
                }
                for format_item in formats
            ]
        except KeyError:
            cipher_url = [
                parse_qs(formats[i]["cipher"]) for i, data in enumerate(formats)
            ]
            stream_data[key] = [
                {
                    "url": cipher_url[i]["url"][0],
                    "s": cipher_url[i]["s"][0],
                    "type": format_item["mimeType"],
                    "quality": format_item["quality"],
                    "itag": format_item["itag"],
                    "bitrate": format_item.get("bitrate"),
                    "is_otf": (format_item.get("type") == otf_type),
                }
                for i, format_item in enumerate(formats)
            ]
    else:
        stream_data[key] = [
            {k: unquote(v) for k, v in parse_qsl(i)}
            for i in stream_data[key].split(",")
        ]

    logger.debug("applying descrambler")
