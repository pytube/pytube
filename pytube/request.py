# -*- coding: utf-8 -*-
"""Implements a simple wrapper around urlopen."""
from typing import Any, Iterable, Dict
from urllib.request import Request
from urllib.request import urlopen


def _execute_request(url: str) -> Any:
    if not url.lower().startswith("http"):
        raise ValueError
    return urlopen(Request(url, headers={"User-Agent": "Mozilla/5.0"}))  # nosec


def get(url) -> str:
    """Send an http GET request.

    :param str url:
        The URL to perform the GET request for.
    :rtype: str
    :returns:
        UTF-8 encoded string of response
    """
    return _execute_request(url).read().decode("utf-8")


def stream(url: str, chunk_size: int = 8192) -> Iterable[bytes]:
    """Read the response in chunks.
    :param str url:
        The URL to perform the GET request for.
    :param int chunk_size:
        The size in bytes of each chunk. Defaults to 8*1024
    :rtype: Iterable[bytes]
    """
    response = _execute_request(url)
    while True:
        buf = response.read(chunk_size)
        if not buf:
            break
        yield buf


def headers(url: str) -> Dict:
    """Fetch headers returned http GET request.

    :param str url:
        The URL to perform the GET request for.
    :rtype: dict
    :returns:
        dictionary of lowercase headers
    """
    return {k.lower(): v for k, v in _execute_request(url).info().items()}
