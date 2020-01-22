# -*- coding: utf-8 -*-
"""Unit tests for the :module:`extract <extract>` module."""
import pytest

from pytube.exceptions import RegexMatchError

from pytube import extract


def test_extract_video_id():
    url = "https://www.youtube.com/watch?v=9bZkp7q19f0"
    video_id = extract.video_id(url)
    assert video_id == "9bZkp7q19f0"


def test_extract_watch_url():
    video_id = "9bZkp7q19f0"
    watch_url = extract.watch_url(video_id)
    assert watch_url == "https://youtube.com/watch?v=9bZkp7q19f0"


def test_info_url(cipher_signature):
    video_info_url = extract.video_info_url(
        video_id=cipher_signature.video_id,
        watch_url=cipher_signature.watch_url,
        embed_html="",
        age_restricted=False,
    )
    expected = (
        "https://youtube.com/get_video_info?video_id=9bZkp7q19f0&el=%24el"
        "&ps=default&eurl=https%253A%2F%2Fyoutube.com%2Fwatch%253Fv%"
        "253D9bZkp7q19f0&hl=en_US"
    )
    assert video_info_url == expected


def test_js_url(cipher_signature):
    expected = "https://youtube.com/yts/jsbin/player_ias-vflWQEEag/en_US/base.js"
    result = extract.js_url(cipher_signature.watch_html)
    assert expected == result


def test_age_restricted(age_restricted):
    assert extract.is_age_restricted(age_restricted["watch_html"])


def test_non_age_restricted(cipher_signature):
    assert not extract.is_age_restricted(cipher_signature.watch_html)


def test_get_vid_desc(cipher_signature):
    expected = (
        "PSY - ‘I LUV IT’ M/V @ https://youtu.be/Xvjnoagk6GU\n"
        "PSY - ‘New Face’ M/V @https://youtu.be/OwJPPaEyqhI\n"
        "PSY - 8TH ALBUM '4X2=8' on iTunes @\n"
        "https://smarturl.it/PSY_8thAlbum\n"
        "PSY - GANGNAM STYLE(강남스타일) on iTunes @ http://smarturl.it/PsyGangnam\n"
        "#PSY #싸이 #GANGNAMSTYLE #강남스타일\n"
        "More about PSY@\nhttp://www.youtube.com/officialpsy\n"
        "http://www.facebook.com/officialpsy\n"
        "http://twitter.com/psy_oppa\n"
        "https://www.instagram.com/42psy42\n"
        "http://iTunes.com/PSY\n"
        "http://sptfy.com/PSY\n"
        "http://weibo.com/psyoppa"
    )
    assert extract.get_vid_descr(cipher_signature.watch_html) == expected


def test_eurl():
    url = extract.eurl("videoid")
    assert url == "https://youtube.googleapis.com/v/videoid"


def test_mime_type_codec():
    mime_type, mime_subtype = extract.mime_type_codec('audio/webm; codecs="opus"')
    assert mime_type == "audio/webm"
    assert mime_subtype == ["opus"]


def test_mime_type_codec_with_no_match_should_error():
    with pytest.raises(RegexMatchError):
        extract.mime_type_codec("audio/webm")
