#!/usr/bin/env/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import warnings
import mock
from nose.tools import eq_, raises
from pytube.contrib import batch
from pytube.exceptions import MultipleObjectsReturned, AgeRestricted, \
    DoesNotExist, PytubeError
import filecmp
import os, sys
   
class TestBatch(object):
    def __init__(self):
        self.url = 'http://www.youtube.com/watch?v=C0DPdy98e4c'
        self.video_id = "C0DPdy98e4c"
        self.path = 'tests/mock_data/'

    def test_batch_download(self):
        id_list = [self.video_id]
        url_list = [self.url]
        downloader_id = batch.Batch(path = self.path + 'video_id')
        downloader_url = batch.Batch(path = self.path + 'video_url')
        downloader_id.download_by_id_list(id_list)
        downloader_url.download_by_url_list(url_list)
        eq_(filecmp.cmp(self.path + 'video_id', self.path + 'video_url'), True);
        self.remove_file(self.path + 'video_id')
        self.remove_file(self.path + 'video_url')

    def test_batch_merge_video(self):
        id_list = [self.video_id, self.video_id]
        url_list = [self.url, self.url]
        downloader_id = batch.Batch(path = self.path + 'video_id')
        downloader_url = batch.Batch(path = self.path + 'video_url')
        downloader_id.merge_video_by_id_list(id_list)
        downloader_url.merge_video_by_url_list(url_list)
        eq_(filecmp.cmp(self.path + 'video_id', self.path + 'video_url'), True);
        self.remove_file(self.path + 'video_id')
        self.remove_file(self.path + 'video_url')

    def remove_file(self, filename):
    	path = os.path.normpath(filename)
    	os.remove(path)