# -*- coding: utf-8 -*-
"""Unit tests for the :module:`extract <extract>` module."""
from pytube import extract


def test_extract_video_id():
    url = 'https://www.youtube.com/watch?v=9bZkp7q19f0'
    video_id = extract.video_id(url)
    assert video_id == '9bZkp7q19f0'


def test_extract_watch_url():
    video_id = '9bZkp7q19f0'
    watch_url = extract.watch_url(video_id)
    assert watch_url == 'https://youtube.com/watch?v=9bZkp7q19f0'


def test_info_url(gangnam_style):
    video_info_url = extract.video_info_url(
        video_id=gangnam_style.video_id,
        watch_url=gangnam_style.watch_url,
        watch_html=gangnam_style.watch_html,
    )
    expected = (
        'https://youtube.com/get_video_info?video_id=9bZkp7q19f0&el=%24el'
        '&ps=default&eurl=https%253A%2F%2Fyoutube.com%2Fwatch%253Fv%'
        '253D9bZkp7q19f0&hl=en_US&t=%252C%2522t%2522%253A%25221%2522'
    )
    assert video_info_url == expected


def test_js_url(gangnam_style):
    expected = 'https://youtube.com/yts/jsbin/player-vflOdyxa4/en_US/base.js'
    result = extract.js_url(gangnam_style.watch_html)
    assert expected == result
