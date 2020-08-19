# -*- coding: utf-8 -*-
import os
from unittest import mock

import pytest

from pytube import request


@mock.patch("pytube.request.urlopen")
def test_streaming(mock_urlopen):
    # Given
    fake_stream_binary = [
        os.urandom(8 * 1024),
        os.urandom(8 * 1024),
        os.urandom(8 * 1024),
        None,
    ]
    response = mock.Mock()
    response.read.side_effect = fake_stream_binary
    response.info.return_value = {"Content-Range": "bytes 200-1000/24576"}
    mock_urlopen.return_value = response
    # When
    response = request.stream("http://fakeassurl.gov")
    # Then
    call_count = len(list(response))
    assert call_count == 3


@mock.patch("pytube.request.urlopen")
def test_headers(mock_urlopen):
    response = mock.Mock()
    response.info.return_value = {"content-length": "16384"}
    mock_urlopen.return_value = response
    response = request.head("http://fakeassurl.gov")
    assert response == {"content-length": "16384"}


@mock.patch("pytube.request.urlopen")
def test_get(mock_urlopen):
    response = mock.Mock()
    response.read.return_value = "<html></html>".encode("utf-8")
    mock_urlopen.return_value = response
    response = request.get("http://fakeassurl.gov")
    assert response == "<html></html>"


def test_get_non_http():
    with pytest.raises(ValueError):  # noqa: PT011
        request.get("file://bad")
