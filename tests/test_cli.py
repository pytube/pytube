import argparse
import logging
import os
from unittest import mock
from unittest.mock import MagicMock, patch

import pytest

from pytube import Caption, CaptionQuery, cli, StreamQuery
from pytube.exceptions import PytubeError

parse_args = cli._parse_args


@mock.patch("pytube.cli._parse_args")
def test_main_invalid_url(_parse_args):  # noqa: PT019
    parser = argparse.ArgumentParser()
    args = parse_args(parser, ["crikey",],)
    _parse_args.return_value = args
    with pytest.raises(SystemExit):
        cli.main()


@mock.patch("pytube.cli.display_streams")
@mock.patch("pytube.cli.YouTube")
def test_download_when_itag_not_found(youtube, display_streams):
    # Given
    youtube.streams = mock.Mock()
    youtube.streams.get_by_itag.return_value = None
    # When
    with pytest.raises(SystemExit):
        cli.download_by_itag(youtube, 123)
    # Then
    youtube.streams.get_by_itag.assert_called_with(123)
    display_streams.assert_called_with(youtube)


@mock.patch("pytube.cli.YouTube")
@mock.patch("pytube.Stream")
def test_download_when_itag_is_found(youtube, stream):
    stream.itag = 123
    stream.exists_at_path.return_value = False
    youtube.streams = StreamQuery([stream])
    with patch.object(
        youtube.streams, "get_by_itag", wraps=youtube.streams.get_by_itag
    ) as wrapped_itag:
        cli.download_by_itag(youtube, 123)
        wrapped_itag.assert_called_with(123)
    youtube.register_on_progress_callback.assert_called_with(cli.on_progress)
    stream.download.assert_called()


@mock.patch("pytube.cli.YouTube")
@mock.patch("pytube.Stream")
def test_display_stream(youtube, stream):
    # Given
    stream.itag = 123
    stream.__repr__ = MagicMock(return_value="")
    youtube.streams = StreamQuery([stream])
    # When
    cli.display_streams(youtube)
    # Then
    stream.__repr__.assert_called()


@mock.patch("pytube.cli._print_available_captions")
@mock.patch("pytube.cli.YouTube")
def test_download_caption_with_none(youtube, print_available):
    # Given
    caption = Caption(
        {"url": "url1", "name": {"simpleText": "name1"}, "languageCode": "en", "vssId": ".en"}
    )
    youtube.captions = CaptionQuery([caption])
    # When
    cli.download_caption(youtube, None)
    # Then
    print_available.assert_called_with(youtube.captions)


@mock.patch("pytube.cli.YouTube")
def test_download_caption_with_language_found(youtube):
    youtube.title = "video title"
    caption = Caption(
        {"url": "url1", "name": {"simpleText": "name1"}, "languageCode": "en", "vssId": ".en"}
    )
    caption.download = MagicMock(return_value="file_path")
    youtube.captions = CaptionQuery([caption])
    cli.download_caption(youtube, "en")
    caption.download.assert_called_with(title="video title", output_path=None)


@mock.patch("pytube.cli._print_available_captions")
@mock.patch("pytube.cli.YouTube")
def test_download_caption_with_lang_not_found(youtube, print_available):
    # Given
    caption = Caption(
        {"url": "url1", "name": {"simpleText": "name1"}, "languageCode": "en", "vssId": ".en"}
    )
    youtube.captions = CaptionQuery([caption])
    # When
    cli.download_caption(youtube, "blah")
    # Then
    print_available.assert_called_with(youtube.captions)


def test_print_available_captions(capsys):
    # Given
    caption1 = Caption(
        {"url": "url1", "name": {"simpleText": "name1"}, "languageCode": "en", "vssId": ".en"}
    )
    caption2 = Caption(
        {"url": "url2", "name": {"simpleText": "name2"}, "languageCode": "fr", "vssId": ".fr"}
    )
    query = CaptionQuery([caption1, caption2])
    # When
    cli._print_available_captions(query)
    # Then
    captured = capsys.readouterr()
    assert captured.out == "Available caption codes are: en, fr\n"


def test_display_progress_bar(capsys):
    cli.display_progress_bar(bytes_received=25, filesize=100, scale=0.55)
    out, _ = capsys.readouterr()
    assert "25.0%" in out


@mock.patch("pytube.Stream")
def test_on_progress(stream):
    stream.filesize = 10
    cli.display_progress_bar = MagicMock()
    cli.on_progress(stream, "", 7)
    cli.display_progress_bar.assert_called_once_with(3, 10)


def test_parse_args_falsey():
    parser = argparse.ArgumentParser()
    args = cli._parse_args(parser, ["http://youtube.com/watch?v=9bZkp7q19f0"])
    assert args.url == "http://youtube.com/watch?v=9bZkp7q19f0"
    assert args.build_playback_report is False
    assert args.itag is None
    assert args.list is False
    assert args.verbose is False


def test_parse_args_truthy():
    parser = argparse.ArgumentParser()
    args = cli._parse_args(
        parser,
        [
            "http://youtube.com/watch?v=9bZkp7q19f0",
            "--build-playback-report",
            "-c",
            "en",
            "-l",
            "--itag=10",
            "-vvv",
        ],
    )
    assert args.url == "http://youtube.com/watch?v=9bZkp7q19f0"
    assert args.build_playback_report is True
    assert args.itag == 10
    assert args.list is True
    assert args.verbose is True


@mock.patch("pytube.cli.setup_logger", return_value=None)
def test_main_logging_setup(setup_logger):
    # Given
    parser = argparse.ArgumentParser()
    args = parse_args(parser, ["http://fakeurl", "-v"])
    cli._parse_args = MagicMock(return_value=args)
    # When
    with pytest.raises(SystemExit):
        cli.main()
    # Then
    setup_logger.assert_called_with(logging.DEBUG, log_filename=None)


@mock.patch("pytube.cli.YouTube", return_value=None)
def test_main_download_by_itag(youtube):
    parser = argparse.ArgumentParser()
    args = parse_args(
        parser, ["http://youtube.com/watch?v=9bZkp7q19f0", "--itag=10"]
    )
    cli._parse_args = MagicMock(return_value=args)
    cli.download_by_itag = MagicMock()
    cli.main()
    youtube.assert_called()
    cli.download_by_itag.assert_called()


@mock.patch("pytube.cli.YouTube", return_value=None)
def test_main_build_playback_report(youtube):
    parser = argparse.ArgumentParser()
    args = parse_args(
        parser,
        ["http://youtube.com/watch?v=9bZkp7q19f0", "--build-playback-report"],
    )
    cli._parse_args = MagicMock(return_value=args)
    cli.build_playback_report = MagicMock()
    cli.main()
    youtube.assert_called()
    cli.build_playback_report.assert_called()


@mock.patch("pytube.cli.YouTube", return_value=None)
def test_main_display_streams(youtube):
    parser = argparse.ArgumentParser()
    args = parse_args(parser, ["http://youtube.com/watch?v=9bZkp7q19f0", "-l"])
    cli._parse_args = MagicMock(return_value=args)
    cli.display_streams = MagicMock()
    cli.main()
    youtube.assert_called()
    cli.display_streams.assert_called()


@mock.patch("pytube.cli.YouTube", return_value=None)
def test_main_download_caption(youtube):
    parser = argparse.ArgumentParser()
    args = parse_args(parser, ["http://youtube.com/watch?v=9bZkp7q19f0", "-c", "en"])
    cli._parse_args = MagicMock(return_value=args)
    cli.download_caption = MagicMock()
    cli.main()
    youtube.assert_called()
    cli.download_caption.assert_called()


@mock.patch("pytube.cli.YouTube", return_value=None)
@mock.patch("pytube.cli.download_by_resolution")
def test_download_by_resolution_flag(youtube, download_by_resolution):
    parser = argparse.ArgumentParser()
    args = parse_args(
        parser, ["http://youtube.com/watch?v=9bZkp7q19f0", "-r", "320p"]
    )
    cli._parse_args = MagicMock(return_value=args)
    cli.main()
    youtube.assert_called()
    download_by_resolution.assert_called()


@mock.patch("pytube.cli.YouTube")
@mock.patch("pytube.cli.Playlist")
@mock.patch("pytube.cli._perform_args_on_youtube")
def test_download_with_playlist(perform_args_on_youtube, playlist, youtube):
    # Given
    cli.safe_filename = MagicMock(return_value="safe_title")
    parser = argparse.ArgumentParser()
    args = parse_args(parser, ["https://www.youtube.com/playlist?list=PLyn"])
    cli._parse_args = MagicMock(return_value=args)
    videos = [youtube]
    playlist_instance = playlist.return_value
    playlist_instance.videos = videos
    # When
    cli.main()
    # Then
    playlist.assert_called()
    perform_args_on_youtube.assert_called_with(youtube, args)


@mock.patch("pytube.cli.YouTube")
@mock.patch("pytube.cli.Playlist")
@mock.patch("pytube.cli._perform_args_on_youtube")
def test_download_with_playlist_video_error(
    perform_args_on_youtube, playlist, youtube, capsys
):
    # Given
    cli.safe_filename = MagicMock(return_value="safe_title")
    parser = argparse.ArgumentParser()
    args = parse_args(parser, ["https://www.youtube.com/playlist?list=PLyn"])
    cli._parse_args = MagicMock(return_value=args)
    videos = [youtube]
    playlist_instance = playlist.return_value
    playlist_instance.videos = videos
    perform_args_on_youtube.side_effect = PytubeError()
    # When
    cli.main()
    # Then
    playlist.assert_called()
    captured = capsys.readouterr()
    assert "There was an error with video" in captured.out


@mock.patch("pytube.cli.YouTube")
@mock.patch("pytube.StreamQuery")
@mock.patch("pytube.Stream")
@mock.patch("pytube.cli._download")
def test_download_by_resolution(download, stream, stream_query, youtube):
    # Given
    stream_query.get_by_resolution.return_value = stream
    youtube.streams = stream_query
    # When
    cli.download_by_resolution(
        youtube=youtube, resolution="320p", target="test_target"
    )
    # Then
    download.assert_called_with(stream, target="test_target")


@mock.patch("pytube.cli.YouTube")
@mock.patch("pytube.StreamQuery")
@mock.patch("pytube.cli._download")
def test_download_by_resolution_not_exists(download, stream_query, youtube):
    stream_query.get_by_resolution.return_value = None
    youtube.streams = stream_query
    with pytest.raises(SystemExit):
        cli.download_by_resolution(
            youtube=youtube, resolution="DOESNT EXIST", target="test_target"
        )
    download.assert_not_called()


@mock.patch("pytube.Stream")
def test_download_stream_file_exists(stream, capsys):
    # Given
    stream.exists_at_path.return_value = True
    # When
    cli._download(stream=stream)
    # Then
    captured = capsys.readouterr()
    assert "Already downloaded at" in captured.out
    stream.download.assert_not_called()


@mock.patch("pytube.cli.YouTube")
@mock.patch("pytube.cli.ffmpeg_process")
def test_perform_args_should_ffmpeg_process(ffmpeg_process, youtube):
    # Given
    parser = argparse.ArgumentParser()
    args = parse_args(
        parser, ["http://youtube.com/watch?v=9bZkp7q19f0", "-f", "best"]
    )
    cli._parse_args = MagicMock(return_value=args)
    # When
    cli._perform_args_on_youtube(youtube, args)
    # Then
    ffmpeg_process.assert_called_with(
        youtube=youtube, resolution="best", target=None
    )


@mock.patch("pytube.cli.YouTube")
@mock.patch("pytube.cli._ffmpeg_downloader")
def test_ffmpeg_process_best_should_download(  # noqa: PT019
    _ffmpeg_downloader, youtube
):
    # Given
    target = "/target"
    streams = MagicMock()
    youtube.streams = streams
    video_stream = MagicMock()
    streams.filter.return_value.order_by.return_value.last.return_value = (
        video_stream
    )
    audio_stream = MagicMock()
    streams.get_audio_only.return_value = audio_stream
    # When
    cli.ffmpeg_process(youtube, "best", target)
    # Then
    _ffmpeg_downloader.assert_called_with(
        audio_stream=audio_stream, video_stream=video_stream, target=target
    )


@mock.patch("pytube.cli.YouTube")
@mock.patch("pytube.cli._ffmpeg_downloader")
def test_ffmpeg_process_res_should_download(  # noqa: PT019
    _ffmpeg_downloader, youtube
):
    # Given
    target = "/target"
    streams = MagicMock()
    youtube.streams = streams
    video_stream = MagicMock()
    streams.filter.return_value.first.return_value = video_stream
    audio_stream = MagicMock()
    streams.get_audio_only.return_value = audio_stream
    # When
    cli.ffmpeg_process(youtube, "XYZp", target)
    # Then
    _ffmpeg_downloader.assert_called_with(
        audio_stream=audio_stream, video_stream=video_stream, target=target
    )


@mock.patch("pytube.cli.YouTube")
@mock.patch("pytube.cli._ffmpeg_downloader")
def test_ffmpeg_process_res_none_should_not_download(  # noqa: PT019
    _ffmpeg_downloader, youtube
):
    # Given
    target = "/target"
    streams = MagicMock()
    youtube.streams = streams
    streams.filter.return_value.first.return_value = None
    audio_stream = MagicMock()
    streams.get_audio_only.return_value = audio_stream
    # When
    with pytest.raises(SystemExit):
        cli.ffmpeg_process(youtube, "XYZp", target)
    # Then
    _ffmpeg_downloader.assert_not_called()


@mock.patch("pytube.cli.YouTube")
@mock.patch("pytube.cli._ffmpeg_downloader")
def test_ffmpeg_process_audio_none_should_fallback_download(  # noqa: PT019
    _ffmpeg_downloader, youtube
):
    # Given
    target = "/target"
    streams = MagicMock()
    youtube.streams = streams
    stream = MagicMock()
    streams.filter.return_value.order_by.return_value.last.return_value = stream
    streams.get_audio_only.return_value = None
    # When
    cli.ffmpeg_process(youtube, "best", target)
    # Then
    _ffmpeg_downloader.assert_called_with(
        audio_stream=stream, video_stream=stream, target=target
    )


@mock.patch("pytube.cli.YouTube")
@mock.patch("pytube.cli._ffmpeg_downloader")
def test_ffmpeg_process_audio_fallback_none_should_exit(  # noqa: PT019
    _ffmpeg_downloader, youtube
):
    # Given
    target = "/target"
    streams = MagicMock()
    youtube.streams = streams
    stream = MagicMock()
    streams.filter.return_value.order_by.return_value.last.side_effect = [
        stream,
        stream,
        None,
    ]
    streams.get_audio_only.return_value = None
    # When
    with pytest.raises(SystemExit):
        cli.ffmpeg_process(youtube, "best", target)
    # Then
    _ffmpeg_downloader.assert_not_called()


@mock.patch("pytube.cli.os.unlink", return_value=None)
@mock.patch("pytube.cli.subprocess.run", return_value=None)
@mock.patch("pytube.cli._download", return_value=None)
@mock.patch("pytube.cli._unique_name", return_value=None)
def test_ffmpeg_downloader(unique_name, download, run, unlink):
    # Given
    target = "target"
    audio_stream = MagicMock()
    video_stream = MagicMock()
    video_stream.id = "video_id"
    audio_stream.subtype = "audio_subtype"
    video_stream.subtype = "video_subtype"
    unique_name.side_effect = ["video_name", "audio_name"]

    # When
    cli._ffmpeg_downloader(
        audio_stream=audio_stream, video_stream=video_stream, target=target
    )
    # Then
    download.assert_called()
    run.assert_called_with(
        [
            "ffmpeg",
            "-i",
            os.path.join("target", "video_name.video_subtype"),
            "-i",
            os.path.join("target", "audio_name.audio_subtype"),
            "-codec",
            "copy",
            os.path.join("target", "safe_title.video_subtype"),
        ]
    )
    unlink.assert_called()


@mock.patch("pytube.cli.download_audio")
@mock.patch("pytube.cli.YouTube.__init__", return_value=None)
def test_download_audio_args(youtube, download_audio):
    # Given
    parser = argparse.ArgumentParser()
    args = parse_args(
        parser, ["http://youtube.com/watch?v=9bZkp7q19f0", "-a", "mp4"]
    )
    cli._parse_args = MagicMock(return_value=args)
    # When
    cli.main()
    # Then
    youtube.assert_called()
    download_audio.assert_called()


@mock.patch("pytube.cli._download")
@mock.patch("pytube.cli.YouTube")
def test_download_audio(youtube, download):
    # Given
    youtube_instance = youtube.return_value
    audio_stream = MagicMock()
    youtube_instance.streams.filter.return_value.order_by.return_value.last.return_value = (
        audio_stream
    )
    # When
    cli.download_audio(youtube_instance, "filetype", "target")
    # Then
    download.assert_called_with(audio_stream, target="target")


@mock.patch("pytube.cli._download")
@mock.patch("pytube.cli.YouTube")
def test_download_audio_none(youtube, download):
    # Given
    youtube_instance = youtube.return_value
    youtube_instance.streams.filter.return_value.order_by.return_value.last.return_value = (
        None
    )
    # When
    with pytest.raises(SystemExit):
        cli.download_audio(youtube_instance, "filetype", "target")
    # Then
    download.assert_not_called()


@mock.patch("pytube.cli.YouTube.__init__", return_value=None)
def test_perform_args_on_youtube(youtube):
    parser = argparse.ArgumentParser()
    args = parse_args(parser, ["http://youtube.com/watch?v=9bZkp7q19f0"])
    cli._parse_args = MagicMock(return_value=args)
    cli._perform_args_on_youtube = MagicMock()
    cli.main()
    youtube.assert_called()
    cli._perform_args_on_youtube.assert_called()


@mock.patch("pytube.cli.os.path.exists", return_value=False)
def test_unique_name(path_exists):
    assert (
        cli._unique_name("base", "subtype", "video", "target") == "base_video_0"
    )


@mock.patch("pytube.cli.os.path.exists")
def test_unique_name_counter(path_exists):
    path_exists.side_effect = [True, False]
    assert (
        cli._unique_name("base", "subtype", "video", "target") == "base_video_1"
    )
