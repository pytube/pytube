# -*- coding: utf-8 -*-
from unittest import mock

from pytube import YouTube


@mock.patch("pytube.__main__.YouTube")
def test_prefetch_deferred(MockYouTube):
    instance = MockYouTube.return_value
    instance.prefetch_descramble.return_value = None
    YouTube("https://www.youtube.com/watch?v=9bZkp7q19f0", True)
    assert not instance.prefetch_descramble.called
