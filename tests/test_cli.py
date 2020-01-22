# -*- coding: utf-8 -*-
from unittest import mock
from unittest.mock import MagicMock, patch

import pytest

from pytube import cli, StreamQuery, Caption, CaptionQuery


@mock.patch("pytube.cli.YouTube")
def test_download_when_itag_not_found(youtube):
    youtube.streams = mock.Mock()
    youtube.streams.all.return_value = []
    youtube.streams.get_by_itag.return_value = None
    with pytest.raises(SystemExit):
        cli.download(youtube, 123)
    youtube.streams.get_by_itag.assert_called_with(123)


@mock.patch("pytube.cli.YouTube")
@mock.patch("pytube.Stream")
def test_download_when_itag_is_found(youtube, stream):
    stream.itag = 123
    youtube.streams = StreamQuery([stream])
    with patch.object(
        youtube.streams, "get_by_itag", wraps=youtube.streams.get_by_itag
    ) as wrapped_itag:
        cli.download(youtube, 123)
        wrapped_itag.assert_called_with(123)
    youtube.register_on_progress_callback.assert_called_with(cli.on_progress)
    stream.download.assert_called()


@mock.patch("pytube.cli.YouTube")
@mock.patch("pytube.Stream")
def test_display_stream(youtube, stream):
    stream.itag = 123
    stream.__repr__ = MagicMock(return_value="")
    youtube.streams = StreamQuery([stream])
    with patch.object(youtube.streams, "all", wraps=youtube.streams.all) as wrapped_all:
        cli.display_streams(youtube)
        wrapped_all.assert_called()
        stream.__repr__.assert_called()


@mock.patch("pytube.cli.YouTube")
def test_download_caption_with_none(youtube):
    caption = Caption(
        {"url": "url1", "name": {"simpleText": "name1"}, "languageCode": "en"}
    )
    youtube.captions = CaptionQuery([caption])
    with patch.object(
        youtube.captions, "all", wraps=youtube.captions.all
    ) as wrapped_all:
        cli.download_caption(youtube, None)
        wrapped_all.assert_called()


@mock.patch("pytube.cli.YouTube")
def test_download_caption_with_language_found(youtube):
    youtube.title = "video title"
    caption = Caption(
        {"url": "url1", "name": {"simpleText": "name1"}, "languageCode": "en"}
    )
    caption.download = MagicMock(return_value="file_path")
    youtube.captions = CaptionQuery([caption])
    cli.download_caption(youtube, "en")
    caption.download.assert_called_with(title="video title")


@mock.patch("pytube.cli.YouTube")
def test_download_caption_with_language_not_found(youtube):
    caption = Caption(
        {"url": "url1", "name": {"simpleText": "name1"}, "languageCode": "en"}
    )
    youtube.captions = CaptionQuery([caption])
    with patch.object(
        youtube.captions, "all", wraps=youtube.captions.all
    ) as wrapped_all:
        cli.download_caption(youtube, "blah")
        wrapped_all.assert_called()
