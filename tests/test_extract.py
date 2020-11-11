# -*- coding: utf-8 -*-
"""Unit tests for the :module:`extract <extract>` module."""
from datetime import datetime
import pytest

from pytube import extract
from pytube.exceptions import RegexMatchError


def test_extract_video_id():
    url = "https://www.youtube.com/watch?v=2lAe1cqCOXo"
    video_id = extract.video_id(url)
    assert video_id == "2lAe1cqCOXo"


def test_info_url(age_restricted):
    video_info_url = extract.video_info_url_age_restricted(
        video_id="QRS8MkLhQmM", embed_html=age_restricted["embed_html"],
    )
    expected = (
        "https://youtube.com/get_video_info?video_id=QRS8MkLhQmM&eurl"
        "=https%3A%2F%2Fyoutube.googleapis.com%2Fv%2FQRS8MkLhQmM&sts="
    )
    assert video_info_url == expected


def test_info_url_age_restricted(cipher_signature):
    video_info_url = extract.video_info_url(
        video_id=cipher_signature.video_id,
        watch_url=cipher_signature.watch_url,
    )
    expected = (
        "https://youtube.com/get_video_info?video_id=2lAe1cqCOXo"
        "&ps=default&eurl=https%253A%2F%2Fyoutube.com%2Fwatch%253Fv%"
        "253D2lAe1cqCOXo&hl=en_US"
    )
    assert video_info_url == expected


def test_js_url(cipher_signature):
    expected = (
        "https://youtube.com/s/player/9b65e980/player_ias.vflset/en_US/base.js"
    )
    result = extract.js_url(cipher_signature.watch_html)
    assert expected == result


def test_age_restricted(age_restricted):
    assert extract.is_age_restricted(age_restricted["watch_html"])


def test_non_age_restricted(cipher_signature):
    assert not extract.is_age_restricted(cipher_signature.watch_html)


def test_is_private(private):
    assert extract.is_private(private['watch_html'])


def test_not_is_private(cipher_signature):
    assert not extract.is_private(cipher_signature.watch_html)


def test_recording_available(cipher_signature):
    assert extract.recording_available(cipher_signature.watch_html)


def test_publish_date(cipher_signature):
    expected = datetime(2019, 12, 5)
    assert cipher_signature.publish_date == expected
    assert extract.publish_date('') is None


def test_not_recording_available(missing_recording):
    assert not extract.recording_available(missing_recording['watch_html'])


def test_mime_type_codec():
    mime_type, mime_subtype = extract.mime_type_codec(
        'audio/webm; codecs="opus"'
    )
    assert mime_type == "audio/webm"
    assert mime_subtype == ["opus"]


def test_mime_type_codec_with_no_match_should_error():
    with pytest.raises(RegexMatchError):
        extract.mime_type_codec("audio/webm")


def test_get_ytplayer_config_with_no_match_should_error():
    with pytest.raises(RegexMatchError):
        extract.get_ytplayer_config("")


def test_get_ytplayer_js_with_no_match_should_error():
    with pytest.raises(RegexMatchError):
        extract.get_ytplayer_js("")


def test_signature_cipher_does_not_error(stream_dict):
    config_args = extract.get_ytplayer_config(stream_dict)['args']
    extract.apply_descrambler(config_args, "url_encoded_fmt_stream_map")
    assert "s" in config_args["url_encoded_fmt_stream_map"][0].keys()


def test_initial_data_missing():
    initial_data = extract.initial_data('')
    assert initial_data == "{}"


def test_initial_data(stream_dict):
    initial_data = extract.initial_data(stream_dict)
    assert 'contents' in initial_data
