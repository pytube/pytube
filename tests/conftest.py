# -*- coding: utf-8 -*-
"""Reusable dependency injected testing components."""
import json
import os

import pytest

from pytube import YouTube


@pytest.fixture
def gangnam_style():
    """Youtube instance initialized with video id 9bZkp7q19f0."""
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    fp = os.path.join(cur_dir, 'mocks', 'yt-video-9bZkp7q19f0.json')
    video = None
    with open(fp, 'r') as fh:
        video = json.loads(fh.read())
    yt = YouTube(
        url='https://www.youtube.com/watch?v=9bZkp7q19f0',
        defer_prefetch_init=True,
    )
    yt.watch_html = video['watch_html']
    yt.js = video['js']
    yt.vid_info = video['video_info']
    yt.init()
    return yt
