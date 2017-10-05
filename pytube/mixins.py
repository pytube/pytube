# -*- coding: utf-8 -*-
"""
pytube.mixins
~~~~~~~~~~~~~

"""
import logging

from pytube import cipher
from pytube.compat import parse_qsl
from pytube.compat import unquote


logger = logging.getLogger(__name__)


def apply_signature(video_info, fmt, js):
    stream_map = video_info[fmt]
    for i, stream in enumerate(stream_map):
        url = stream['url']
        if 'signature=' in url:
            continue
        signature = cipher.get_signature(js, stream['s'])
        logger.debug(
            'descrambling url signature %s ', stream['s'], extra={
                's': stream['s'],
                'signature': signature,
                'itag': stream['itag'],
            },
        )
        stream_map[i]['url'] = url + '&signature=' + signature


def apply_fmt_decoder(video_info, fmt):
    video_info[fmt] = [
        {k: unquote(v) for k, v in parse_qsl(i)} for i
        in video_info[fmt].split(',')
    ]
