#!/usr/bin/env python
# -*- coding: utf-8 -*-
# flake8: noqa
"""Python 2/3 compatibility support."""
import sys

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
PY33 = sys.version_info[0:2] >= (3, 3)


if PY2:
    from urllib import urlencode
    from urllib2 import URLError
    from urllib2 import quote
    from urllib2 import unquote
    from urllib2 import urlopen
    from urlparse import parse_qsl
    from HTMLParser import HTMLParser

    def unescape(s):
        """Strip HTML entries from a string."""
        html_parser = HTMLParser()
        return html_parser.unescape(s)

    def unicode(s):
        """Encode a string to utf-8."""
        return s.encode('utf-8')

elif PY3:
    from urllib.error import URLError
    from urllib.parse import parse_qsl
    from urllib.parse import quote
    from urllib.parse import unquote
    from urllib.parse import urlencode
    from urllib.request import urlopen

    def unicode(s):
        """No-op."""
        return s

    if PY33:
        from html.parser import HTMLParser

        def unescape(s):
            """Strip HTML entries from a string."""
            html_parser = HTMLParser()
            return html_parser.unescape(s)
    else:
        from html import unescape
