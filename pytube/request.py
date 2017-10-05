# -*- coding: utf-8 -*-
"""
pytube.request
~~~~~~~~~~~~~~

Implements a simple wrapper around urlopen.
"""
from pytube.compat import urlopen


def get(url, headers=False, streaming=False, chunk_size=8 * 1024):
    """Sends an http GET request.

    :param str url:
        The URL to perform the GET request for.
    :param bool headers:
        Only return the http headers.
    :param bool streaming:
        Returns the response body in chunks via a generator.
    :param int chunk_size:
        The size in bytes of each chunk.
    """
    response = urlopen(url)
    if streaming:
        return stream_response(response, chunk_size)
    elif headers:
        return dict(response.info().items())
    return response.read().decode('utf-8')


def stream_response(response, chunk_size=8 * 1024):
    """Reads the :module:`urlopen` response in chunks."""
    while True:
        buf = response.read(chunk_size)
        if not buf:
            break
        yield buf
