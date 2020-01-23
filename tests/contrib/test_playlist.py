# -*- coding: utf-8 -*-
from unittest import mock
from unittest.mock import MagicMock

from pytube import Playlist


@mock.patch("request.get")
def test_title(request_get):
    request_get.return_value = ""
    list_key = "PLsyeobzWxl7poL9JTVyndKe62ieoN-MZ3"
    url = "https://www.fakeurl.com/playlist?list=" + list_key
    pl = Playlist(url)
    pl_title = pl.title()
    assert pl_title == "Python Tutorial for Beginners"
