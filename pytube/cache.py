# -*- coding: utf-8 -*-
"""Minimize requests for base.js when looking to the same URL"""
from functools import lru_cache

from pytube import request

@lru_cache(maxsize=None)
def get_js(js_url):
    """Retrieve Javascript from js_url if Javascript is not already cached.

    :param str js_url:
        A YouTube url for the base.js asset file.
    :rtype: str
    :returns:
        The contents of the base.js asset file.
    """
    return request.get(js_url)
