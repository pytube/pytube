# -*- coding: utf-8 -*-
"""Reusable dependency injected testing components."""
from __future__ import unicode_literals

import gzip
import json
import os

import pytest

from pytube import YouTube


def load_from_playback_file(filename):
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    fp = os.path.join(cur_dir, 'mocks', filename)
    video = None
    with gzip.open(fp, 'rb') as fh:
        video = json.loads(fh.read().decode('utf-8'))
    yt = YouTube(
        url='https://www.youtube.com/watch?v=9bZkp7q19f0',
        defer_prefetch_init=True,
    )
    yt.watch_html = video['watch_html']
    yt.js = video['js']
    yt.vid_info = video['video_info']
    yt.init()
    return yt


@pytest.fixture
def gangnam_style():
    """Youtube instance initialized with video id 9bZkp7q19f0."""
    filename = 'yt-video-9bZkp7q19f0-1507588332.json.tar.gz'
    return load_from_playback_file(filename)


@pytest.fixture
def youtube_captions_and_subtitles():
    """Youtube instance initialized with video id QRS8MkLhQmM."""
    filename = 'yt-video-QRS8MkLhQmM-1507588031.json.tar.gz'
    return load_from_playback_file(filename)
