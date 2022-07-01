"""Reusable dependency injected testing components."""
import gzip
import json
import os
import pytest
from unittest import mock

from pytube import YouTube


def load_playback_file(filename):
    """Load a gzip json playback file."""
    cur_fp = os.path.realpath(__file__)
    cur_dir = os.path.dirname(cur_fp)
    fp = os.path.join(cur_dir, "mocks", filename)
    with gzip.open(fp, "rb") as fh:
        content = fh.read().decode("utf-8")
        return json.loads(content)


@mock.patch('pytube.request.urlopen')
def load_and_init_from_playback_file(filename, mock_urlopen):
    """Load a gzip json playback file and create YouTube instance."""
    pb = load_playback_file(filename)

    # Mock the responses to YouTube
    mock_url_open_object = mock.Mock()
    mock_url_open_object.read.side_effect = [
        pb['watch_html'].encode('utf-8'),
        pb['js'].encode('utf-8')
    ]
    mock_urlopen.return_value = mock_url_open_object

    # Pytest caches this result, so we can speed up the tests
    #  by causing the object to fetch all the relevant information
    #  it needs. Previously, this was handled by prefetch_init()
    #  and descramble(), but this functionality has since been
    #  deferred
    v = YouTube(pb["url"])
    v.watch_html
    v._vid_info = pb['vid_info']
    v.js
    v.fmt_streams
    return v


@pytest.fixture
def cipher_signature():
    """Youtube instance initialized with video id 2lAe1cqCOXo."""
    filename = "yt-video-2lAe1cqCOXo-html.json.gz"
    return load_and_init_from_playback_file(filename)


@pytest.fixture
def presigned_video():
    """Youtube instance initialized with video id QRS8MkLhQmM."""
    filename = "yt-video-QRS8MkLhQmM-html.json.gz"
    return load_and_init_from_playback_file(filename)


@pytest.fixture
def age_restricted():
    """Youtube instance initialized with video id irauhITDrsE."""
    filename = "yt-video-irauhITDrsE-html.json.gz"
    return load_playback_file(filename)


@pytest.fixture
def private():
    """Youtube instance initialized with video id m8uHb5jIGN8."""
    filename = "yt-video-m8uHb5jIGN8-html.json.gz"
    return load_playback_file(filename)


@pytest.fixture
def missing_recording():
    """Youtube instance initialized with video id 5YceQ8YqYMc."""
    filename = "yt-video-5YceQ8YqYMc-html.json.gz"
    return load_playback_file(filename)


@pytest.fixture
def playlist_html():
    """Youtube playlist HTML loaded on 2020-01-25 from
    https://www.youtube.com/playlist?list=PLzMcBGfZo4-mP7qA9cagf68V06sko5otr
    """
    file_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "mocks",
        "playlist.html.gz",
    )
    with gzip.open(file_path, "rb") as f:
        return f.read().decode("utf-8")


@pytest.fixture
def playlist_long_html():
    """Youtube playlist HTML loaded on 2020-01-25 from
    https://www.youtube.com/playlist?list=PLzMcBGfZo4-mP7qA9cagf68V06sko5otr
    """
    file_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "mocks",
        "playlist_long.html.gz",
    )
    with gzip.open(file_path, "rb") as f:
        return f.read().decode("utf-8")


@pytest.fixture
def playlist_submenu_html():
    """Youtube playlist HTML loaded on 2020-01-24 from
    https://www.youtube.com/playlist?list=PLZHQObOWTQDMsr9K-rj53DwVRMYO3t5Yr
    """
    file_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "mocks",
        "playlist_submenu.html.gz",
    )
    with gzip.open(file_path, "rb") as f:
        return f.read().decode("utf-8")


@pytest.fixture
def stream_dict():
    """Youtube instance initialized with video id WXxV9g7lsFE."""
    file_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "mocks",
        "yt-video-WXxV9g7lsFE-html.json.gz",
    )
    with gzip.open(file_path, "rb") as f:
        content = json.loads(f.read().decode("utf-8"))
        return content['watch_html']


@pytest.fixture
def channel_videos_html():
    """Youtube channel HTML loaded on 2021-05-05 from
    https://www.youtube.com/c/ProgrammingKnowledge/videos
    """
    file_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "mocks",
        "channel-videos.html.gz",
    )
    with gzip.open(file_path, 'rb') as f:
        return f.read().decode('utf-8')


@pytest.fixture
def base_js():
    """Youtube base.js files retrieved on 2022-02-04 and 2022-04-15
    from https://www.youtube.com/watch?v=vmzxpUsN0uA and
    https://www.youtube.com/watch?v=Y4-GSFKZmEg respectively
    """
    base_js_files = []
    for file in ["base.js-2022-02-04.gz", "base.js-2022-04-15.gz"]:
        file_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "mocks",
            file,
        )
        with gzip.open(file_path, 'rb') as f:
            base_js_files.append(f.read().decode('utf-8'))
    return base_js_files
