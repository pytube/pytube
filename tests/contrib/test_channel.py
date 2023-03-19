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
        'https://www.youtube.com/watch?v=ZR4FHmypft4',
        'https://www.youtube.com/watch?v=oLu1U77qjSc',
        'https://www.youtube.com/watch?v=WDEdRmTCSs8',
        'https://www.youtube.com/watch?v=eZMV-fOPNLU',
        'https://www.youtube.com/watch?v=suE1vJPLDd8',
        'https://www.youtube.com/watch?v=RSjrUXECxW0',
        'https://www.youtube.com/watch?v=bj3BzUDX0S8',
        'https://www.youtube.com/watch?v=28gsNU-ylDI',
        'https://www.youtube.com/watch?v=sxbTqVgLLjQ',
        'https://www.youtube.com/watch?v=b165eo5SmA0',
    ]
    assert c.video_urls[:10] == first_ten


@mock.patch('pytube.request.get')
def test_channel_shorts_list(request_get, channel_shorts_html):
    request_get.return_value = channel_shorts_html
    c = Channel('https://www.youtube.com/@MLB/shorts')
    first_ten = [
        'https://www.youtube.com/watch?v=QkxWDZWLdPo',
        'https://www.youtube.com/watch?v=PFhXf8JNTlk',
        'https://www.youtube.com/watch?v=OYtlbyue5wk',
        'https://www.youtube.com/watch?v=1QrfBgCilcg',
        'https://www.youtube.com/watch?v=_h6ZxGGol5A',
        'https://www.youtube.com/watch?v=cf_cjXbIWuk',
        'https://www.youtube.com/watch?v=W_XX5yXjclI',
        'https://www.youtube.com/watch?v=X_yifl4zvMQ',
        'https://www.youtube.com/watch?v=HnYmQ1pNIxk',
        'https://www.youtube.com/watch?v=prBUfkJyY1E',
    ]
    assert c.video_urls[:10] == first_ten


@mock.patch('pytube.request.get')
def test_channel_live_list(request_get, channel_live_html):
    request_get.return_value = channel_live_html
    c = Channel('https://www.youtube.com/@MLB/streams')
    first_ten = [
        'https://www.youtube.com/watch?v=2u5Y3wadFc0',
        'https://www.youtube.com/watch?v=VS3QeZ823Lg',
        'https://www.youtube.com/watch?v=dtG7A1wJKLs',
        'https://www.youtube.com/watch?v=Kw2C3XOsFY0',
        'https://www.youtube.com/watch?v=yc2SSlcl2Ek',
        'https://www.youtube.com/watch?v=SyQ2UZ9EF-k',
        'https://www.youtube.com/watch?v=qjtzooqcjgA',
        'https://www.youtube.com/watch?v=rU-K8Im4KRw',
        'https://www.youtube.com/watch?v=cio1zhDHP-E',
        'https://www.youtube.com/watch?v=w72lUUiN__s',
    ]
    assert c.video_urls[:10] == first_ten


@mock.patch('pytube.request.get')
def test_videos_html(request_get, channel_videos_html):
    request_get.return_value = channel_videos_html

    c = Channel('https://www.youtube.com/c/ProgrammingKnowledge')
    assert c.html == channel_videos_html

# Because the Channel object subclasses the Playlist object, most of the tests
# are already taken care of by the Playlist test suite.
