# -*- coding: utf-8 -*-
"""
pytube.download
~~~~~~~~~~~~~~~

"""
from urllib.request import urlopen

import requests


def get(url):
    response = requests.get(url)
    return response.text


def headers(url):
    response = urlopen(url)
    return dict(response.info().items())


def stream(url, chunk_size=8 * 1024):
    response = urlopen(url)
    while True:
        buf = response.read(chunk_size)
        if not buf:
            break
        yield buf
