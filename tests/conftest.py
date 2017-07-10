import mock
import pytest

from pytube import api


@pytest.fixture
def yt_video():
    url = 'http://www.youtube.com/watch?v=9bZkp7q19f0'
    mock_html = None
    mock_js = None

    with open('tests/mock_data/youtube_gangnam_style.html') as fh:
        mock_html = fh.read()

    with open('tests/mock_data/youtube_gangnam_style.js') as fh:
        mock_js = fh.read()

    with mock.patch('pytube.api.urlopen') as urlopen:
        urlopen.return_value.read.return_value = mock_html
        yt = api.YouTube()
        yt._js_cache = mock_js
        yt.from_url(url)
        return yt
