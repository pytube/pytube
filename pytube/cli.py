# -*- coding: utf-8 -*-
"""A simple command line application to download youtube videos."""
from __future__ import print_function

import argparse
import json
import os
import sys

from pytube import YouTube


def main():
    """Command line application to download youtube videos."""
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument('url', help='The YouTube /watch url', nargs='?')
    parser.add_argument(
        '--itag', type=int, help=(
            'The itag for the desired stream'
        ),
    )
    parser.add_argument(
        '-l', '--list', action='store_true', help=(
            'The list option causes pytube cli to return a list of streams '
            'available to download'
        ),
    )
    parser.add_argument(
        '--build-debug-report', action='store_true', help=(
            'Save the html and js to disk'
        ),
    )
    args = parser.parse_args()
    if not args.url:
        parser.print_help()
        sys.exit(1)
    if args.list:
        display_streams(args.url)
    elif args.build_debug_report:
        build_debug_report(args.url)
    elif args.itag:
        download(args.url, args.itag)


def build_debug_report(url):
    yt = YouTube(url)
    fp = os.path.join(
        os.getcwd(),
        'yt-video-{yt.video_id}.json'.format(yt=yt),
    )
    with open(fp, 'w') as fh:
        fh.write(json.dumps({
            'js': yt.js,
            'watch_html': yt.watch_html,
            'video_info': yt.vid_info,
        }))


def get_terminal_size():
    """Return the terminal size in rows and columns."""
    rows, columns = os.popen('stty size', 'r').read().split()
    return int(rows), int(columns)


def display_progress_bar(bytes_received, filesize, ch='█', scale=0.55):
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
    :param ch str:
        Character to use for presenting progress segment.
    :param float scale:
        Scale multipler to reduce progress bar size.

    """
    _, columns = get_terminal_size()
    max_width = int(columns * scale)

    filled = int(round(max_width * bytes_received / float(filesize)))
    remaining = max_width - filled
    bar = ch * filled + ' ' * remaining
    percent = round(100.0 * bytes_received / float(filesize), 1)
    text = ' ↳ |{bar}| {percent}%\r'.format(bar=bar, percent=percent)
    sys.stdout.write(text)
    sys.stdout.flush()


def on_progress(stream, file_handle, bytes_remaining):
    """On download progress callback function.

    :param object stream:
        An instance of :class:`Stream <Stream>` being downloaded.
    :param :class:`_io.BufferedWriter <BufferedWriter>` file_handle:
        The file handle where the media is being written to.
    :param int bytes_remaining:
        How many bytes have been downloaded.

    """
    filesize = stream.filesize
    bytes_received = filesize - bytes_remaining
    display_progress_bar(bytes_received, filesize)


def download(url, itag):
    """Start downloading a YouTube video.

    :param str url:
        A valid YouTube watch URL.
    :param str itag:
        YouTube format identifier code.

    """
    # TODO(nficano): allow download target to be specified
    # TODO(nficano): allow dash itags to be selected
    yt = YouTube(url, on_progress_callback=on_progress)
    stream = yt.streams.get(itag)
    print('\n{fn} | {fs} bytes'.format(
        fn=stream.default_filename,
        fs=stream.filesize,
    ))
    stream.download()
    sys.stdout.write('\n')


def display_streams(url):
    """Probe YouTube video and lists its available formats.

    :param str url:
        A valid YouTube watch URL.

    """
    yt = YouTube(url)
    for stream in yt.streams.all():
        print(stream)


if __name__ == '__main__':
    main()
