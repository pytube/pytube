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
