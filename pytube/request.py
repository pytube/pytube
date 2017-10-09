# -*- coding: utf-8 -*-
"""Implements a simple wrapper around urlopen."""
import multiprocessing

from pytube.compat import urlopen


def get(
    url=None, urls=[], processes=2, headers=False,
    streaming=False, chunk_size=8 * 1024,
):
    """Send an http GET request.

    :param str url:
        The URL to perform the GET request for.
    :param list urls:
        List of URLs to perform the GET request for concurrently.
    :param int processes:
        How many worker processes to start.
    :param bool headers:
        Only return the http headers.
    :param bool streaming:
        Returns the response body in chunks via a generator.
    :param int chunk_size:
        The size in bytes of each chunk.
    """
    if urls:
        pool = multiprocessing.Pool(processes=processes)
        return pool.map(get, urls)
    else:
        response = urlopen(url)
        if streaming:
            return stream_response(response, chunk_size)
        elif headers:
            return dict(response.info().items())
        return (
            response
            .read()
            .decode('utf-8')
        )


def stream_response(response, chunk_size=8 * 1024):
    """Read the response in chunks."""
    while True:
        buf = response.read(chunk_size)
        if not buf:
            break
        yield buf
