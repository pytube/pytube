#!/usr/bin/env python
# -*- coding: utf-8 -*-
# flake8: noqa
"""Python 2/3 compatibility support."""
import sys

python_version = sys.version_info[0]

if python_version == 2:
    from urllib import urlencode
    from urllib2 import URLError
    from urllib2 import quote
    from urllib2 import unquote
    from urllib2 import urlopen
    from urlparse import parse_qsl

elif python_version == 3:
    from urllib.error import URLError
    from urllib.parse import parse_qsl
    from urllib.parse import quote
    from urllib.parse import unquote
    from urllib.parse import urlencode
    from urllib.request import urlopen
