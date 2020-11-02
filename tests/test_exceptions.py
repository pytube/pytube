# -*- coding: utf-8 -*-
from pytube.exceptions import LiveStreamError
from pytube.exceptions import RegexMatchError
from pytube.exceptions import VideoUnavailable
from pytube.exceptions import VideoPrivate


def test_video_unavailable():
    try:
        raise VideoUnavailable(video_id="YLnZklYFe7E")
    except VideoUnavailable as e:
        assert e.video_id == "YLnZklYFe7E"  # noqa: PT017
        assert str(e) == "YLnZklYFe7E is unavailable"


def test_regex_match_error():
    try:
        raise RegexMatchError(caller="hello", pattern="*")
    except RegexMatchError as e:
        assert str(e) == "hello: could not find match for *"


def test_live_stream_error():
    try:
        raise LiveStreamError(video_id="YLnZklYFe7E")
    except LiveStreamError as e:
        assert e.video_id == "YLnZklYFe7E"  # noqa: PT017
        assert str(e) == "YLnZklYFe7E is streaming live and cannot be loaded"


def test_private_error():
    try:
        raise VideoPrivate('mRe-514tGMg')
    except VideoPrivate as e:
        assert e.video_id == 'mRe-514tGMg'
        assert str(e) == 'mRe-514tGMg is a private video'
