# -*- coding: utf-8 -*-
from pytube.exceptions import VideoUnavailable


def test_is_expected():
    try:
        raise VideoUnavailable("ppfff", video_id="YLnZklYFe7E")
    except VideoUnavailable as e:
        assert e.video_id == "YLnZklYFe7E"
