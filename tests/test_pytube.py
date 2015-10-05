#!/usr/bin/env/python
# -*- coding: utf-8 -*-

from nose.tools import eq_, raises
from pytube import YouTube
from pytube.exceptions import MultipleObjectsReturned


class TestYouTube(object):
    """Test all methods of Youtube class"""

    def setUp(self):
        """Set up the all attributes required for a particular video."""

        self.url = "https://www.youtube.com/watch?v=Ik-RsDGPI5Y"
        self.video_id = 'Ik-RsDGPI5Y'
        self.filename = 'Pulp Fiction - Dancing Scene'
        self.yt = YouTube(self.url)
        # using flv since it has only once video
        self.flv = '<Video: Sorenson H.263 (.flv) - 240p - N/A>'

    def test_url(self):
        eq_(self.yt.url, self.url)

    def test_video_id(self):
        eq_(self.yt.video_id, self.video_id)

    def test_filename(self):
        eq_(self.yt.filename, self.filename)

    def test_get_videos(self):
        eq_(self.yt.get_videos())

    def test_get_video_data(self):
        eq_((self.yt.get_video_data()['args']['loaderUrl']), self.url)

    @raises(MultipleObjectsReturned)
    def test_get_false(self):
        self.yt.get()

    def test_get_true(self):
        eq_(str(self.yt.get('flv')), self.flv)

    def test_filter(self):
        eq_(str(self.yt.filter('flv')[0]), self.flv)
