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
    filename = "yt-video-irauhITDrsE.json.gz"
    return load_playback_file(filename)


@pytest.fixture
def playlist_html():
    """Youtube playlist HTML loaded on 2020-01-25 from
    https://www.youtube.com/playlist?list=PLzMcBGfZo4-mP7qA9cagf68V06sko5otr"""
    file_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "mocks", "playlist.html.gz"
    )
    with gzip.open(file_path, "rb") as f:
        return f.read().decode("utf-8")


@pytest.fixture
def playlist_long_html():
    """Youtube playlist HTML loaded on 2020-01-25 from
    https://www.youtube.com/playlist?list=PLzMcBGfZo4-mP7qA9cagf68V06sko5otr"""
    file_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "mocks", "playlist_long.html.gz"
    )
    with gzip.open(file_path, "rb") as f:
        return f.read().decode("utf-8")
