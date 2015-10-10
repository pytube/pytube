#!/usr/bin/env python
# -*- coding: utf-8 -*-
# flake8: noqa
try:
    from urllib2 import urlopen
    from urlparse import urlparse, parse_qs, unquote
except ImportError:
    from urllib.parse import urlparse, parse_qs, unquote
    from urllib.request import urlopen
