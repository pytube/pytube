# -*- coding: utf-8 -*-
import os

import mock

from pytube import request


@mock.patch('pytube.request.urlopen')
def test_get_streaming(mock_urlopen):
    fake_stream_binary = [
        iter(os.urandom(8 * 1024)),
        iter(os.urandom(8 * 1024)),
        iter(os.urandom(8 * 1024)),
        None,
    ]
    response = mock.Mock()
    response.read.side_effect = fake_stream_binary
    mock_urlopen.return_value = response
    response = request.get('fakeassurl.gov', streaming=True)
    call_count = 0
    for i in response:
        call_count += 1
    assert call_count == 3


@mock.patch('pytube.request.urlopen')
def test_get_headers(mock_urlopen):
    response = mock.Mock()
    response.info.return_value = {'content-length': '16384'}
    mock_urlopen.return_value = response
    response = request.get('fakeassurl.gov', headers=True)
    assert response == {'content-length': '16384'}


@mock.patch('pytube.request.urlopen')
def test_get(mock_urlopen):
    response = mock.Mock()
    response.read.return_value = '<html></html>'.encode('utf-8')
    mock_urlopen.return_value = response
    response = request.get('fakeassurl.gov')
    assert response == '<html></html>'
