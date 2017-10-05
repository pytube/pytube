# -*- coding: utf-8 -*-
"""
pytube.logging
~~~~~~~~~~~~~~

This module implements a log factory.
"""
import logging


def create_logger(level=logging.DEBUG):
    fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = logging.Formatter(fmt)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger
