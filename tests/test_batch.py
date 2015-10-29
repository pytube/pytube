#!/usr/bin/env/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import warnings
import mock
from nose.tools import eq_, raises
from pytube import batch
from pytube.exceptions import MultipleObjectsReturned, AgeRestricted, \
    DoesNotExist, PytubeError
import filecmp


class TestPytube(object):
	def setUp(self):
		url = 'http://www.youtube.com/watch?v=C0DPdy98e4c'
		video_id = 'C0DPdy98e4c'
		batch_download_file = 'tests/mock_data/test_output'
		downloader = batch.Batch(batch_download_file)

	def test_batch_download_by_url_list(self):
		url_list = [url]
		downloader.download_by_url_list(url_list)
		eq_(filecmp.com('tests/mock_data/youtube_test_video.mp4', 'tests/mock_data/test_output'), True);
		path = os.path.normpath(batch_download_file)
		os.remove(path)

	def test_batch_download_by_id_list(self):
		id_list = [video_id]
		downloader.download_by_id_list(id_list)
		eq_(filecmp.com('tests/mock_data/youtube_test_video.mp4', 'tests/mock_data/test_output'), True);
		path = os.path.normpath(batch_download_file)
		os.remove(path)

	def test_batch_merge_video_by_url_list(self):
		url_list = [url, url]
		downloader.merge_video_by_url_list(url_list)
		eq_(filecmp.com('tests/mock_data/youtube_test_video_double', 'tests/mock_data/test_output'), True);
		path = os.path.normpath(batch_download_file)
		os.remove(path)

	def test_batch_merge_video_by_id_list(self):
		id_list = [video_id, video_id]
		downloader.download_by_id_list(id_list)
		eq_(filecmp.com('tests/mock_data/youtube_test_video_double', 'tests/mock_data/test_output'), True);
		path = os.path.normpath(batch_download_file)
		os.remove(path)
