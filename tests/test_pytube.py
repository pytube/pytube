#!/usr/bin/env python
# -*- coding: utf-8 -*-
import warnings

import mock
import pytest

from pytube import api
from pytube.exceptions import AgeRestricted
from pytube.exceptions import MultipleObjectsReturned
from pytube.exceptions import PytubeError


def test_video_id(yt_video):
    """Resolve the video id from url"""
    assert yt_video.video_id == '9bZkp7q19f0'


def test_auto_filename(yt_video):
    """Generate safe filename based on video title"""
    expected = u'PSY - GANGNAM STYLE(강남스타일) MV'
    assert yt_video.filename == expected


def test_manual_filename(yt_video):
    """Manually set a filename"""
    expected = 'PSY - Gangnam Style'
    yt_video.set_filename(expected)
    assert yt_video.filename == expected


def test_get_all_videos(yt_video):
    """Get all videos"""
    assert len(yt_video.get_videos()) == 6


def test_filter_video_by_extension(yt_video):
    """Filter videos by filetype"""
    assert len(yt_video.filter('mp4')) == 2
    assert len(yt_video.filter('3gp')) == 2
    assert len(yt_video.filter('webm')) == 1
    assert len(yt_video.filter('flv')) == 1


def test_filter_video_by_extension_and_resolution(yt_video):
    """Filter videos by file extension and resolution"""
    assert len(yt_video.filter('mp4', '720p')) == 1
    assert len(yt_video.filter('mp4', '1080p')) == 0


def test_filter_video_by_extension_resolution_profile(yt_video):
    """Filter videos by file extension, resolution, and profile"""
    assert len(yt_video.filter('mp4', '360p', 'Baseline')) == 1


def test_filter_video_by_profile(yt_video):
    """Filter videos by file profile"""
    assert len(yt_video.filter(profile='Simple')) == 2


def test_filter_video_by_resolution(yt_video):
    """Filter videos by resolution"""
    assert len(yt_video.filter(resolution='360p')) == 2


def test_get_multiple_items(yt_video):
    """get(...) cannot return more than one video"""
    with pytest.raises(MultipleObjectsReturned):
        yt_video.get(profile='Simple')
        yt_video.get('mp4')
        yt_video.get(resolution='240p')


def test_age_restricted_video():
    """Raise exception on age restricted video"""
    mock_html = None

    with open('tests/mock_data/youtube_age_restricted.html') as fh:
        mock_html = fh.read()

    with mock.patch('pytube.api.urlopen') as urlopen:
        urlopen.return_value.read.return_value = mock_html
        yt = api.YouTube()

        with pytest.raises(AgeRestricted):
            yt.from_url('http://www.youtube.com/watch?v=nzNgkc6t260')


def test_deprecation_warnings_on_url_set(yt_video):
    """Deprecation warnings get triggered on url set"""
    with warnings.catch_warnings(record=True) as w:
        # Cause all warnings to always be triggered.
        warnings.simplefilter('always')
        yt_video.url = 'http://www.youtube.com/watch?v=9bZkp7q19f0'
        assert len(w) == 1


def test_deprecation_warnings_on_filename_set(yt_video):
    """Deprecation warnings get triggered on filename set"""
    with warnings.catch_warnings(record=True) as w:
        # Cause all warnings to always be triggered.
        warnings.simplefilter('always')
        yt_video.filename = 'Gangnam Style'
        assert len(w) == 1


def test_deprecation_warnings_on_videos_get(yt_video):
    """Deprecation warnings get triggered on video getter"""
    with warnings.catch_warnings(record=True) as w:
        # Cause all warnings to always be triggered.
        warnings.simplefilter('always')
        yt_video.videos
        assert len(w) == 1


def test_get_json_offset(yt_video):
    """Find the offset in the html for where the js starts"""
    mock_html = None

    with open('tests/mock_data/youtube_gangnam_style.html') as fh:
        mock_html = fh.read()

    offset = yt_video._get_json_offset(mock_html)
    assert offset == 312


def test_get_json_offset_with_bad_html(yt_video):
    """Raise exception if json offset cannot be found"""
    with pytest.raises(PytubeError):
        yt_video._get_json_offset('asdfasdf')
