# -*- coding: utf-8 -*-
import argparse
from unittest import mock
from unittest.mock import MagicMock, patch

import pytest

from pytube import cli, StreamQuery, Caption, CaptionQuery

parse_args = cli._parse_args


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


@mock.patch("pytube.Stream")
@mock.patch("io.BufferedWriter")
def test_on_progress(stream, writer):
    stream.filesize = 10
    cli.display_progress_bar = MagicMock()
    cli.on_progress(stream, "", writer, 7)
    cli.display_progress_bar.assert_called_once_with(3, 10)


def test_parse_args_falsey():
    parser = argparse.ArgumentParser()
    args = cli._parse_args(parser, ["urlhere"])
    assert args.url == "urlhere"
    assert args.build_playback_report is False
    assert args.itag is None
    assert args.list is False
    assert args.verbosity == 0


def test_parse_args_truthy():
    parser = argparse.ArgumentParser()
    args = cli._parse_args(
        parser, ["urlhere", "--build-playback-report", "-c", "en", "-l", "--itag=10"]
    )
    assert args.url == "urlhere"
    assert args.build_playback_report is True
    assert args.itag == 10
    assert args.list is True


@mock.patch("pytube.cli.YouTube.__init__", return_value=None)
def test_main_download(youtube):
    parser = argparse.ArgumentParser()
    args = parse_args(parser, ["urlhere", "--itag=10"])
    cli._parse_args = MagicMock(return_value=args)
    cli.download = MagicMock()
    cli.main()
    youtube.assert_called()
    cli.download.assert_called()


@mock.patch("pytube.cli.YouTube.__init__", return_value=None)
def test_main_build_playback_report(youtube):
    parser = argparse.ArgumentParser()
    args = parse_args(parser, ["urlhere", "--build-playback-report"])
    cli._parse_args = MagicMock(return_value=args)
    cli.build_playback_report = MagicMock()
    cli.main()
    youtube.assert_called()
    cli.build_playback_report.assert_called()


@mock.patch("pytube.cli.YouTube.__init__", return_value=None)
def test_main_display_streams(youtube):
    parser = argparse.ArgumentParser()
    args = parse_args(parser, ["urlhere", "-l"])
    cli._parse_args = MagicMock(return_value=args)
    cli.display_streams = MagicMock()
    cli.main()
    youtube.assert_called()
    cli.display_streams.assert_called()


@mock.patch("pytube.cli.YouTube.__init__", return_value=None)
def test_main_download_caption(youtube):
    parser = argparse.ArgumentParser()
    args = parse_args(parser, ["urlhere", "-c"])
    cli._parse_args = MagicMock(return_value=args)
    cli.download_caption = MagicMock()
    cli.main()
    youtube.assert_called()
    cli.download_caption.assert_called()
