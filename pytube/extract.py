# -*- coding: utf-8 -*-
"""
pytube.extract
~~~~~~~~~~~~~~

"""
import json
import re

from pytube.compat import parse_qsl
from pytube.compat import quote
from pytube.compat import urlencode
from pytube.helpers import memoize


def video_id(url):
    pattern = re.compile(r'.*(?:v=|/v/|^)(?P<id>[^&]*)')
    return pattern.search(url).group(1)


def watch_url(video_id):
    return (
        'https://www.youtube.com/watch?v={video_id}'
        .format(video_id=video_id)
    )


def video_info_url(video_id, watch_url, watch_html):
    # TODO(nficano): not sure what t represents.
    t = re.compile('\W[\'"]?t[\'"]?: ?[\'"](.+?)[\'"]')
    params = urlencode({
        'video_id': video_id,
        'el': '$el',
        'ps': 'default',
        'eurl': quote(watch_url),
        'hl': 'en_US',
        't': quote(t.search(watch_html).group(0)),
    })
    return (
        'https://www.youtube.com/get_video_info?{params}'
        .format(params=params)
    )


def js_url(watch_html):
    ytplayer_config = get_ytplayer_config(watch_html)
    base_js = ytplayer_config['assets']['js']
    return 'https://youtube.com{base_js}'.format(base_js=base_js)


@memoize
def get_ytplayer_config(watch_html):
    pattern = re.compile(r';ytplayer\.config\s*=\s*({.*?});')
    return json.loads(pattern.search(watch_html).group(1))


def decode_video_info(video_info):
    return {k: v for k, v in parse_qsl(video_info)}
