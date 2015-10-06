#!/usr/bin/env/python
# -*- coding: utf-8 -*-

import mock
from nose.tools import eq_
from pytube import api


class TestPytube(object):
    def setUp(self):
        url = 'http://www.youtube.com/watch?v=Ik-RsDGPI5Y'
        mock_js = open('tests/mock_video.js')
        mock_html = open('tests/mock_video.html')
        with mock.patch('pytube.api.urlopen') as urlopen:
            urlopen.return_value.read.return_value = mock_html.read()
            self.yt = api.YouTube()
            self.yt._js_code = mock_js.read()
            self.yt.from_url(url)

    def test_get_video_id(self):
        """Resolve the video id from url"""
        eq_(self.yt.video_id, 'Ik-RsDGPI5Y')
