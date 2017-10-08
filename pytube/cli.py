# -*- coding: utf-8 -*-
"""
pytube.cli
~~~~~~~~~~

A simple command line application to download youtube videos.

"""
from __future__ import print_function

import argparse
import os
import sys

from pytube import YouTube


def main():
    """A simple command line application to download youtube videos."""
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
    args = parser.parse_args()
    if not args.url:
        parser.print_help()
        exit(1)
    if args.list:
        display_streams(args.url)
    elif args.itag:
        download(args.url, args.itag)


def get_terminal_size():
    """Returns the terminal size in rows and columns."""
    rows, columns = os.popen('stty size', 'r').read().split()
    return int(rows), int(columns)


def render_progress_percentage(bar, percent):
    """Writes the updated progress bar percentage and filled area.

    :param str bar:
        The filled and unfilled remainder chars of the progress bar.
    :param int percent:
        Numerical representation of progress completion.
    """
    text = ' ↳ |{bar}| {percent}%\r'.format(bar=bar, percent=percent)
    sys.stdout.write(text)
    sys.stdout.flush()


def display_progress_bar(count, total, ch='█', scale=0.55):
    _, columns = get_terminal_size()
    max_width = int(columns * scale)

    filled = int(round(max_width * count / float(total)))
    remaining = max_width - filled
    bar = ch * filled + ' ' * remaining
    percent = round(100.0 * count / float(total), 1)
    render_progress_percentage(bar, percent)


def on_progress(stream, file_handle, bytes_remaining):
    """On download progress callback function.

    :param object stream:
        An instance of :class:`Stream <Stream>` being downloaded.
    :param :class:`_io.BufferedWriter <BufferedWriter>` file_handle:
        The file handle where the media is being written to.
    :param int bytes_remaining:
        The delta between the total file size in bytes and amount already
        downloaded.
    """
    total = stream.filesize
    count = total - bytes_remaining
    display_progress_bar(count, total)


def download(url, itag):
    """Begin downloading a YouTube video.

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
    """Probes YouTube video and lists its available formats.

    :param str url:
        A valid YouTube watch URL.
    """
    yt = YouTube(url)
    for stream in yt.streams.all():
        print(stream)


if __name__ == '__main__':
    main()
