#!/usr/bin/env/python
# -*- coding: utf-8 -*-

import unittest
from pytube import YouTube
from pytube.exceptions import MultipleObjectsReturned

SHOW_ERROR_MESSAGES = True


class TestYouTube(unittest.TestCase):
    """Test all methods of Youtube class"""

    def setUp(self):
        """Set up the all attributes required for a particular video."""

        self.url = "https://www.youtube.com/watch?v=Ik-RsDGPI5Y"
        self.video_id = 'Ik-RsDGPI5Y'
        self.filename = 'Pulp Fiction - Dancing Scene'
        self.yt = YouTube(self.url)
        #: don't hard code, make is universal
        self.videos = ['<Video: MPEG-4 Visual (.3gp) - 144p - Simple>',
                    '<Video: MPEG-4 Visual (.3gp) - 240p - Simple>',
                   '<Video: Sorenson H.263 (.flv) - 240p - N/A>',
                   '<Video: H.264 (.mp4) - 360p - Baseline>',
                   '<Video: H.264 (.mp4) - 720p - High>',
                   '<Video: VP8 (.webm) - 360p - N/A>']
        # using flv since it has only once video
        self.flv = '<Video: Sorenson H.263 (.flv) - 240p - N/A>'

    def test_url(self):
        self.assertEqual(self.yt.url, self.url)

    def test_video_id(self):
        self.assertEqual(self.yt.video_id, self.video_id)

    def test_filename(self):
        self.assertEqual(self.yt.filename, self.filename)

    def test_get_videos(self):
        self.assertEqual(map(str, self.yt.get_videos()), self.videos)

    def test_get_video_data(self):
        self.assertEqual((self.yt.get_video_data()['args']['loaderUrl']),
                         self.url)

    def test_get_false(self):
        with self.assertRaises(MultipleObjectsReturned):
                self.yt.get()

    def test_get_true(self):
        self.assertEqual(str(self.yt.get('flv')), self.flv)

    def test_filter(self):
        self.assertEqual(str(self.yt.filter('flv')[0]), self.flv)

if __name__ == '__main__':
    unittest.main()
