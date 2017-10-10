# -*- coding: utf-8 -*-
"""Unit tests for the :class:`StreamQuery <StreamQuery>` class."""
import pytest


def test_count(gangnam_style):
    assert gangnam_style.streams.count() == 22


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
def test_filters(test_input, expected, gangnam_style):
    result = [s.itag for s in gangnam_style.streams.filter(**test_input).all()]
    assert result == expected


@pytest.mark.parametrize('test_input', ['first', 'last'])
def test_empty(test_input, gangnam_style):
    query = gangnam_style.streams.filter(video_codec='vp20')
    fn = getattr(query, test_input)
    assert fn() is None


def test_get_last(gangnam_style):
    assert gangnam_style.streams.last().itag == '251'


def test_get_first(gangnam_style):
    assert gangnam_style.streams.first().itag == '22'


def test_order_by(gangnam_style):
    itags = [
        s.itag for s in gangnam_style.streams
        .filter(progressive=True)
        .order_by('itag')
        .all()
    ]

    assert itags == ['17', '18', '22', '36', '43']


def test_order_by_descending(gangnam_style):
    itags = [
        s.itag for s in gangnam_style.streams
        .filter(progressive=True)
        .order_by('itag')
        .desc()
        .all()
    ]

    assert itags == ['43', '36', '22', '18', '17']


def test_order_by_ascending(gangnam_style):
    itags = [
        s.itag for s in gangnam_style.streams
        .filter(progressive=True)
        .order_by('itag')
        .asc()
        .all()
    ]

    assert itags == ['17', '18', '22', '36', '43']


def test_get_by_itag(gangnam_style):
    assert gangnam_style.streams.get_by_itag(22).itag == '22'


def test_get_by_non_existent_itag(gangnam_style):
    assert not gangnam_style.streams.get_by_itag(22983)
