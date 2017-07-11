#!/usr/bin/env python
# -*- coding: utf-8 -*-
# flake8: noqa
__title__ = 'pytube'
__version__ = '6.4.2'
__author__ = 'Nick Ficano'
__license__ = 'MIT License'
__copyright__ = 'Copyright 2017 Nick Ficano'

from .api import YouTube

# Set default logging handler to avoid "No handler found" warnings.
import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())
