# -*- coding: utf-8 -*-
"""This module contains all non-cipher related data extraction logic."""
import json
from collections import OrderedDict

from pytube.compat import quote
from pytube.compat import urlencode
from pytube.exceptions import RegexMatchError
from pytube.helpers import regex_search


def is_age_restricted(watch_html):
    """Check if content is age restricted.

    :param str watch_html:
        The html contents of the watch page.
    :rtype: bool
    :returns:
        Whether or not the content is age restricted.
    """
    try:
        regex_search(r'og:restrictions:age', watch_html, group=0)
    except RegexMatchError:
        return False
    return True


def video_id(url):
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
    return regex_search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url, group=1)


def watch_url(video_id):
    """Construct a sanitized YouTube watch url, given a video id.

    :param str video_id:
        A YouTube video identifier.
    :rtype: str
    :returns:
        Sanitized YouTube watch url.
    """
    return 'https://youtube.com/watch?v=' + video_id


def embed_url(video_id):
    return 'https://www.youtube.com/embed/{}'.format(video_id)


def eurl(video_id):
    return 'https://youtube.googleapis.com/v/{}'.format(video_id)


def video_info_url(
    video_id, watch_url, watch_html, embed_html,
    age_restricted,
):
    """Construct the video_info url.

    :param str video_id:
        A YouTube video identifier.
    :param str watch_url:
        A YouTube watch url.
    :param str watch_html:
        The html contents of the watch page.
    :param str embed_html:
        The html contents of the embed page (for age restricted videos).
    :param bool age_restricted:
        Is video age restricted.
    :rtype: str
    :returns:
        :samp:`https://youtube.com/get_video_info` with necessary GET
        parameters.
    """
    if age_restricted:
        sts = regex_search(r'"sts"\s*:\s*(\d+)', embed_html, group=1)
        # Here we use ``OrderedDict`` so that the output is consistent between
        # Python 2.7+.
        params = OrderedDict([
            ('video_id', video_id),
            ('eurl', eurl(video_id)),
            ('sts', sts),
        ])
    else:
        # I'm not entirely sure what ``t`` represents. Looks to represent a
        # boolean.
        t = regex_search(
            r'\W[\'"]?t[\'"]?: ?[\'"](.+?)[\'"]', watch_html,
            group=0,
        )
        params = OrderedDict([
            ('video_id', video_id),
            ('el', '$el'),
            ('ps', 'default'),
            ('eurl', quote(watch_url)),
            ('hl', 'en_US'),
            ('t', quote(t)),
        ])
    return 'https://youtube.com/get_video_info?' + urlencode(params)


def js_url(html, age_restricted=False):
    """Get the base JavaScript url.

    Construct the base JavaScript url, which contains the decipher
    "transforms".

    :param str watch_html:
        The html contents of the watch page.
    :param bool age_restricted:
        Is video age restricted.

    """
    ytplayer_config = get_ytplayer_config(html, age_restricted)
    base_js = ytplayer_config['assets']['js']
    return 'https://youtube.com' + base_js


def mime_type_codec(mime_type_codec):
    """Parse the type data.

    Breaks up the data in the ``type`` key of the manifest, which contains the
    mime type and codecs serialized together, and splits them into separate
    elements.

    **Example**:

    >>> mime_type_codec('audio/webm; codecs="opus"')
    ('audio/webm', ['opus'])

    :param str mime_type_codec:
        String containing mime type and codecs.
    :rtype: tuple
    :returns:
        The mime type and a list of codecs.

    """
    pattern = r'(\w+\/\w+)\;\scodecs=\"([a-zA-Z-0-9.,\s]*)\"'
    mime_type, codecs = regex_search(pattern, mime_type_codec, groups=True)
    return mime_type, [c.strip() for c in codecs.split(',')]


def get_ytplayer_config(html, age_restricted=False):
    """Get the YouTube player configuration data from the watch html.

    Extract the ``ytplayer_config``, which is json data embedded within the
    watch html and serves as the primary source of obtaining the stream
    manifest data.

    :param str watch_html:
        The html contents of the watch page.
    :param bool age_restricted:
        Is video age restricted.
    :rtype: str
    :returns:
        Substring of the html containing the encoded manifest data.
    """
    if age_restricted:
        pattern = r";yt\.setConfig\(\{'PLAYER_CONFIG':\s*({.*})(,'EXPERIMENT_FLAGS'|;)"  # noqa: E501
    else:
        pattern = r';ytplayer\.config\s*=\s*({.*?});'
    yt_player_config = regex_search(pattern, html, group=1)
    return json.loads(yt_player_config)
