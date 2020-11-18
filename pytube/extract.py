# -*- coding: utf-8 -*-
"""This module contains all non-cipher related data extraction logic."""
import json
import logging
import urllib.parse
import re
from collections import OrderedDict
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from urllib.parse import parse_qs
from urllib.parse import parse_qsl
from urllib.parse import quote
from urllib.parse import unquote
from urllib.parse import urlencode

from pytube.cipher import Cipher
from pytube.exceptions import LiveStreamError
from pytube.exceptions import RegexMatchError
from pytube.helpers import regex_search
from pytube.metadata import YouTubeMetadata

logger = logging.getLogger(__name__)


def publish_date(watch_html: str):
    """Extract publish date
    :param str watch_html:
        The html contents of the watch page.
    :rtype: str
    :returns:
        Publish date of the video.
    """
    try:
        result = regex_search(
            r"(?<=itemprop=\"datePublished\" content=\")\d{4}-\d{2}-\d{2}",
            watch_html, group=0
        )
    except RegexMatchError:
        return None
    return datetime.strptime(result, '%Y-%m-%d')


def recording_available(watch_html):
    """Check if live stream recording is available.

    :param str watch_html:
        The html contents of the watch page.
    :rtype: bool
    :returns:
        Whether or not the content is private.
    """
    unavailable_strings = [
        'This live stream recording is not available.'
    ]
    for string in unavailable_strings:
        if string in watch_html:
            return False
    return True


def is_private(watch_html):
    """Check if content is private.

    :param str watch_html:
        The html contents of the watch page.
    :rtype: bool
    :returns:
        Whether or not the content is private.
    """
    private_strings = [
        "This is a private video. Please sign in to verify that you may see it.",
        "\"simpleText\":\"Private video\"",
        "This video is private."
    ]
    for string in private_strings:
        if string in watch_html:
            return True
    return False


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


def playlist_id(url: str) -> str:
    """Extract the ``playlist_id`` from a YouTube url.

    This function supports the following patterns:

    - :samp:`https://youtube.com/playlist?list={playlist_id}`
    - :samp:`https://youtube.com/watch?v={video_id}&list={playlist_id}`

    :param str url:
        A YouTube url containing a playlist id.
    :rtype: str
    :returns:
        YouTube playlist id.
    """
    parsed = urllib.parse.urlparse(url)
    return parse_qs(parsed.query)['list'][0]


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
    params = OrderedDict(
        [("video_id", video_id), ("eurl", eurl), ("sts", sts),]
    )
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
    try:
        base_js = get_ytplayer_config(html)['assets']['js']
    except (KeyError, RegexMatchError):
        base_js = get_ytplayer_js(html)
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


def get_ytplayer_js(html: str) -> Any:
    """Get the YouTube player base JavaScript path.

    :param str html
        The html contents of the watch page.
    :rtype: str
    :returns:
        Path to YouTube's base.js file.
    """
    js_url_patterns = [
        r"(/s/player/[\w\d]+/[\w\d_/.]+/base\.js)"
    ]
    for pattern in js_url_patterns:
        regex = re.compile(pattern)
        function_match = regex.search(html)
        if function_match:
            logger.debug("finished regex search, matched: %s", pattern)
            yt_player_js = function_match.group(1)
            return yt_player_js

    raise RegexMatchError(
        caller="get_ytplayer_js", pattern="js_url_patterns"
    )


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
    logger.debug("finding initial function name")
    config_patterns = [
        r"ytplayer\.config\s*=\s*({.+?});ytplayer",
        r"ytInitialPlayerResponse\s*=\s*({.+?(?<!gdpr)});"
    ]
    for pattern in config_patterns:
        regex = re.compile(pattern)
        function_match = regex.search(html)
        if function_match:
            logger.debug("finished regex search, matched: %s", pattern)
            yt_player_config = function_match.group(1)
            return json.loads(yt_player_config)

    # setConfig() needs to be handled a little differently.
    # We want to parse the entire argument to setConfig()
    #  and use then load that as json to find PLAYER_CONFIG
    #  inside of it.
    setconfig_patterns = [
        r"yt\.setConfig\((.*['\"]PLAYER_CONFIG['\"]:\s*{.+?})\);"
    ]
    for pattern in setconfig_patterns:
        regex = re.compile(pattern)
        function_match = regex.search(html)
        if function_match:
            logger.debug("finished regex search, matched: %s", pattern)
            yt_config = function_match.group(1)
            return json.loads(yt_config)['PLAYER_CONFIG']

    raise RegexMatchError(
        caller="get_ytplayer_config", pattern="config_patterns, setconfig_patterns"
    )


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

        logger.debug(
            "finished descrambling signature for itag=%s", stream["itag"]
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
    otf_type = "FORMAT_STREAM_TYPE_OTF"

    if key == "url_encoded_fmt_stream_map" and not stream_data.get(
        "url_encoded_fmt_stream_map"
    ):
        if isinstance(stream_data["player_response"], str):
            streaming_data = json.loads(stream_data["player_response"])["streamingData"]
        else:
            streaming_data = stream_data["player_response"]
        formats = []
        if 'formats' in streaming_data.keys():
            formats.extend(streaming_data['formats'])
        if 'adaptiveFormats' in streaming_data.keys():
            formats.extend(streaming_data['adaptiveFormats'])
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
                parse_qs(
                    data[
                        "cipher" if "cipher" in data.keys() else "signatureCipher"
                    ]
                )
                for data in formats
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


def initial_data(watch_html: str) -> str:
    """Extract the ytInitialData json from the watch_html page.

    This mostly contains metadata necessary for rendering the page on-load,
    such as video information, copyright notices, etc.

    @param watch_html: Html of the watch page
    @return:
    """
    initial_data_pattern = r"window\[['\"]ytInitialData['\"]]\s*=\s*([^\n]+);"
    try:
        return regex_search(initial_data_pattern, watch_html, 1)
    except RegexMatchError:
        return "{}"


def metadata(initial_data) -> Optional[YouTubeMetadata]:
    """Get the informational metadata for the video.

    e.g.:
    [
        {
            'Song': '강남스타일(Gangnam Style)',
            'Artist': 'PSY',
            'Album': 'PSY SIX RULES Pt.1',
            'Licensed to YouTube by': 'YG Entertainment Inc. [...]'
        }
    ]

    :rtype: YouTubeMetadata
    """
    try:
        metadata_rows: List = initial_data["contents"]["twoColumnWatchNextResults"][
            "results"]["results"]["contents"][1]["videoSecondaryInfoRenderer"][
            "metadataRowContainer"]["metadataRowContainerRenderer"]["rows"]
    except (KeyError, IndexError):
        # If there's an exception accessing this data, it probably doesn't exist.
        return YouTubeMetadata([])

    # Rows appear to only have "metadataRowRenderer" or "metadataRowHeaderRenderer"
    #  and we only care about the former, so we filter the others
    metadata_rows = filter(
        lambda x: "metadataRowRenderer" in x.keys(),
        metadata_rows
    )

    # We then access the metadataRowRenderer key in each element
    #  and build a metadata object from this new list
    metadata_rows = [x["metadataRowRenderer"] for x in metadata_rows]

    return YouTubeMetadata(metadata_rows)
