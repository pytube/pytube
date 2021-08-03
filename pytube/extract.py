"""This module contains all non-cipher related data extraction logic."""
import logging
import urllib.parse
import re
from collections import OrderedDict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, quote, urlencode, urlparse

from pytube.cipher import Cipher
from pytube.exceptions import HTMLParseError, LiveStreamError, RegexMatchError
from pytube.helpers import regex_search
from pytube.metadata import YouTubeMetadata
from pytube.parser import parse_for_object, parse_for_all_objects


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


def playability_status(watch_html: str) -> (str, str):
    """Return the playability status and status explanation of a video.

    For example, a video may have a status of LOGIN_REQUIRED, and an explanation
    of "This is a private video. Please sign in to verify that you may see it."

    This explanation is what gets incorporated into the media player overlay.

    :param str watch_html:
        The html contents of the watch page.
    :rtype: bool
    :returns:
        Playability status and reason of the video.
    """
    player_response = initial_player_response(watch_html)
    status_dict = player_response.get('playabilityStatus', {})
    if 'liveStreamability' in status_dict:
        return 'LIVE_STREAM', 'Video is a live stream.'
    if 'status' in status_dict:
        if 'reason' in status_dict:
            return status_dict['status'], [status_dict['reason']]
        if 'messages' in status_dict:
            return status_dict['status'], status_dict['messages']
    return None, [None]


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


def channel_name(url: str) -> str:
    """Extract the ``channel_name`` or ``channel_id`` from a YouTube url.

    This function supports the following patterns:

    - :samp:`https://youtube.com/c/{channel_name}/*`
    - :samp:`https://youtube.com/channel/{channel_id}/*
    - :samp:`https://youtube.com/u/{channel_name}/*`
    - :samp:`https://youtube.com/user/{channel_id}/*

    :param str url:
        A YouTube url containing a channel name.
    :rtype: str
    :returns:
        YouTube channel name.
    """
    patterns = [
        r"(?:\/(c)\/([%\d\w_\-]+)(\/.*)?)",
        r"(?:\/(channel)\/([%\w\d_\-]+)(\/.*)?)",
        r"(?:\/(u)\/([%\d\w_\-]+)(\/.*)?)",
        r"(?:\/(user)\/([%\w\d_\-]+)(\/.*)?)"
    ]
    for pattern in patterns:
        regex = re.compile(pattern)
        function_match = regex.search(url)
        if function_match:
            logger.debug("finished regex search, matched: %s", pattern)
            uri_style = function_match.group(1)
            uri_identifier = function_match.group(2)
            return f'/{uri_style}/{uri_identifier}'

    raise RegexMatchError(
        caller="channel_name", pattern="patterns"
    )


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
            ("html5", "1"),
            ("c", "TVHTML5"),
            ("cver", "7.20201028"),
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
        [
            ("video_id", video_id),
            ("eurl", eurl),
            ("sts", sts),
            ("html5", "1"),
            ("c", "TVHTML5"),
            ("cver", "7.20201028"),
        ]
    )
    return _video_info_url(params)


def _video_info_url(params: OrderedDict) -> str:
    return "https://www.youtube.com/get_video_info?" + urlencode(params)


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
        r"ytplayer\.config\s*=\s*",
        r"ytInitialPlayerResponse\s*=\s*"
    ]
    for pattern in config_patterns:
        # Try each pattern consecutively if they don't find a match
        try:
            return parse_for_object(html, pattern)
        except HTMLParseError as e:
            logger.debug(f'Pattern failed: {pattern}')
            logger.debug(e)
            continue

    # setConfig() needs to be handled a little differently.
    # We want to parse the entire argument to setConfig()
    #  and use then load that as json to find PLAYER_CONFIG
    #  inside of it.
    setconfig_patterns = [
        r"yt\.setConfig\(.*['\"]PLAYER_CONFIG['\"]:\s*"
    ]
    for pattern in setconfig_patterns:
        # Try each pattern consecutively if they don't find a match
        try:
            return parse_for_object(html, pattern)
        except HTMLParseError:
            continue

    raise RegexMatchError(
        caller="get_ytplayer_config", pattern="config_patterns, setconfig_patterns"
    )


def get_ytcfg(html: str) -> str:
    """Get the entirety of the ytcfg object.

    This is built over multiple pieces, so we have to find all matches and
    combine the dicts together.

    :param str html:
        The html contents of the watch page.
    :rtype: str
    :returns:
        Substring of the html containing the encoded manifest data.
    """
    ytcfg = {}
    ytcfg_patterns = [
        r"ytcfg\s=\s",
        r"ytcfg\.set\("
    ]
    for pattern in ytcfg_patterns:
        # Try each pattern consecutively and try to build a cohesive object
        try:
            found_objects = parse_for_all_objects(html, pattern)
            for obj in found_objects:
                ytcfg.update(obj)
        except HTMLParseError:
            continue

    if len(ytcfg) > 0:
        return ytcfg

    raise RegexMatchError(
        caller="get_ytcfg", pattern="ytcfg_pattenrs"
    )


def apply_signature(stream_manifest: Dict, vid_info: Dict, js: str) -> None:
    """Apply the decrypted signature to the stream manifest.

    :param dict stream_manifest:
        Details of the media streams available.
    :param str js:
        The contents of the base.js asset file.

    """
    cipher = Cipher(js=js)

    for i, stream in enumerate(stream_manifest):
        try:
            url: str = stream["url"]
        except KeyError:
            live_stream = (
                vid_info.get("playabilityStatus", {},)
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
        parsed_url = urlparse(url)

        # Convert query params off url to dict
        query_params = parse_qs(urlparse(url).query)
        query_params = {
            k: v[0] for k,v in query_params.items()
        }
        query_params['sig'] = signature
        if 'ratebypass' not in query_params.keys():
            # Cipher n to get the updated value

            initial_n = list(query_params['n'])
            new_n = cipher.calculate_n(initial_n)
            query_params['n'] = new_n

        url = f'{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}?{urlencode(query_params)}'  # noqa:E501

        # 403 forbidden fix
        stream_manifest[i]["url"] = url


def apply_descrambler(stream_data: Dict) -> None:
    """Apply various in-place transforms to YouTube's media stream data.

    Creates a ``list`` of dictionaries by string splitting on commas, then
    taking each list item, parsing it as a query string, converting it to a
    ``dict`` and unquoting the value.

    :param dict stream_data:
        Dictionary containing query string encoded values.

    **Example**:

    >>> d = {'foo': 'bar=1&var=test,em=5&t=url%20encoded'}
    >>> apply_descrambler(d, 'foo')
    >>> print(d)
    {'foo': [{'bar': '1', 'var': 'test'}, {'em': '5', 't': 'url encoded'}]}

    """
    if 'url' in stream_data:
        return None

    # Merge formats and adaptiveFormats into a single list
    formats = []
    if 'formats' in stream_data.keys():
        formats.extend(stream_data['formats'])
    if 'adaptiveFormats' in stream_data.keys():
        formats.extend(stream_data['adaptiveFormats'])

    # Extract url and s from signatureCiphers as necessary
    for data in formats:
        if 'url' not in data:
            if 'signatureCipher' in data:
                cipher_url = parse_qs(data['signatureCipher'])
                data['url'] = cipher_url['url'][0]
                data['s'] = cipher_url['s'][0]
        data['is_otf'] = data.get('type') == 'FORMAT_STREAM_TYPE_OTF'

    logger.debug("applying descrambler")
    return formats


def initial_data(watch_html: str) -> str:
    """Extract the ytInitialData json from the watch_html page.

    This mostly contains metadata necessary for rendering the page on-load,
    such as video information, copyright notices, etc.

    @param watch_html: Html of the watch page
    @return:
    """
    patterns = [
        r"window\[['\"]ytInitialData['\"]]\s*=\s*",
        r"ytInitialData\s*=\s*"
    ]
    for pattern in patterns:
        try:
            return parse_for_object(watch_html, pattern)
        except HTMLParseError:
            pass

    raise RegexMatchError(caller='initial_data', pattern='initial_data_pattern')


def initial_player_response(watch_html: str) -> str:
    """Extract the ytInitialPlayerResponse json from the watch_html page.

    This mostly contains metadata necessary for rendering the page on-load,
    such as video information, copyright notices, etc.

    @param watch_html: Html of the watch page
    @return:
    """
    patterns = [
        r"window\[['\"]ytInitialPlayerResponse['\"]]\s*=\s*",
        r"ytInitialPlayerResponse\s*=\s*"
    ]
    for pattern in patterns:
        try:
            return parse_for_object(watch_html, pattern)
        except HTMLParseError:
            pass

    raise RegexMatchError(
        caller='initial_player_response',
        pattern='initial_player_response_pattern'
    )


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
