# -*- coding: utf-8 -*-
# flake8: noqa: F401
# noreorder
"""
Pytube: a very serious Python library for downloading YouTube Videos.
"""
__title__ = "pytube3"
__author__ = "Nick Ficano, Harold Martin"
__license__ = "MIT License"
__copyright__ = "Copyright 2019 Nick Ficano"

from pytube.__main__ import YouTube
from pytube.captions import Caption
from pytube.contrib.playlist import Playlist
from pytube.query import CaptionQuery, StreamQuery
from pytube.streams import Stream
from pytube.version import __version__
