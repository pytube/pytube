# -*- coding: utf-8 -*-
# flake8: noqa
# noreorder
"""
Pytube: a very serious Python library for downloading YouTube Videos.
"""
__title__ = 'pytube'
__version__ = '9.3.3'
__author__ = 'Nick Ficano'
__license__ = 'MIT License'
__copyright__ = 'Copyright 2018 Nick Ficano'

from pytube.logging import create_logger
from pytube.query import CaptionQuery
from pytube.query import StreamQuery
from pytube.streams import Stream
from pytube.captions import Caption
from pytube.contrib.playlist import Playlist
from pytube.__main__ import YouTube

logger = create_logger()
logger.info('%s v%s', __title__, __version__)
