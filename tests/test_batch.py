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
import os
   
class TestBatch(object):
	def __init__(self):
		self.url = 'http://www.youtube.com/watch?v=C0DPdy98e4c'
		self.video_id = "C0DPdy98e4c"
		self.batch_download_file = './mock_data/test_output'
		self.test_file = './mock_data/youtube_test_video.mp4'
		self.merge_file = './mock_data/youtube_test_video_double'
		self.downloader = batch.Batch(path = self.batch_download_file)

	def test_batch_download_by_id_list(self):
		id_list = [self.video_id]
		self.downloader.download_by_id_list(id_list)
		eq_(filecmp.cmp(self.test_file, self.batch_download_file), True);
		path = os.path.normpath(self.batch_download_file)
		try:
			os.remove(path)
		except OSError as e:
			print("Failed with:{0}".format(e.strerror))
			print("Error code:{0}".format(e.code))

	def test_batch_download_by_url_list(self):
		url_list = [self.url]
		self.downloader.download_by_url_list(url_list)
		eq_(filecmp.cmp(self.test_file, self.batch_download_file), True);
		path = os.path.normpath(self.batch_download_file)
		try:
			os.remove(path)
		except OSError as e:
			print("Failed with:{0}".format(e.strerror))
			print("Error code:{0}".format(e.code))

	def test_batch_merge_video_by_url_list(self):
		url_list = [self.url, self.url]
		self.downloader.merge_video_by_url_list(url_list)
		eq_(filecmp.cmp(self.merge_file, self.batch_download_file), True);
		path = os.path.normpath(self.batch_download_file)
		try:
			os.remove(path)
		except OSError as e:
			print("Failed with:{0}".format(e.strerror))
			print("Error code:{0}".format(e.code))

	def test_batch_merge_video_by_id_list(self):
		id_list = [self.video_id, self.video_id]
		self.downloader.merge_video_by_id_list(id_list)
		eq_(filecmp.cmp(self.merge_file, self.batch_download_file), True);
		path = os.path.normpath(self.batch_download_file)
		try:
			os.remove(path)
		except OSError as e:
			print("Failed with:{0}".format(e.strerror))
			print("Error code:{0}".format(e.code))
