# -*- coding: utf-8 -*-
import pytest
from unittest import mock

from pytube import YouTube
from pytube.exceptions import LiveStreamError
from pytube.exceptions import RecordingUnavailable
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


def test_recording_unavailable():
    try:
        raise RecordingUnavailable(video_id="5YceQ8YqYMc")
    except RecordingUnavailable as e:
        assert e.video_id == "5YceQ8YqYMc"  # noqa: PT017
        assert str(e) == "5YceQ8YqYMc does not have a live stream recording available"


def test_private_error():
    try:
        raise VideoPrivate('mRe-514tGMg')
    except VideoPrivate as e:
        assert e.video_id == 'mRe-514tGMg'  # noqa: PT017
        assert str(e) == 'mRe-514tGMg is a private video'


def test_raises_video_private(private):
    with mock.patch('pytube.request.urlopen') as mock_url_open:
        # Mock the responses to YouTube
        mock_url_open_object = mock.Mock()
        mock_url_open_object.read.side_effect = [
            private['watch_html'].encode('utf-8'),
        ]
        mock_url_open.return_value = mock_url_open_object
        with pytest.raises(VideoPrivate):
            YouTube('https://youtube.com/watch?v=mRe-514tGMg')


def test_raises_recording_unavailable(missing_recording):
    with mock.patch('pytube.request.urlopen') as mock_url_open:
        # Mock the responses to YouTube
        mock_url_open_object = mock.Mock()
        mock_url_open_object.read.side_effect = [
            missing_recording['watch_html'].encode('utf-8'),
        ]
        mock_url_open.return_value = mock_url_open_object
        with pytest.raises(RecordingUnavailable):
            YouTube('https://youtube.com/watch?v=5YceQ8YqYMc')
