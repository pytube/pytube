# -*- coding: utf-8 -*-
"""Unit tests for the :module:`extract <extract>` module."""
from pytube import extract


def test_extract_video_id():
    url = 'https://www.youtube.com/watch?v=9bZkp7q19f0'
    video_id = extract.video_id(url)
    assert video_id == '9bZkp7q19f0'


def test_extract_watch_url():
    video_id = '9bZkp7q19f0'
    watch_url = extract.watch_url(video_id)
    assert watch_url == 'https://youtube.com/watch?v=9bZkp7q19f0'


def test_info_url(cipher_signature):
    video_info_url = extract.video_info_url(
        video_id=cipher_signature.video_id,
        watch_url=cipher_signature.watch_url,
        watch_html=cipher_signature.watch_html,
        embed_html='',
        age_restricted=False,
    )
    expected = (
        'https://youtube.com/get_video_info?video_id=9bZkp7q19f0&el=%24el'
        '&ps=default&eurl=https%253A%2F%2Fyoutube.com%2Fwatch%253Fv%'
        '253D9bZkp7q19f0&hl=en_US&t=%252C%2522t%2522%253A%25221%2522'
    )
    assert video_info_url == expected


def test_js_url(cipher_signature):
    expected = 'https://youtube.com/yts/jsbin/player-vflOdyxa4/en_US/base.js'
    result = extract.js_url(cipher_signature.watch_html)
    assert expected == result


def test_age_restricted(age_restricted):
    assert extract.is_age_restricted(age_restricted['watch_html'])


def test_non_age_restricted(cipher_signature):
    assert not extract.is_age_restricted(cipher_signature.watch_html)


def test_get_vid_desc(cipher_signature):
    expected = "PSY - DADDY(feat. CL of 2NE1) M/V @ https://youtu.be/FrG4TEcSuRgPSY - 나팔바지(NAPAL BAJI) M/V @ https://youtu.be/tF27TNC_4pcPSY - 7TH ALBUM '칠집싸이다' on iTunes @ http://smarturl.it/PSY_7THALBUMPSY - GANGNAM STYLE(강남스타일) on iTunes @ http://smarturl.it/PsyGangnam#PSY #싸이 #GANGNAMSTYLE #강남스타일More about PSY@http://www.psypark.com/http://www.youtube.com/officialpsyhttp://www.facebook.com/officialpsyhttp://twitter.com/psy_oppahttps://www.instagram.com/42psy42http://iTunes.com/PSYhttp://sptfy.com/PSYhttp://weibo.com/psyoppahttp://twitter.com/ygent_official"  # noqa
    assert extract.get_vid_descr(cipher_signature.watch_html) == expected
