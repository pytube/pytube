# -*- coding: utf-8 -*-
"""Reusable dependency injected testing components."""

import gzip
import json
import os

import pytest

from pytube import YouTube


def load_playback_file(filename):
    """Load a gzip json playback file."""
    cur_fp = os.path.realpath(__file__)
    cur_dir = os.path.dirname(cur_fp)
    fp = os.path.join(cur_dir, "mocks", filename)
    with gzip.open(fp, "rb") as fh:
        content = fh.read().decode("utf-8")
        return json.loads(content)


def load_and_init_from_playback_file(filename):
    """Load a gzip json playback file and create YouTube instance."""
    pb = load_playback_file(filename)
    yt = YouTube(pb["url"], defer_prefetch_init=True)
    yt.watch_html = pb["watch_html"]
    yt.js = pb["js"]
    yt.vid_info = pb["video_info"]
    yt.descramble()
    return yt


@pytest.fixture
def cipher_signature():
    """Youtube instance initialized with video id 9bZkp7q19f0."""
    filename = "yt-video-9bZkp7q19f0.json.gz"
    return load_and_init_from_playback_file(filename)


@pytest.fixture
def presigned_video():
    """Youtube instance initialized with video id QRS8MkLhQmM."""
    filename = "yt-video-QRS8MkLhQmM.json.gz"
    return load_and_init_from_playback_file(filename)


@pytest.fixture
def age_restricted():
    """Youtube instance initialized with video id zRbsm3e2ltw."""
    filename = "yt-video-zRbsm3e2ltw-1507777044.json.gz"
    return load_playback_file(filename)
