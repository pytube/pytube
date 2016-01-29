#!/usr/bin/env python3
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
        self.url = 'http://www.youtube.com/watch?v=9bZkp7q19f0'

    def test_YT_create_from_url(self):
        'test creation of YouYube Object from url'
        yt = api.YouTube(self.url)
