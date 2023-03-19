import itertools

import pytest

from pytube import Channel

CHANNEL_URL = 'https://www.youtube.com/@MLB'


@pytest.fixture
def channel():
    """Channel instance."""
    return Channel(CHANNEL_URL)


@pytest.mark.xfail(reason='Broken Channel Attributes')
def test_channel_info_broken(channel):
    broken_attrs = ('last_updated', 'title', 'description', 'length')

    errors = {}
    for attr in broken_attrs:
        try:
            assert getattr(channel, attr)
        except Exception as err:
            errors[attr] = err

    channel = None  # Reset channel to avoid pytest converting it to a string and fetching all videos.
    assert sorted(broken_attrs) == sorted(errors)
    message = 'Unexpected errors for attributes:'
    for attr in errors:
        message += f'\n{attr}: {repr(errors[attr])}'

    assert len(errors) == 0, message


def test_channel(channel):
    size_attrs = ('videos', 'shorts', 'live')
    attrs = ('channel_id', 'channel_name') + size_attrs

    errors = {}
    for attr in attrs:
        try:
            if attr in size_attrs:
                value = list(itertools.islice(getattr(channel, attr), 10))
            else:
                value = getattr(channel, attr)
            assert value
        except Exception as err:
            errors[attr] = err
    channel = None  # Reset channel to avoid pytest converting it to a string and fetching all videos.
    if errors:
        message = f'Unexpected errors for attributes: {errors}'
        for attr in errors:
            message += f'\n{attr}: {errors[attr]}'
        assert errors == [], message


def test_video_stream(channel):
    videos = list(itertools.islice(channel.videos, 3))
    assert len(videos)
    youtube_instance_attrs = ('video_id', 'publish_date', 'watch_url')
    stream_attrs = ('mime_type',)
    channel = None  # Reset channel to avoid pytest converting it to a string and fetching all videos.
    for yt in videos:
        for attr in youtube_instance_attrs:
            assert getattr(yt, attr)
        stream = yt.streams.first()
        for attr in stream_attrs:
            assert getattr(stream, attr)
