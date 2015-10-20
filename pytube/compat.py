#!/usr/bin/env python
# -*- coding: utf-8 -*-
# flake8: noqa
import sys

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

if PY2:
    from urllib2 import urlopen
    from urlparse import urlparse, parse_qs, unquote
if PY3:
    from urllib.parse import urlparse, parse_qs, unquote
    from urllib.request import urlopen
