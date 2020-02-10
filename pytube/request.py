# -*- coding: utf-8 -*-

"""Implements a simple wrapper around urlopen."""
from typing import Any, Iterable, Dict, Optional
from urllib.request import Request
from urllib.request import urlopen


def _execute_request(
    url: str, method: Optional[str] = None, headers: Optional[Dict[str, str]] = None
) -> Any:
    base_headers = {"User-Agent": "Mozilla/5.0"}
    if headers:
        base_headers.update(headers)
    if url.lower().startswith("http"):
        request = Request(url, headers=base_headers, method=method)
    else:
        raise ValueError
    return urlopen(request)  # nosec


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
    :param str url: The URL to perform the GET request for.
    :param int chunk_size: The size in bytes of each chunk. Defaults to 8*1024
    :rtype: Iterable[bytes]
    """
    response = _execute_request(url, headers={"Range": "bytes=0-"})
    while True:
        buf = response.read(chunk_size)
        if not buf:
            break
        yield buf


def head(url: str) -> Dict:
    """Fetch headers returned http GET request.

    :param str url:
        The URL to perform the GET request for.
    :rtype: dict
    :returns:
        dictionary of lowercase headers
    """
    response_headers = _execute_request(url, method="HEAD").info()
    return {k.lower(): v for k, v in response_headers.items()}
