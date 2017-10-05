# -*- coding: utf-8 -*-
"""
tests.test_extract
~~~~~~~~~~~~~~~~~~

Unit tests for the :module:`extract <extract>` module.
"""
from pytube import extract


def test_extract_video_id():
    url = 'https://www.youtube.com/watch?v=9bZkp7q19f0'
    video_id = extract.video_id(url)
    assert video_id == '9bZkp7q19f0'


def test_extract_watch_url():
    video_id = '9bZkp7q19f0'
    watch_url = extract.watch_url(video_id)
    assert watch_url == 'https://www.youtube.com/watch?v=9bZkp7q19f0'
