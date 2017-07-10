#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pytube import utils


blob = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit'


def test_truncate():
    """Truncate string works as expected"""
    truncated = utils.truncate(blob, 11)
    assert truncated == 'Lorem ipsum'


def test_safe_filename():
    """Unsafe characters get stripped from generated filename"""
    assert utils.safe_filename('abc1245$$') == 'abc1245'
    assert utils.safe_filename('abc##') == 'abc'
    assert utils.safe_filename('abc:foo') == 'abc -foo'
    assert utils.safe_filename('abc_foo') == 'abc foo'


def test_sizeof():
    """Accurately converts the bytes to its humanized equivalent"""
    assert utils.sizeof(1) == '1 byte'
    assert utils.sizeof(2) == '2 bytes'
    assert utils.sizeof(2400) == '2 KB'
    assert utils.sizeof(2400000) == '2 MB'
    assert utils.sizeof(2400000000) == '2 GB'
    assert utils.sizeof(2400000000000) == '2 TB'
    assert utils.sizeof(2400000000000000) == '2 PB'
