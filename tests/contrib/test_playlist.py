# -*- coding: utf-8 -*-
from unittest import mock

from pytube import Playlist


@mock.patch("pytube.contrib.playlist.request.get")
def test_title(request_get):
    request_get.return_value = (
        "<title>(149) Python Tutorial for Beginners "
        "(For Absolute Beginners) - YouTube</title>"
    )
    url = "https://www.fakeurl.com/playlist?list=PLsyeobzWxl7poL9JTVyndKe62ieoN"
    pl = Playlist(url)
    pl_title = pl.title()
    assert pl_title == "(149) Python Tutorial for Beginners (For Absolute Beginners)"


def test_init_with_playlist_url():
    url = "https://www.youtube.com/playlist?list=PLynhp4cZEpTbRs_PYISQ8v_uwO0_mDg_X"
    playlist = Playlist(url)
    assert playlist.playlist_url == url


def test_init_with_watch_url():
    url = (
        "https://www.youtube.com/watch?v=1KeYzjILqDo&"
        "list=PLynhp4cZEpTbRs_PYISQ8v_uwO0_mDg_X&index=2&t=661s"
    )
    playlist = Playlist(url)
    assert (
        playlist.playlist_url
        == "https://www.youtube.com/playlist?list=PLynhp4cZEpTbRs_PYISQ8v_uwO0_mDg_X"
    )
