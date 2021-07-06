"""Unit tests for the :module:`extract <extract>` module."""
from datetime import datetime
import pytest
import re

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
    assert video_info_url.startswith('https://www.youtube.com/get_video_info')
    assert 'video_id=QRS8MkLhQmM' in video_info_url


def test_info_url_age_restricted(cipher_signature):
    video_info_url = extract.video_info_url(
        video_id=cipher_signature.video_id,
        watch_url=cipher_signature.watch_url,
    )
    assert video_info_url.startswith('https://www.youtube.com/get_video_info')
    assert 'video_id=2lAe1cqCOXo' in video_info_url


def test_js_url(cipher_signature):
    expected = (
        r"https://youtube.com/s/player/([\w\d]+)/player_ias.vflset/en_US/base.js"
    )
    result = extract.js_url(cipher_signature.watch_html)
    match = re.search(expected, result)
    assert match is not None


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


def test_initial_data_missing():
    with pytest.raises(RegexMatchError):
        extract.initial_data('')


def test_initial_data(stream_dict):
    initial_data = extract.initial_data(stream_dict)
    assert 'contents' in initial_data
