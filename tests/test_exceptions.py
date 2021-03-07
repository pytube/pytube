# -*- coding: utf-8 -*-
import pytest
from unittest import mock

from pytube import YouTube
from pytube.exceptions import LiveStreamError
from pytube.exceptions import RecordingUnavailable
from pytube.exceptions import RegexMatchError
from pytube.exceptions import VideoUnavailable
from pytube.exceptions import VideoPrivate
from pytube.exceptions import VideoRegionBlocked


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
    # Ensure this can be caught as generic VideoUnavailable exception
    with pytest.raises(VideoUnavailable):
        raise LiveStreamError(video_id='YLnZklYFe7E')
    try:
        raise LiveStreamError(video_id='YLnZklYFe7E')
    except LiveStreamError as e:
        assert e.video_id == 'YLnZklYFe7E'  # noqa: PT017
        assert str(e) == 'YLnZklYFe7E is streaming live and cannot be loaded'


def test_recording_unavailable_error():
    # Ensure this can be caught as generic VideoUnavailable exception
    with pytest.raises(VideoUnavailable):
        raise RecordingUnavailable(video_id='5YceQ8YqYMc')
    try:
        raise RecordingUnavailable(video_id='5YceQ8YqYMc')
    except RecordingUnavailable as e:
        assert e.video_id == '5YceQ8YqYMc'  # noqa: PT017
        assert str(e) == '5YceQ8YqYMc does not have a live stream recording available'


def test_private_error():
    # Ensure this can be caught as generic VideoUnavailable exception
    with pytest.raises(VideoUnavailable):
        raise VideoPrivate('m8uHb5jIGN8')
    try:
        raise VideoPrivate('m8uHb5jIGN8')
    except VideoPrivate as e:
        assert e.video_id == 'm8uHb5jIGN8'  # noqa: PT017
        assert str(e) == 'm8uHb5jIGN8 is a private video'


def test_region_locked_error():
    # Ensure this can be caught as generic VideoUnavailable exception
    with pytest.raises(VideoUnavailable):
        raise VideoRegionBlocked('hZpzr8TbF08')
    try:
        raise VideoRegionBlocked('hZpzr8TbF08')
    except VideoRegionBlocked as e:
        assert e.video_id == 'hZpzr8TbF08'  # noqa: PT017
        assert str(e) == 'hZpzr8TbF08 is not available in your region'


def test_raises_video_private(private):
    with mock.patch('pytube.request.urlopen') as mock_url_open:
        # Mock the responses to YouTube
        mock_url_open_object = mock.Mock()
        mock_url_open_object.read.side_effect = [
            private['watch_html'].encode('utf-8'),
        ]
        mock_url_open.return_value = mock_url_open_object
        with pytest.raises(VideoPrivate):
            YouTube('https://youtube.com/watch?v=m8uHb5jIGN8').streams


def test_raises_recording_unavailable(missing_recording):
    with mock.patch('pytube.request.urlopen') as mock_url_open:
        # Mock the responses to YouTube
        mock_url_open_object = mock.Mock()
        mock_url_open_object.read.side_effect = [
            missing_recording['watch_html'].encode('utf-8'),
        ]
        mock_url_open.return_value = mock_url_open_object
        with pytest.raises(RecordingUnavailable):
            YouTube('https://youtube.com/watch?v=5YceQ8YqYMc').streams


def test_raises_video_region_blocked(region_blocked):
    with mock.patch('pytube.request.urlopen') as mock_url_open:
        # Mock the responses to YouTube
        mock_url_open_object = mock.Mock()
        mock_url_open_object.read.side_effect = [
            region_blocked['watch_html'].encode('utf-8')
        ]
        mock_url_open.return_value = mock_url_open_object
        with pytest.raises(VideoRegionBlocked):
            YouTube('https://youtube.com/watch?v=hZpzr8TbF08').streams
