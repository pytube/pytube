# -*- coding: utf-8 -*-
"""Unit tests for the :class:`StreamQuery <StreamQuery>` class."""
import pytest


def test_count(cipher_signature):
    """Ensure :meth:`~pytube.StreamQuery.count` returns an accurate amount."""
    assert cipher_signature.streams.count() == 22


@pytest.mark.parametrize(
    'test_input,expected', [
        ({'progressive': True}, ['22', '43', '18', '36', '17']),
        ({'resolution': '720p'}, ['22', '136', '247']),
        ({'res': '720p'}, ['22', '136', '247']),
        ({'fps': 30, 'resolution': '480p'}, ['135', '244']),
        ({'mime_type': 'audio/mp4'}, ['140']),
        ({'type': 'audio'}, ['140', '171', '249', '250', '251']),
        ({'subtype': '3gpp'}, ['36', '17']),
        ({'abr': '128kbps'}, ['43', '140', '171']),
        ({'bitrate': '128kbps'}, ['43', '140', '171']),
        ({'audio_codec': 'vorbis'}, ['43', '171']),
        ({'video_codec': 'vp9'}, ['248', '247', '244', '243', '242', '278']),
        ({'only_audio': True}, ['140', '171', '249', '250', '251']),
        ({'only_video': True, 'video_codec': 'avc1.4d4015'}, ['133']),
        ({'progressive': True}, ['22', '43', '18', '36', '17']),
        ({'adaptive': True, 'resolution': '1080p'}, ['137', '248']),
        ({'custom_filter_functions': [lambda s: s.itag == '22']}, ['22']),
    ],
)
def test_filters(test_input, expected, cipher_signature):
    """Ensure filters produce the expected results."""
    result = [
        s.itag for s
        in cipher_signature.streams.filter(**test_input).all()
    ]
    assert result == expected


@pytest.mark.parametrize('test_input', ['first', 'last'])
def test_empty(test_input, cipher_signature):
    """Ensure :meth:`~pytube.StreamQuery.last` and
    :meth:`~pytube.StreamQuery.first` return None if the resultset is
    empty.
    """
    query = cipher_signature.streams.filter(video_codec='vp20')
    fn = getattr(query, test_input)
    assert fn() is None


def test_get_last(cipher_signature):
    """Ensure :meth:`~pytube.StreamQuery.last` returns the expected
    :class:`Stream <Stream>`.
    """
    assert cipher_signature.streams.last().itag == '251'


def test_get_first(cipher_signature):
    """Ensure :meth:`~pytube.StreamQuery.first` returns the expected
    :class:`Stream <Stream>`.
    """
    assert cipher_signature.streams.first().itag == '22'


def test_order_by(cipher_signature):
    """Ensure :meth:`~pytube.StreamQuery.order_by` sorts the list of
    :class:`Stream <Stream>` instances in the expected order.
    """
    itags = [
        s.itag for s in cipher_signature.streams
        .filter(progressive=True)
        .order_by('itag')
        .all()
    ]

    assert itags == ['17', '18', '22', '36', '43']


def test_order_by_descending(cipher_signature):
    """Ensure :meth:`~pytube.StreamQuery.desc` sorts the list of
    :class:`Stream <Stream>` instances in the reverse order.
    """
    # numerical values
    itags = [
        s.itag for s in cipher_signature.streams
        .filter(progressive=True)
        .order_by('itag')
        .desc()
        .all()
    ]
    assert itags == ['43', '36', '22', '18', '17']

    # non numerical values
    mime_types = [
        s.mime_type for s in cipher_signature.streams
        .filter(progressive=True)
        .order_by('mime_type')
        .desc()
        .all()
    ]
    assert mime_types == [
        'video/webm', 'video/mp4',
        'video/mp4', 'video/3gpp', 'video/3gpp',
    ]


def test_order_by_ascending(cipher_signature):
    """Ensure :meth:`~pytube.StreamQuery.desc` sorts the list of
    :class:`Stream <Stream>` instances in ascending order.
    """
    # numerical values
    itags = [
        s.itag for s in cipher_signature.streams
        .filter(progressive=True)
        .order_by('itag')
        .asc()
        .all()
    ]

    assert itags == ['17', '18', '22', '36', '43']

    # non numerical values
    mime_types = [
        s.mime_type for s in cipher_signature.streams
        .filter(progressive=True)
        .order_by('mime_type')
        .asc()
        .all()
    ]
    assert mime_types == [
        'video/3gpp', 'video/3gpp',
        'video/mp4', 'video/mp4', 'video/webm',
    ]


def test_get_by_itag(cipher_signature):
    """Ensure :meth:`~pytube.StreamQuery.get_by_itag` returns the expected
    :class:`Stream <Stream>`.
    """
    assert cipher_signature.streams.get_by_itag(22).itag == '22'
    assert cipher_signature.streams.get_by_itag('22').itag == '22'


def test_get_by_non_existent_itag(cipher_signature):
    assert not cipher_signature.streams.get_by_itag(22983)
