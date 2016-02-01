#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import warnings
import mock
from nose.tools import eq_, raises
from pytube import api
from pytube.exceptions import MultipleObjectsReturned, AgeRestricted, \
    DoesNotExist, PytubeError


class TestPytube(object):
    def setUp(self):
        url = 'http://www.youtube.com/watch?v=9bZkp7q19f0'

        with open('tests/mock_data/youtube_gangnam_style.html') as fh:
            self.mock_html = fh.read()

        with open('tests/mock_data/youtube_gangnam_style.js') as fh:
            self.mock_js = fh.read()

        with mock.patch('pytube.api.urlopen') as urlopen:
            urlopen.return_value.read.return_value = self.mock_html
            self.yt = api.YouTube()
            self.yt._js_cache = self.mock_js
            self.yt.from_url(url)

    def test_get_video_id(self):
        """Resolve the video id from url"""
        eq_(self.yt.video_id, '9bZkp7q19f0')

    def test_auto_filename(self):
        """Generate safe filename based on video title"""
        expected = 'PSY - GANGNAM STYLE(\uac15\ub0a8\uc2a4\ud0c0\uc77c) MV'

        eq_(self.yt.filename, expected)

    def test_manual_filename(self):
        """Manually set a filename"""
        expected = 'PSY - Gangnam Style'

        self.yt.set_filename(expected)
        eq_(self.yt.filename, expected)

    def test_get_all_videos(self):
        """Get all videos"""
        eq_(len(self.yt.get_videos()), 6)

    def test_filter_video_by_extension(self):
        """Filter videos by filetype"""
        eq_(len(self.yt.filter('mp4')), 2)
        eq_(len(self.yt.filter('3gp')), 2)
        eq_(len(self.yt.filter('webm')), 1)
        eq_(len(self.yt.filter('flv')), 1)

    def test_filter_video_by_extension_and_resolution(self):
        """Filter videos by file extension and resolution"""
        eq_(len(self.yt.filter('mp4', '720p')), 1)
        eq_(len(self.yt.filter('mp4', '1080p')), 0)

    def test_filter_video_by_extension_resolution_profile(self):
        """Filter videos by file extension, resolution, and profile"""
        eq_(len(self.yt.filter('mp4', '360p', 'Baseline')), 1)

    def test_filter_video_by_profile(self):
        """Filter videos by file profile"""
        eq_(len(self.yt.filter(profile='Simple')), 2)

    def test_filter_video_by_resolution(self):
        """Filter videos by resolution"""
        eq_(len(self.yt.filter(resolution='360p')), 2)

    @raises(MultipleObjectsReturned)
    def test_get_multiple_items(self):
        """get(...) cannot return more than one video"""
        self.yt.get(profile='Simple')
        self.yt.get('mp4')
        self.yt.get(resolution='240p')

    @raises(DoesNotExist)
    def test_get_does_not_exist(self):
        """get(...) must return something"""
        self.yt.get('mp4', '1080p')

    @raises(AgeRestricted)
    def test_age_restricted_video(self):
        """Raise exception on age restricted video"""
        url = 'http://www.youtube.com/watch?v=nzNgkc6t260'

        with open('tests/mock_data/youtube_age_restricted.html') as fh:
            mock_html = fh.read()

        with mock.patch('pytube.api.urlopen') as urlopen:
            urlopen.return_value.read.return_value = mock_html
            yt = api.YouTube()
            yt.from_url(url)

    def test_deprecation_warnings_on_url_set(self):
        """Deprecation warnings get triggered on url set"""
        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")
            with mock.patch('pytube.api.urlopen') as urlopen:
                urlopen.return_value.read.return_value = self.mock_html
                yt = api.YouTube()
                yt._js_cache = self.mock_js
                yt.url = 'http://www.youtube.com/watch?v=9bZkp7q19f0'
            eq_(len(w), 1)

    def test_deprecation_warnings_on_filename_set(self):
        """Deprecation warnings get triggered on filename set"""
        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")
            self.yt.filename = 'Gangnam Style'
            eq_(len(w), 1)

    def test_deprecation_warnings_on_videos_get(self):
        """Deprecation warnings get triggered on video getter"""
        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")
            self.yt.videos
            eq_(len(w), 1)

    def test_get_json_offset(self):
        """Find the offset in the html for where the js starts"""
        offset = self.yt._get_json_offset(self.mock_html)
        eq_(offset, 312)

    @raises(PytubeError)
    def test_get_json_offset_with_bad_html(self):
        """Raise exception if json offset cannot be found"""
        self.yt._get_json_offset('asdfasdf')

    def test_YT_create_from_url(self):
        'test creation of YouYube Object from url'
        url = 'http://www.youtube.com/watch?v=9bZkp7q19f0'

        yt = api.YouTube(url)
