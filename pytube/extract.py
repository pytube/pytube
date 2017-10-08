# -*- coding: utf-8 -*-
"""
pytube.extract
~~~~~~~~~~~~~~

This module is responsible for all non-cipher related data extraction
(primarily used during data pre-fetching).
"""
import json
import re

from pytube.compat import quote
from pytube.compat import urlencode
from pytube.helpers import memoize


def video_id(url):
    """The ``video_id`` part of /watch?v=<video_id>.

    :param str url:
        A url YouTube id containing a video_id.

    """
    pattern = re.compile(r'.*(?:v=|/v/|^)(?P<id>[^&]*)')
    return pattern.search(url).group(1)


def watch_url(video_id):
    """Constructs a YouTube Watch url, given a video id.

    :param str video_id:
        A YouTube video identifer.

    """
    return 'https://youtube.com/watch?v=' + video_id


def video_info_url(video_id, watch_url, watch_html):
    """Contructs the video_info URL.

    :param str video_id:
        A YouTube video identifer.
    :param str watch_url:
        A YouTube watch url.
    :param str watch_html:
        The html contents of the watch page.

    """
    # I'm not entirely sure what ``t`` represents. Looks to represent a
    # boolean.
    t = re.compile('\W[\'"]?t[\'"]?: ?[\'"](.+?)[\'"]')
    params = urlencode({
        'video_id': video_id,
        'el': '$el',
        'ps': 'default',
        'eurl': quote(watch_url),
        'hl': 'en_US',
        't': quote(t.search(watch_html).group(0)),
    })
    return 'https://youtube.com/get_video_info?' + params


def js_url(watch_html):
    """Constructs the base JavaScript url, which contains the decipher
    transforms.

    :param str watch_html:
        The html contents of the watch page.

    """
    ytplayer_config = get_ytplayer_config(watch_html)
    base_js = ytplayer_config['assets']['js']
    return 'https://youtube.com' + base_js


@memoize
def get_ytplayer_config(watch_html):
    """The ``ytplayer_config`` is json data embedded within the watch html and
    serves as the primary source of obtaining the stream manifest data.

    :param str watch_html:
        The html contents of the watch page.

    """
    pattern = re.compile(r';ytplayer\.config\s*=\s*({.*?});')
    return json.loads(pattern.search(watch_html).group(1))
