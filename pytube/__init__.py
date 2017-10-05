# -*- coding: utf-8 -*-
# flake8: noqa
# noreorder
"""
pytube.__init__
~~~~~~~~~~~~~~~

A lightweight, dependency-free Python library (and command-line utility) for
downloading YouTube Videos. It's extensively documented and follows best
practice patterns.
"""
__title__ = 'pytube'
__version__ = '6.4.3'
__author__ = 'Nick Ficano'
__license__ = 'MIT License'
__copyright__ = 'Copyright 2017 Nick Ficano'

from pytube.query import StreamQuery
from pytube.streams import Stream
from pytube.__main__ import YouTube
