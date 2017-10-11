# -*- coding: utf-8 -*-
import random

import mock

from pytube import request


def test_filesize(gangnam_style, mocker):
    mocker.patch.object(request, 'get')
    request.get.return_value = {'Content-Length': '6796391'}
    assert gangnam_style.streams.first().filesize == 6796391


def test_default_filename(gangnam_style):
    expected = 'PSY - GANGNAM STYLE(강남스타일) MV.mp4'
    stream = gangnam_style.streams.first()
    assert stream.default_filename == expected


def test_download(gangnam_style, mocker):
    mocker.patch.object(request, 'get')
    request.get.side_effect = [
        {'Content-Length': '16384'},
        {'Content-Length': '16384'},
        iter([str(random.getrandbits(8 * 1024))]),
    ]
    with mock.patch('pytube.streams.open', mock.mock_open(), create=True):
        stream = gangnam_style.streams.first()
        stream.download()


def test_progressive_streams_return_includes_audio_track(gangnam_style):
    stream = gangnam_style.streams.filter(progressive=True).first()
    assert stream.includes_audio_track


def test_progressive_streams_return_includes_video_track(gangnam_style):
    stream = gangnam_style.streams.filter(progressive=True).first()
    assert stream.includes_video_track
