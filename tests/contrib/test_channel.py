from unittest import mock

from pytube import Channel


@mock.patch('pytube.request.get')
def test_init_with_url(request_get, channel_videos_html):
    request_get.return_value = channel_videos_html
    c = Channel('https://www.youtube.com/c/ProgrammingKnowledge/videos')
    assert c.channel_url == 'https://www.youtube.com/c/ProgrammingKnowledge'
    assert c.videos_url == f'{c.channel_url}/videos'
    assert c.playlists_url == f'{c.channel_url}/playlists'
    assert c.community_url == f'{c.channel_url}/community'
    assert c.featured_channels_url == f'{c.channel_url}/channels'
    assert c.about_url == f'{c.channel_url}/about'


@mock.patch('pytube.request.get')
def test_channel_uri(request_get, channel_videos_html):
    request_get.return_value = channel_videos_html

    c = Channel('https://www.youtube.com/c/ProgrammingKnowledge/videos')
    assert c.channel_uri == '/c/ProgrammingKnowledge'

    c = Channel('https://www.youtube.com/channel/UCs6nmQViDpUw0nuIx9c_WvA/videos')
    assert c.channel_uri == '/channel/UCs6nmQViDpUw0nuIx9c_WvA'


@mock.patch('pytube.request.get')
def test_channel_name(request_get, channel_videos_html):
    request_get.return_value = channel_videos_html

    c = Channel('https://www.youtube.com/c/ProgrammingKnowledge/videos')
    assert c.channel_name == 'ProgrammingKnowledge'


@mock.patch('pytube.request.get')
def test_channel_id(request_get, channel_videos_html):
    request_get.return_value = channel_videos_html

    c = Channel('https://www.youtube.com/c/ProgrammingKnowledge/videos')
    assert c.channel_id == 'UCs6nmQViDpUw0nuIx9c_WvA'


@mock.patch('pytube.request.get')
def test_channel_vanity_url(request_get, channel_videos_html):
    request_get.return_value = channel_videos_html

    c = Channel('https://www.youtube.com/c/ProgrammingKnowledge/videos')
    assert c.vanity_url == 'http://www.youtube.com/@ProgrammingKnowledge'


@mock.patch('pytube.request.get')
def test_channel_video_list(request_get, channel_videos_html):
    request_get.return_value = channel_videos_html

    c = Channel('https://www.youtube.com/c/ProgrammingKnowledge/videos')
    first_ten = [
        'https://www.youtube.com/watch?v=S19QqBytWC4',
        'https://www.youtube.com/watch?v=ah5M4Umuf9w',
        'https://www.youtube.com/watch?v=fclTFQQvQFQ',
        'https://www.youtube.com/watch?v=RphKLsy3tSc',
        'https://www.youtube.com/watch?v=ANE0uKeX-U0',
        'https://www.youtube.com/watch?v=SeOlDGN346E',
        'https://www.youtube.com/watch?v=Z2r46Gv7mp4',
        'https://www.youtube.com/watch?v=B3DndCaYgyM',
        'https://www.youtube.com/watch?v=KzS39YvFOv8',
        'https://www.youtube.com/watch?v=nkMTc_E2a_Q',
    ]
    assert c.video_urls[:10] == first_ten


@mock.patch('pytube.request.get')
def test_videos_html(request_get, channel_videos_html):
    request_get.return_value = channel_videos_html

    c = Channel('https://www.youtube.com/c/ProgrammingKnowledge')
    assert c.html == channel_videos_html

# Because the Channel object subclasses the Playlist object, most of the tests
# are already taken care of by the Playlist test suite.
