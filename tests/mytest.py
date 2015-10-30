#!/usr/bin/env/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from nose.tools import eq_
from test_utils import TestUtils

test = TestUtils()
test.test_truncate()
test.test_safe_filename()
test.test_sizeof()