# -*- coding: utf-8 -*-
from unittest import mock
from unittest.mock import MagicMock

from pytube import Playlist


@mock.patch("pytube.contrib.playlist.request.get")
def test_title(request_get):
    request_get.return_value = (
        "<title>(149) Python Tutorial for Beginners "
        "(For Absolute Beginners) - YouTube</title>"
    )
    url = "https://www.fakeurl.com/playlist?list=PLS1QulWo1RIaJECMeUT4LFwJ-ghgoSH6n"
    pl = Playlist(url)
    pl_title = pl.title()
    assert pl_title == "(149) Python Tutorial for Beginners (For Absolute Beginners)"


@mock.patch("pytube.contrib.playlist.request.get")
def test_init_with_playlist_url(request_get):
    request_get.return_value = ""
    url = "https://www.youtube.com/playlist?list=PLS1QulWo1RIaJECMeUT4LFwJ-ghgoSH6n"
    playlist = Playlist(url)
    assert playlist.playlist_url == url


@mock.patch("pytube.contrib.playlist.request.get")
def test_init_with_watch_url(request_get):
    request_get.return_value = ""
    url = (
        "https://www.youtube.com/watch?v=1KeYzjILqDo&"
        "list=PLS1QulWo1RIaJECMeUT4LFwJ-ghgoSH6n&index=2&t=661s"
    )
    playlist = Playlist(url)
    assert (
        playlist.playlist_url
        == "https://www.youtube.com/playlist?list=PLS1QulWo1RIaJECMeUT4LFwJ-ghgoSH6n"
    )


@mock.patch("pytube.contrib.playlist.request.get")
def test_parse_links(request_get, playlist_html):
    url = "https://www.fakeurl.com/playlist?list=whatever"
    request_get.return_value = playlist_html
    playlist = Playlist(url)
    playlist._find_load_more_url = MagicMock(return_value=None)
    links = playlist.parse_links()
    request_get.assert_called()
    assert links == [
        "/watch?v=ujTCoH21GlA",
        "/watch?v=45ryDIPHdGg",
        "/watch?v=1BYu65vLKdA",
        "/watch?v=3AQ_74xrch8",
        "/watch?v=ddqQUz9mZaM",
        "/watch?v=vwLT6bZrHEE",
        "/watch?v=TQKI0KE-JYY",
        "/watch?v=dNBvQ38MlT8",
        "/watch?v=JHxyrMgOUWI",
        "/watch?v=l2I8NycJMCY",
        "/watch?v=g1Zbuk1gAfk",
        "/watch?v=zixd-si9Q-o",
    ]


@mock.patch("pytube.contrib.playlist.request.get")
def test_video_urls(request_get, playlist_html):
    url = "https://www.fakeurl.com/playlist?list=whatever"
    request_get.return_value = playlist_html
    playlist = Playlist(url)
    playlist._find_load_more_url = MagicMock(return_value=None)
    request_get.assert_called()
    assert playlist.video_urls == [
        "https://www.youtube.com/watch?v=ujTCoH21GlA",
        "https://www.youtube.com/watch?v=45ryDIPHdGg",
        "https://www.youtube.com/watch?v=1BYu65vLKdA",
        "https://www.youtube.com/watch?v=3AQ_74xrch8",
        "https://www.youtube.com/watch?v=ddqQUz9mZaM",
        "https://www.youtube.com/watch?v=vwLT6bZrHEE",
        "https://www.youtube.com/watch?v=TQKI0KE-JYY",
        "https://www.youtube.com/watch?v=dNBvQ38MlT8",
        "https://www.youtube.com/watch?v=JHxyrMgOUWI",
        "https://www.youtube.com/watch?v=l2I8NycJMCY",
        "https://www.youtube.com/watch?v=g1Zbuk1gAfk",
        "https://www.youtube.com/watch?v=zixd-si9Q-o",
    ]


@mock.patch("pytube.contrib.playlist.request.get")
@mock.patch("pytube.cli.YouTube.__init__", return_value=None)
def test_videos(youtube, request_get, playlist_html):
    url = "https://www.fakeurl.com/playlist?list=whatever"
    request_get.return_value = playlist_html
    playlist = Playlist(url)
    playlist._find_load_more_url = MagicMock(return_value=None)
    request_get.assert_called()
    assert len(list(playlist.videos)) == 12


@mock.patch("pytube.contrib.playlist.request.get")
@mock.patch("pytube.contrib.playlist.install_proxy", return_value=None)
def test_proxy(install_proxy, request_get):
    url = "https://www.fakeurl.com/playlist?list=whatever"
    request_get.return_value = ""
    Playlist(url, proxies={"http": "things"})
    install_proxy.assert_called_with({"http": "things"})


@mock.patch("pytube.contrib.playlist.request.get")
def test_trimmed(request_get, playlist_html):
    url = "https://www.fakeurl.com/playlist?list=whatever"
    request_get.return_value = playlist_html
    playlist = Playlist(url)
    playlist._find_load_more_url = MagicMock(return_value=None)
    assert playlist.trimmed("1BYu65vLKdA") == [
        "https://www.youtube.com/watch?v=ujTCoH21GlA",
        "https://www.youtube.com/watch?v=45ryDIPHdGg",
    ]
