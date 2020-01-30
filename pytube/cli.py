#!/usr/bin/env python3
"""A simple command line application to download youtube videos."""

import argparse
import datetime as dt
import gzip
import json
import logging
import os
import shutil
import sys
import subprocess
from io import BufferedWriter
from typing import Any, Optional, List
from pathlib import Path

from pytube import __version__, CaptionQuery, Stream, Playlist
from pytube import YouTube
from pytube.exceptions import PytubeError
from pytube.helpers import safe_filename

logger = logging.getLogger(__name__)


def main():
    """Command line application to download youtube videos."""
    # noinspection PyTypeChecker
    parser = argparse.ArgumentParser(description=main.__doc__)
    args = _parse_args(parser)
    logging.getLogger().setLevel(max(3 - args.verbosity, 0) * 10)

    if not args.url or "youtu" not in args.url:
        parser.print_help()
        sys.exit(1)

    if "/playlist" in args.url:
        print("Loading playlist...")
        playlist = Playlist(args.url)
        if not args.target:
            args.target = safe_filename(playlist.title())
        for youtube_video in playlist.videos:
            try:
                _perform_args_on_youtube(youtube_video, args)
            except PytubeError as e:
                print(f"There was an error with video: {youtube_video}")
                print(e)
    else:
        print("Loading video...")
        youtube = YouTube(args.url)
        _perform_args_on_youtube(youtube, args)


def _perform_args_on_youtube(youtube: YouTube, args: argparse.Namespace) -> None:
    if args.list:
        display_streams(youtube)
    if args.build_playback_report:
        build_playback_report(youtube)
    if args.itag:
        download_by_itag(youtube=youtube, itag=args.itag, target=args.target)
    if hasattr(args, "caption_code"):
        download_caption(
            youtube=youtube, lang_code=args.caption_code, target=args.target
        )
    if args.resolution:
        download_by_resolution(
            youtube=youtube, resolution=args.resolution, target=args.target
        )
    if args.audio:
        download_audio(youtube=youtube, filetype=args.audio, target=args.target)
    if args.ffmpeg:
        ffmpeg_process(youtube=youtube, resolution=args.ffmpeg, target=args.target)


def _parse_args(
    parser: argparse.ArgumentParser, args: Optional[List] = None
) -> argparse.Namespace:
    parser.add_argument("url", help="The YouTube /watch or /playlist url", nargs="?")
    parser.add_argument(
        "--version", action="version", version="%(prog)s " + __version__,
    )
    parser.add_argument(
        "--itag", type=int, help="The itag for the desired stream",
    )
    parser.add_argument(
        "-r", "--resolution", type=str, help="The resolution for the desired stream",
    )
    parser.add_argument(
        "-l",
        "--list",
        action="store_true",
        help=(
            "The list option causes pytube cli to return a list of streams "
            "available to download"
        ),
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        dest="verbosity",
        help="Verbosity level",
    )
    parser.add_argument(
        "--build-playback-report",
        action="store_true",
        help="Save the html and js to disk",
    )
    parser.add_argument(
        "-c",
        "--caption-code",
        type=str,
        default=argparse.SUPPRESS,
        nargs="?",
        help=(
            "Download srt captions for given language code. "
            "Prints available language codes if no argument given"
        ),
    )
    parser.add_argument(
        "-t",
        "--target",
        help=(
            "The output directory for the downloaded stream. "
            "Default is current working directory"
        ),
    )
    parser.add_argument(
        "-a",
        "--audio",
        const="mp4",
        nargs="?",
        help=(
            "Download the audio for a given URL at the highest bitrate available"
            "Defaults to mp4 format if none is specified"
        )
    )
    parser.add_argument(
        "-f",
        "--ffmpeg",
        const="best",
        nargs="?",
        help=(
            "If no resolution provided, will download the highest quality video and\
            audio streams avaiable, will try to download mp4 but will then download\
            a webm if none are found"
            )
        )

    return parser.parse_args(args)


def build_playback_report(youtube: YouTube) -> None:
    """Serialize the request data to json for offline debugging.

    :param YouTube youtube:
        A YouTube object.
    """
    ts = int(dt.datetime.utcnow().timestamp())
    fp = os.path.join(os.getcwd(), f"yt-video-{youtube.video_id}-{ts}.json.gz")

    js = youtube.js
    watch_html = youtube.watch_html
    vid_info = youtube.vid_info

    with gzip.open(fp, "wb") as fh:
        fh.write(
            json.dumps(
                {
                    "url": youtube.watch_url,
                    "js": js,
                    "watch_html": watch_html,
                    "video_info": vid_info,
                }
            ).encode("utf8"),
        )


def display_progress_bar(
    bytes_received: int, filesize: int, ch: str = "█", scale: float = 0.55
) -> None:
    """Display a simple, pretty progress bar.

    Example:
    ~~~~~~~~
    PSY - GANGNAM STYLE(강남스타일) MV.mp4
    ↳ |███████████████████████████████████████| 100.0%

    :param int bytes_received:
        The delta between the total file size (bytes) and bytes already
        written to disk.
    :param int filesize:
        File size of the media stream in bytes.
    :param str ch:
        Character to use for presenting progress segment.
    :param float scale:
        Scale multiplier to reduce progress bar size.

    """
    columns = shutil.get_terminal_size().columns
    max_width = int(columns * scale)

    filled = int(round(max_width * bytes_received / float(filesize)))
    remaining = max_width - filled
    progress_bar = ch * filled + " " * remaining
    percent = round(100.0 * bytes_received / float(filesize), 1)
    text = f" ↳ |{progress_bar}| {percent}%\r"
    sys.stdout.write(text)
    sys.stdout.flush()


# noinspection PyUnusedLocal
def on_progress(
    stream: Any, chunk: Any, file_handler: BufferedWriter, bytes_remaining: int
) -> None:
    filesize = stream.filesize
    bytes_received = filesize - bytes_remaining
    display_progress_bar(bytes_received, filesize)


def _download(
    stream: Stream, target: Optional[str] = None, filename: Optional[str] = None
) -> None:
    filesize_megabytes = stream.filesize // 1048576
    print(f"{stream.default_filename} | {filesize_megabytes} MB")
    stream.download(output_path=target, filename=filename)
    sys.stdout.write("\n")


def unique_name(base: str, subtype: str, video_audio: str, target: Path) -> str:
    """
    Given a base name, the file format, and the target directory, will generate 
    a filename unique for that directory and file format.
    :param str base:
        The given base-name, which the function uses to create the unique name.
    :param str subtype:
        The filetype of the video which will be downloaded.
    :param Path target:
        The target directory.
    """
    counter = 0
    while True:
        name = f"{base}_{video_audio}_{counter}"
        unique = target / f"{name}.{subtype}"

        if not unique.exists():
            return str(name)
        counter += 1


def ffmpeg_process(
    youtube: YouTube, resolution: str, target: Optional[str] = None
) -> None:
    """
    Downloads the adaptive audio and video streams given a resolution,
    then uses ffmpeg to create a new file with the audio and video from
    each, before deleting these files and keeping the combination.
    If no resolution is given, will download the highest, trying mp4 first.

    :param YouTube youtube:
        A valid YouTube object.
    :param str resolution:
        YouTube video resolution.
    :param str target:
        Target directory for download
    """
    youtube.register_on_progress_callback(on_progress)
    if target is None:
        target = Path.cwd()
    else:
        target = Path(target)

    if resolution is "best":
        highest_quality = youtube.streams.filter(
            progressive=False
            ).order_by("resolution").desc().first()

        video_stream = youtube.streams.filter(
            progressive=False, subtype="mp4"
            ).order_by("resolution").desc().first()

        if highest_quality.resolution == video_stream.resolution:
            ffmpeg_downloader(youtube=youtube, stream=video_stream, target=target)
        else:
            ffmpeg_downloader(youtube=youtube, stream=highest_quality, target=target)
    else:
        video_stream = youtube.streams.filter(
            progressive=False, resolution=resolution, subtype="mp4"
            ).first()
        if video_stream is not None:
            ffmpeg_downloader(youtube=youtube, stream=video_stream, target=target)
        else:
            video_stream = youtube.streams.filter(
                progressive=False, resolution=resolution
                ).first()
            if video_stream is None:
                print(f"Could not find a stream with resolution: {resolution}")
                print("Try one of these:")
                display_streams(youtube)
                sys.exit()
            ffmpeg_downloader(youtube=youtube, stream=video_stream, target=target)


def ffmpeg_downloader(youtube: YouTube, stream: Stream, target: Path) -> None:
    audio_stream = youtube.streams.filter(
        only_audio=True, subtype=stream.subtype
        ).order_by("abr").desc().first()

    video_unique_name = unique_name(
        safe_filename(stream.title), stream.subtype, "video", target=target
        )
    audio_unique_name = unique_name(
        safe_filename(stream.title), stream.subtype, "audio", target=target
        )
    _download(stream=stream, target=str(target), filename=video_unique_name)
    _download(stream=audio_stream, target=str(target), filename=audio_unique_name)

    video_path = Path(target) / f"{video_unique_name}.{stream.subtype}"
    audio_path = Path(target) / f"{audio_unique_name}.{stream.subtype}"
    final_path = Path(target) / f"{safe_filename(stream.title)}.{stream.subtype}"

    subprocess.run(["ffmpeg", "-i", f"{video_path}", "-i",
        f"{audio_path}", "-codec", "copy", f'{final_path}'
        ]
    )
    video_path.unlink()
    audio_path.unlink()


def download_by_itag(youtube: YouTube, itag: int, target: Optional[str] = None) -> None:
    """Start downloading a YouTube video.

    :param YouTube youtube:
        A valid YouTube object.
    :param int itag:
        YouTube format identifier code.
    :param str target:
        Target directory for download
    """
    stream = youtube.streams.get_by_itag(itag)
    if stream is None:
        print(f"Could not find a stream with itag: {itag}")
        print("Try one of these:")
        display_streams(youtube)
        sys.exit()

    youtube.register_on_progress_callback(on_progress)

    try:
        _download(stream, target=target)
    except KeyboardInterrupt:
        sys.exit()


def download_by_resolution(
    youtube: YouTube, resolution: str, target: Optional[str] = None
) -> None:
    """Start downloading a YouTube video.

    :param YouTube youtube:
        A valid YouTube object.
    :param str resolution:
        YouTube video resolution.
    :param str target:
        Target directory for download
    """
    # TODO(nficano): allow dash itags to be selected
    stream = youtube.streams.get_by_resolution(resolution)
    if stream is None:
        print(f"Could not find a stream with resolution: {resolution}")
        print("Try one of these:")
        display_streams(youtube)
        sys.exit()

    youtube.register_on_progress_callback(on_progress)

    try:
        _download(stream, target=target)
    except KeyboardInterrupt:
        sys.exit()


def display_streams(youtube: YouTube) -> None:
    """Probe YouTube video and lists its available formats.

    :param YouTube youtube:
        A valid YouTube watch URL.

    """
    for stream in youtube.streams.all():
        print(stream)


def _print_available_captions(captions: CaptionQuery) -> None:
    print(f"Available caption codes are: {', '.join(c.code for c in captions.all())}")


def download_caption(
    youtube: YouTube, lang_code: Optional[str], target: Optional[str] = None
) -> None:
    """Download a caption for the YouTube video.

    :param YouTube youtube:
        A valid YouTube object.
    :param str lang_code:
        Language code desired for caption file.
        Prints available codes if the value is None
        or the desired code is not available.
    :param str target:
        Target directory for download
    """
    if lang_code is None:
        _print_available_captions(youtube.captions)
        return

    caption = youtube.captions.get_by_language_code(lang_code=lang_code)
    if caption:
        downloaded_path = caption.download(title=youtube.title, output_path=target)
        print(f"Saved caption file to: {downloaded_path}")
    else:
        print(f"Unable to find caption with code: {lang_code}")
        _print_available_captions(youtube.captions)


def download_audio(
    youtube: YouTube, filetype: str, target: Optional[str] = None
) -> None:
    """
    Given a filetype, downloads the highest quality available audio stream for a 
    YouTube video.
    
    :param YouTube youtube:
        A valid YouTube object.
    :param str filetype:
        Desired file format to download.
    """
    audio = youtube.streams.filter(
        only_audio=True, subtype=filetype
        ).order_by("abr").desc().first()

    if audio is None:
        print(
            "No audio only stream found. Try one of these:")
        display_streams(youtube)
        sys.exit()

    youtube.register_on_progress_callback(on_progress)

    try:
        _download(audio)
    except KeyboardInterrupt:
        sys.exit()


if __name__ == "__main__":
    main()
