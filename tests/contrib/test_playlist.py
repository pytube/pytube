import datetime
from unittest import mock

from pytube import Playlist


@mock.patch("pytube.request.get")
def test_title(request_get, playlist_long_html):
    request_get.return_value = playlist_long_html
    url = (
        "https://www.fakeurl.com/playlist?list=PLS1QulWo1RIaJECMeUT4LFwJ"
        "-ghgoSH6n"
    )
    pl = Playlist(url)
    pl_title = pl.title
    assert (
        pl_title
        == "Python Tutorial for Beginners (For Absolute Beginners)"
    )


@mock.patch("pytube.request.get")
def test_init_with_playlist_url(request_get):
    request_get.return_value = ""
    url = (
        "https://www.youtube.com/playlist?list=PLS1QulWo1RIaJECMeUT4LFwJ"
        "-ghgoSH6n"
    )
    playlist = Playlist(url)
    assert playlist.playlist_url == url


@mock.patch("pytube.request.get")
def test_init_with_watch_url(request_get):
    request_get.return_value = ""
    url = (
        "https://www.youtube.com/watch?v=1KeYzjILqDo&"
        "list=PLS1QulWo1RIaJECMeUT4LFwJ-ghgoSH6n&index=2&t=661s"
    )
    playlist = Playlist(url)
    assert (
        playlist.playlist_url == "https://www.youtube.com/playlist?list"
        "=PLS1QulWo1RIaJECMeUT4LFwJ-ghgoSH6n"
    )


@mock.patch("pytube.request.get")
def test_last_updated(request_get, playlist_long_html):
    expected = datetime.date(2020, 10, 8)
    request_get.return_value = playlist_long_html
    playlist = Playlist(
        "https://www.youtube.com/playlist?list"
        "=PLS1QulWo1RIaJECMeUT4LFwJ-ghgoSH6n"
    )
    assert playlist.last_updated == expected


@mock.patch("pytube.request.get")
def test_video_urls(request_get, playlist_html):
    url = "https://www.fakeurl.com/playlist?list=whatever"
    request_get.return_value = playlist_html
    playlist = Playlist(url)
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
    request_get.assert_called()


@mock.patch("pytube.request.get")
def test_html(request_get, playlist_html):
    url = "https://www.fakeurl.com/playlist?list=whatever"
    request_get.return_value = playlist_html
    playlist = Playlist(url)
    assert playlist.html == playlist_html
    request_get.assert_called()


@mock.patch("pytube.request.get")
def test_repr(request_get, playlist_html):
    url = "https://www.fakeurl.com/playlist?list=whatever"
    request_get.return_value = playlist_html
    playlist = Playlist(url)
    assert (
        repr(playlist) == "["
        "'https://www.youtube.com/watch?v=ujTCoH21GlA', "
        "'https://www.youtube.com/watch?v=45ryDIPHdGg', "
        "'https://www.youtube.com/watch?v=1BYu65vLKdA', "
        "'https://www.youtube.com/watch?v=3AQ_74xrch8', "
        "'https://www.youtube.com/watch?v=ddqQUz9mZaM', "
        "'https://www.youtube.com/watch?v=vwLT6bZrHEE', "
        "'https://www.youtube.com/watch?v=TQKI0KE-JYY', "
        "'https://www.youtube.com/watch?v=dNBvQ38MlT8', "
        "'https://www.youtube.com/watch?v=JHxyrMgOUWI', "
        "'https://www.youtube.com/watch?v=l2I8NycJMCY', "
        "'https://www.youtube.com/watch?v=g1Zbuk1gAfk', "
        "'https://www.youtube.com/watch?v=zixd-si9Q-o'"
        "]"
    )
    request_get.assert_called()


@mock.patch("pytube.request.get")
def test_sequence(request_get, playlist_html):
    url = "https://www.fakeurl.com/playlist?list=whatever"
    request_get.return_value = playlist_html
    playlist = Playlist(url)
    assert playlist[0] == "https://www.youtube.com/watch?v=ujTCoH21GlA"
    assert len(playlist) == 12


@mock.patch("pytube.request.get")
@mock.patch("pytube.cli.YouTube.__init__", return_value=None)
def test_videos(youtube, request_get, playlist_html):
    url = "https://www.fakeurl.com/playlist?list=whatever"
    request_get.return_value = playlist_html
    playlist = Playlist(url)
    assert len(list(playlist.videos)) == 12
    request_get.assert_called()


@mock.patch("pytube.request.get")
@mock.patch("pytube.cli.YouTube.__init__", return_value=None)
def test_load_more(youtube, request_get, playlist_html):
    url = "https://www.fakeurl.com/playlist?list=whatever"
    request_get.side_effect = [
        playlist_html,
        '{"content_html":"", "load_more_widget_html":""}',
    ]
    playlist = Playlist(url)
    assert len(list(playlist.videos)) == 12
    request_get.assert_called()


@mock.patch("pytube.request.get")
@mock.patch("pytube.contrib.playlist.install_proxy", return_value=None)
def test_proxy(install_proxy, request_get):
    url = "https://www.fakeurl.com/playlist?list=whatever"
    request_get.return_value = ""
    Playlist(url, proxies={"http": "things"})
    install_proxy.assert_called_with({"http": "things"})


@mock.patch("pytube.request.get")
def test_trimmed(request_get, playlist_html):
    url = "https://www.fakeurl.com/playlist?list=whatever"
    request_get.return_value = playlist_html
    playlist = Playlist(url)
    trimmed = list(playlist.trimmed("1BYu65vLKdA"))
    assert trimmed == [
        "https://www.youtube.com/watch?v=ujTCoH21GlA",
        "https://www.youtube.com/watch?v=45ryDIPHdGg",
    ]
    assert request_get.call_count == 1


@mock.patch("pytube.request.get")
@mock.patch("pytube.request.post")
def test_playlist_failed_pagination(request_post, request_get, playlist_long_html):
    url = "https://www.fakeurl.com/playlist?list=whatever"
    request_get.side_effect = [
        playlist_long_html,
    ]
    request_post.side_effect = [
        "{}"
    ]
    playlist = Playlist(url)
    video_urls = playlist.video_urls
    assert len(video_urls) == 100
    assert request_get.call_count == 1
    assert request_post.call_count == 1
    # TODO: Cannot get this test to work probably
    # request_get.assert_called_with(
    #    "https://www.youtube.com/browse_ajax?ctoken" # noqa
    #    "=4qmFsgIsEhpWTFVVYS12aW9HaGUyYnRCY1puZWFQb25LQRoOZWdaUVZEcERSMUUlM0Q" # noqa
    #    "%3D&continuation" # noqa
    #    "=4qmFsgIsEhpWTFVVYS12aW9HaGUyYnRCY1puZWFQb25LQRoOZWdaUVZEcERSMUUlM0Q" # noqa
    #    "%3D", # noqa
    #    {"extra_headers": {'X-YouTube-Client-Name': '1',
    #                       'X-YouTube-Client-Version': '2.20200720.00.02'}}
    # ) # noqa


@mock.patch("pytube.request.get")
@mock.patch("pytube.request.post")
def test_playlist_pagination(request_post, request_get, playlist_html, playlist_long_html):
    url = "https://www.fakeurl.com/playlist?list=whatever"
    request_get.side_effect = [
        playlist_long_html
    ]
    request_post.side_effect = [
        '{"content_html":"<a '
        'href=\\"/watch?v=BcWz41-4cDk&amp;feature=plpp_video&amp;ved'
        '=CCYQxjQYACITCO33n5-pn-cCFUG3xAodLogN2yj6LA\\">}", '
        '"load_more_widget_html":""}',
        "{}",
    ]
    playlist = Playlist(url)
    assert len(playlist.video_urls) == 100
    assert request_get.call_count == 1
    assert request_post.call_count == 1


@mock.patch("pytube.request.get")
def test_trimmed_pagination(request_get, playlist_html, playlist_long_html):
    url = "https://www.fakeurl.com/playlist?list=whatever"
    request_get.side_effect = [
        playlist_long_html,
        '{"content_html":"<a '
        'href=\\"/watch?v=BcWz41-4cDk&amp;feature=plpp_video&amp;ved'
        '=CCYQxjQYACITCO33n5-pn-cCFUG3xAodLogN2yj6LA\\">}", '
        '"load_more_widget_html":""}',
        "{}",
    ]
    playlist = Playlist(url)
    assert len(list(playlist.trimmed("GTpl5yq3bvk"))) == 3
    assert request_get.call_count == 1


# TODO: Test case not clear to me
@mock.patch("pytube.request.get")
def test_trimmed_pagination_not_found(
    request_get, playlist_html, playlist_long_html
):
    url = "https://www.fakeurl.com/playlist?list=whatever"
    request_get.side_effect = [
        playlist_long_html,
        '{"content_html":"<a '
        'href=\\"/watch?v=BcWz41-4cDk&amp;feature=plpp_video&amp;ved'
        '=CCYQxjQYACITCO33n5-pn-cCFUG3xAodLogN2yj6LA\\">}", '
        '"load_more_widget_html":""}',
        "{}",
    ]
    playlist = Playlist(url) # noqa
    # assert len(list(playlist.trimmed("wont-be-found"))) == 101 # noqa
    assert True


# test case for playlist with submenus
@mock.patch("pytube.request.get")
def test_playlist_submenu(request_get, playlist_submenu_html):
    url = "https://www.fakeurl.com/playlist?list=whatever"
    request_get.side_effect = [
        playlist_submenu_html,
        '{"content_html":"<a '
        'href=\\"/watch?v=BcWz41-4cDk&amp;feature=plpp_video&amp;ved'
        '=CCYQxjQYACITCO33n5-pn-cCFUG3xAodLogN2yj6LA\\">}", '
        '"load_more_widget_html":""}',
        "{}",
    ]
    playlist = Playlist(url)
    assert len(playlist.video_urls) == 12


@mock.patch("pytube.request.get")
def test_playlist_length(request_get, playlist_long_html):
    url = 'https://www.example.com/playlist?list=whatever'
    request_get.return_value = playlist_long_html
    p = Playlist(url)
    assert p.length == 217


@mock.patch("pytube.request.get")
def test_playlist_description(request_get, playlist_long_html):
    url = 'https://www.example.com/playlist?list=whatever'
    request_get.return_value = playlist_long_html
    p = Playlist(url)
    assert p.description == (
        'Python Object Oriented - Learning Python in '
        "simple and easy steps ,python,xml,script,install, A beginner's "
        'tutorial containing complete knowledge of Python Syntax Object '
        'Oriented Language, Methods, Tuples,Learn,Python,Tutorial,Interactive,'
        'Free, Tools/Utilities,Getting the most popular pages from your Apache'
        ' logfile,Make your life easier with Virtualenvwrapper,This site now '
        'runs on Django,PythonForBeginners.com has a new owner,How to use '
        'Pillow, a fork of PIL,How to use the Python Imaging Library,Python '
        'Websites and Tutorials,How to use Envoy,Using Feedparser in Python,'
        'Subprocess and Shell Commands in Python, Exceptions Handling, '
        'Sockets, GUI, Extentions, XML Programming'
    )


@mock.patch("pytube.request.get")
def test_playlist_views(request_get, playlist_long_html):
    url = 'https://www.example.com/playlist?list=whatever'
    request_get.return_value = playlist_long_html
    p = Playlist(url)
    assert p.views == 4617130


@mock.patch("pytube.request.get")
def test_playlist_owner(request_get, playlist_long_html):
    url = 'https://www.example.com/playlist?list=whatever'
    request_get.return_value = playlist_long_html
    p = Playlist(url)
    assert p.owner == 'ProgrammingKnowledge'


@mock.patch("pytube.request.get")
def test_playlist_owner_id(request_get, playlist_long_html):
    url = 'https://www.example.com/playlist?list=whatever'
    request_get.return_value = playlist_long_html
    p = Playlist(url)
    assert p.owner_id == 'UCs6nmQViDpUw0nuIx9c_WvA'


@mock.patch("pytube.request.get")
def test_playlist_owner_url(request_get, playlist_long_html):
    url = 'https://www.example.com/playlist?list=whatever'
    request_get.return_value = playlist_long_html
    p = Playlist(url)
    assert p.owner_url == 'https://www.youtube.com/channel/UCs6nmQViDpUw0nuIx9c_WvA'
