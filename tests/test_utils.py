#!/usr/bin/env/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from nose.tools import eq_
from pytube import utils


class TestUtils(object):
    blob = "Lorem ipsum dolor sit amet, consectetur adipiscing elit"

    def test_truncate(self):
        """Truncate string works as expected"""
        truncated = utils.truncate(self.blob, 11)
        eq_(truncated, 'Lorem ipsum')

    def test_safe_filename(self):
        """Unsafe characters get stripped from generated filename"""
        eq_(utils.safe_filename("abc1245$$"), "abc1245")
        eq_(utils.safe_filename("abc##"), "abc")
        eq_(utils.safe_filename("abc:foo"), "abc -foo")
        eq_(utils.safe_filename("abc_foo"), "abc foo")
