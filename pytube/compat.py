#!/usr/bin/env python
# -*- coding: utf-8 -*-
# flake8: noqa
"""Python 2/3 compatibility support."""
import sys


PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
PY33 = sys.version_info[0:2] >= (3, 3)

if PY2:
    reload(sys)
    sys.setdefaultencoding("utf8")
    import urllib2
    from urllib2 import URLError
    from urllib2 import quote
    from urllib2 import unquote
    from urllib2 import urlopen
    from urlparse import parse_qsl
    from HTMLParser import HTMLParser

    def install_proxy(proxy_handler):
        """
        install global proxy.
        :param proxy_handler:
            :samp:`{"http":"http://my.proxy.com:1234", "https":"https://my.proxy.com:1234"}`
        :return:
        """
        proxy_support = urllib2.ProxyHandler(proxy_handler)
        opener = urllib2.build_opener(proxy_support)
        urllib2.install_opener(opener)

    def unescape(s):
        """Strip HTML entries from a string."""
        html_parser = HTMLParser()
        return html_parser.unescape(s)

    def unicode(s):
        """Encode a string to utf-8."""
        return s.encode("utf-8")


elif PY3:
    from urllib import request

    def install_proxy(proxy_handler):
        proxy_support = request.ProxyHandler(proxy_handler)
        opener = request.build_opener(proxy_support)
        request.install_opener(opener)

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
        pass
