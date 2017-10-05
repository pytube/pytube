# -*- coding: utf-8 -*-
"""
pytube.logging
~~~~~~~~~~~~~~

This module implements a log factory.
"""
from __future__ import absolute_import

import logging


def create_logger(level=logging.DEBUG):
    fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(fmt)

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger
