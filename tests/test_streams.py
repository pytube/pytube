# -*- coding: utf-8 -*-
import random

import mock

from pytube import request
from pytube import Stream


def test_filesize(cipher_signature, mocker):
    mocker.patch.object(request, 'get')
    request.get.return_value = {'content-length': '6796391'}
    assert cipher_signature.streams.first().filesize == 6796391


def test_default_filename(cipher_signature):
    expected = 'PSY - GANGNAM STYLE(강남스타일) MV.mp4'
    stream = cipher_signature.streams.first()
    assert stream.default_filename == expected


def test_download(cipher_signature, mocker):
    mocker.patch.object(request, 'get')
    request.get.side_effect = [
        {'content-length': '16384'},
        {'content-length': '16384'},
        iter([str(random.getrandbits(8 * 1024))]),
    ]
    with mock.patch('pytube.streams.open', mock.mock_open(), create=True):
        stream = cipher_signature.streams.first()
        stream.download()


def test_progressive_streams_return_includes_audio_track(cipher_signature):
    stream = cipher_signature.streams.filter(progressive=True).first()
    assert stream.includes_audio_track


def test_progressive_streams_return_includes_video_track(cipher_signature):
    stream = cipher_signature.streams.filter(progressive=True).first()
    assert stream.includes_video_track


def test_on_progress_hook(cipher_signature, mocker):
    callback_fn = mock.MagicMock()
    cipher_signature.register_on_progress_callback(callback_fn)

    mocker.patch.object(request, 'get')
    request.get.side_effect = [
        {'content-length': '16384'},
        {'content-length': '16384'},
        iter([str(random.getrandbits(8 * 1024))]),
    ]
    with mock.patch('pytube.streams.open', mock.mock_open(), create=True):
        stream = cipher_signature.streams.first()
        stream.download()
    assert callback_fn.called
    args, _ = callback_fn.call_args
    assert len(args) == 4
    stream, _, _, _ = args
    assert isinstance(stream, Stream)


def test_on_complete_hook(cipher_signature, mocker):
    callback_fn = mock.MagicMock()
    cipher_signature.register_on_complete_callback(callback_fn)

    mocker.patch.object(request, 'get')
    request.get.side_effect = [
        {'content-length': '16384'},
        {'content-length': '16384'},
        iter([str(random.getrandbits(8 * 1024))]),
    ]
    with mock.patch('pytube.streams.open', mock.mock_open(), create=True):
        stream = cipher_signature.streams.first()
        stream.download()
    assert callback_fn.called


def test_repr_for_audio_streams(cipher_signature):
    stream = str(cipher_signature.streams.filter(only_audio=True).first())
    expected = (
        '<Stream: itag="140" mime_type="audio/mp4" abr="128kbps" '
        'acodec="mp4a.40.2">'
    )
    assert stream == expected


def test_repr_for_video_streams(cipher_signature):
    stream = str(cipher_signature.streams.filter(only_video=True).first())
    expected = (
        '<Stream: itag="137" mime_type="video/mp4" res="1080p" '
        'fps="30fps" vcodec="avc1.640028">'
    )
    assert stream == expected


def test_repr_for_progressive_streams(cipher_signature):
    stream = str(cipher_signature.streams.filter(progressive=True).first())
    expected = (
        '<Stream: itag="22" mime_type="video/mp4" res="720p" '
        'fps="30fps" vcodec="avc1.64001F" acodec="mp4a.40.2">'
    )
    assert stream == expected


def test_repr_for_adaptive_streams(cipher_signature):
    stream = str(cipher_signature.streams.filter(adaptive=True).first())
    expected = (
        '<Stream: itag="137" mime_type="video/mp4" res="1080p" '
        'fps="30fps" vcodec="avc1.640028">'
    )
    assert stream == expected
