# -*- coding: utf-8 -*-
import os
import random
from datetime import datetime
from unittest import mock
from unittest.mock import MagicMock, Mock

from pytube import request
from pytube import Stream


@mock.patch("pytube.streams.request")
def test_stream_to_buffer(mock_request, cipher_signature):
    # Given
    stream_bytes = iter(
        [
            bytes(os.urandom(8 * 1024)),
            bytes(os.urandom(8 * 1024)),
            bytes(os.urandom(8 * 1024)),
        ]
    )
    mock_request.stream.return_value = stream_bytes
    buffer = MagicMock()
    # When
    cipher_signature.streams[0].stream_to_buffer(buffer)
    # Then
    assert buffer.write.call_count == 3


@mock.patch(
    "pytube.streams.request.head", MagicMock(return_value={"content-length": "6796391"})
)
def test_filesize(cipher_signature):
    assert cipher_signature.streams[0].filesize == 6796391


@mock.patch(
    "pytube.streams.request.head", MagicMock(return_value={"content-length": "6796391"})
)
def test_filesize_approx(cipher_signature):
    stream = cipher_signature.streams[0]

    assert stream.filesize_approx == 28309811
    stream.bitrate = None
    assert stream.filesize_approx == 6796391


def test_default_filename(cipher_signature):
    expected = "YouTube Rewind 2019 For the Record  YouTubeRewind.mp4"
    stream = cipher_signature.streams[0]
    assert stream.default_filename == expected


def test_title(cipher_signature):
    expected = "title"
    cipher_signature.player_response = {"videoDetails": {"title": expected}}
    assert cipher_signature.title == expected


def test_expiration(cipher_signature):
    assert cipher_signature.streams[0].expiration == datetime(2020, 10, 30, 5, 39, 41)


def test_caption_tracks(presigned_video):
    assert len(presigned_video.caption_tracks) == 13


def test_captions(presigned_video):
    assert len(presigned_video.captions) == 13


def test_description(cipher_signature):
    expected = (
        "In 2018, we made something you didn’t like. "
        "For Rewind 2019, let’s see what you DID like.\n\n"
        "Celebrating the creators, music and moments "
        "that mattered most to you in 2019. \n\n"
        "To learn how the top lists in Rewind were generated: "
        "https://rewind.youtube/about\n\n"
        "Top lists featured the following channels:\n\n"
        "@1MILLION Dance Studio \n@A4 \n@Anaysa \n"
        "@Andymation \n@Ariana Grande \n@Awez Darbar \n"
        "@AzzyLand \n@Billie Eilish \n@Black Gryph0n \n"
        "@BLACKPINK \n@ChapkisDanceUSA \n@Daddy Yankee \n"
        "@David Dobrik \n@Dude Perfect \n@Felipe Neto \n"
        "@Fischer's-フィッシャーズ- \n@Galen Hooks \n@ibighit \n"
        "@James Charles \n@jeffreestar \n@Jelly \n@Kylie Jenner \n"
        "@LazarBeam \n@Lil Dicky \n@Lil Nas X \n@LOUD \n@LOUD Babi \n"
        "@LOUD Coringa \n@Magnet World \n@MrBeast \n"
        "@Nilson Izaias Papinho Oficial \n@Noah Schnapp\n"
        "@백종원의 요리비책 Paik's Cuisine \n@Pencilmation \n@PewDiePie \n"
        "@SethEverman \n@shane \n@Shawn Mendes \n@Team Naach \n"
        "@whinderssonnunes \n@워크맨-Workman \n@하루한끼 one meal a day \n\n"
        "To see the full list of featured channels in Rewind 2019, "
        "visit: https://rewind.youtube/about"
    )
    assert cipher_signature.description == expected


def test_rating(cipher_signature):
    assert cipher_signature.rating == 2.0860765


def test_length(cipher_signature):
    assert cipher_signature.length == 337


def test_views(cipher_signature):
    assert cipher_signature.views >= 108531745


@mock.patch(
    "pytube.streams.request.head", MagicMock(return_value={"content-length": "6796391"})
)
@mock.patch(
    "pytube.streams.request.stream",
    MagicMock(return_value=iter([str(random.getrandbits(8 * 1024))])),
)
def test_download(cipher_signature):
    with mock.patch("pytube.streams.open", mock.mock_open(), create=True):
        stream = cipher_signature.streams[0]
        stream.download()


@mock.patch(
    "pytube.streams.request.head", MagicMock(return_value={"content-length": "16384"})
)
@mock.patch(
    "pytube.streams.request.stream",
    MagicMock(return_value=iter([str(random.getrandbits(8 * 1024))])),
)
@mock.patch("pytube.streams.target_directory", MagicMock(return_value="/target"))
def test_download_with_prefix(cipher_signature):
    with mock.patch("pytube.streams.open", mock.mock_open(), create=True):
        stream = cipher_signature.streams[0]
        file_path = stream.download(filename_prefix="prefix")
        assert file_path == os.path.join(
            "/target",
            "prefixYouTube Rewind 2019 For the Record  YouTubeRewind.mp4"
        )


@mock.patch(
    "pytube.streams.request.head", MagicMock(return_value={"content-length": "16384"})
)
@mock.patch(
    "pytube.streams.request.stream",
    MagicMock(return_value=iter([str(random.getrandbits(8 * 1024))])),
)
@mock.patch("pytube.streams.target_directory", MagicMock(return_value="/target"))
def test_download_with_filename(cipher_signature):
    with mock.patch("pytube.streams.open", mock.mock_open(), create=True):
        stream = cipher_signature.streams[0]
        file_path = stream.download(filename="cool name bro")
        assert file_path == os.path.join(
            "/target",
            "cool name bro.mp4"
        )


@mock.patch(
    "pytube.streams.request.head", MagicMock(return_value={"content-length": "16384"})
)
@mock.patch(
    "pytube.streams.request.stream",
    MagicMock(return_value=iter([str(random.getrandbits(8 * 1024))])),
)
@mock.patch("pytube.streams.target_directory", MagicMock(return_value="/target"))
@mock.patch("os.path.isfile", MagicMock(return_value=True))
def test_download_with_existing(cipher_signature):
    with mock.patch("pytube.streams.open", mock.mock_open(), create=True):
        stream = cipher_signature.streams[0]
        os.path.getsize = Mock(return_value=stream.filesize)
        file_path = stream.download()
        assert file_path == os.path.join(
            "/target",
            "YouTube Rewind 2019 For the Record  YouTubeRewind.mp4"
        )
        assert not request.stream.called


@mock.patch(
    "pytube.streams.request.head", MagicMock(return_value={"content-length": "16384"})
)
@mock.patch(
    "pytube.streams.request.stream",
    MagicMock(return_value=iter([str(random.getrandbits(8 * 1024))])),
)
@mock.patch("pytube.streams.target_directory", MagicMock(return_value="/target"))
@mock.patch("os.path.isfile", MagicMock(return_value=True))
def test_download_with_existing_no_skip(cipher_signature):
    with mock.patch("pytube.streams.open", mock.mock_open(), create=True):
        stream = cipher_signature.streams[0]
        os.path.getsize = Mock(return_value=stream.filesize)
        file_path = stream.download(skip_existing=False)
        assert file_path == os.path.join(
            "/target",
            "YouTube Rewind 2019 For the Record  YouTubeRewind.mp4"
        )
        assert request.stream.called


def test_progressive_streams_return_includes_audio_track(cipher_signature):
    stream = cipher_signature.streams.filter(progressive=True)[0]
    assert stream.includes_audio_track


def test_progressive_streams_return_includes_video_track(cipher_signature):
    stream = cipher_signature.streams.filter(progressive=True)[0]
    assert stream.includes_video_track


@mock.patch(
    "pytube.streams.request.head", MagicMock(return_value={"content-length": "16384"})
)
@mock.patch(
    "pytube.streams.request.stream",
    MagicMock(return_value=iter([str(random.getrandbits(8 * 1024))])),
)
def test_on_progress_hook(cipher_signature):
    callback_fn = mock.MagicMock()
    cipher_signature.register_on_progress_callback(callback_fn)

    with mock.patch("pytube.streams.open", mock.mock_open(), create=True):
        stream = cipher_signature.streams[0]
        stream.download()
    assert callback_fn.called
    args, _ = callback_fn.call_args
    assert len(args) == 3
    stream, _, _ = args
    assert isinstance(stream, Stream)


@mock.patch(
    "pytube.streams.request.head", MagicMock(return_value={"content-length": "16384"})
)
@mock.patch(
    "pytube.streams.request.stream",
    MagicMock(return_value=iter([str(random.getrandbits(8 * 1024))])),
)
def test_on_complete_hook(cipher_signature):
    callback_fn = mock.MagicMock()
    cipher_signature.register_on_complete_callback(callback_fn)

    with mock.patch("pytube.streams.open", mock.mock_open(), create=True):
        stream = cipher_signature.streams[0]
        stream.download()
    assert callback_fn.called


def test_author(cipher_signature):
    expected = "Test author"
    cipher_signature.player_response = {"videoDetails": {"author": expected}}
    assert cipher_signature.author == expected

    expected = "unknown"
    cipher_signature.player_response = {}
    assert cipher_signature.author == expected


def test_thumbnail_when_in_details(cipher_signature):
    expected = "some url"
    cipher_signature.player_response = {
        "videoDetails": {"thumbnail": {"thumbnails": [{"url": expected}]}}
    }
    assert cipher_signature.thumbnail_url == expected


def test_thumbnail_when_not_in_details(cipher_signature):
    expected = "https://img.youtube.com/vi/2lAe1cqCOXo/maxresdefault.jpg"
    cipher_signature.player_response = {}
    assert cipher_signature.thumbnail_url == expected


def test_repr_for_audio_streams(cipher_signature):
    stream = str(cipher_signature.streams.filter(only_audio=True)[0])
    expected = (
        '<Stream: itag="140" mime_type="audio/mp4" abr="128kbps" '
        'acodec="mp4a.40.2" progressive="False" type="audio">'
    )
    assert stream == expected


def test_repr_for_video_streams(cipher_signature):
    stream = str(cipher_signature.streams.filter(only_video=True)[0])
    expected = (
        '<Stream: itag="137" mime_type="video/mp4" res="1080p" fps="30fps" '
        'vcodec="avc1.640028" progressive="False" type="video">'
    )
    assert stream == expected


def test_repr_for_progressive_streams(cipher_signature):
    stream = str(cipher_signature.streams.filter(progressive=True)[0])
    expected = (
        '<Stream: itag="18" mime_type="video/mp4" res="360p" fps="30fps" '
        'vcodec="avc1.42001E" acodec="mp4a.40.2" progressive="True" '
        'type="video">'
    )
    assert stream == expected


def test_repr_for_adaptive_streams(cipher_signature):
    stream = str(cipher_signature.streams.filter(adaptive=True)[0])
    expected = (
        '<Stream: itag="137" mime_type="video/mp4" res="1080p" fps="30fps" '
        'vcodec="avc1.640028" progressive="False" type="video">'
    )
    assert stream == expected
