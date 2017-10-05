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


def _get_terminal_size():
    """Returns the terminal size in rows and columns."""
    rows, columns = os.popen('stty size', 'r').read().split()
    return int(rows), int(columns)


def _render_progress_bar(bar, percent):
    text = ' ↳ |{bar}| {percent}%\r'.format(bar=bar, percent=percent)
    sys.stdout.write(text)
    sys.stdout.flush()


def display_progress_bar(count, total, ch='█', scale=0.55):
    _, columns = _get_terminal_size()
    max_width = int(columns * scale)

    filled = int(round(max_width * count / float(total)))
    remaining = max_width - filled
    bar = ch * filled + ' ' * remaining
    percent = round(100.0 * count / float(total), 1)
    _render_progress_bar(bar, percent)


def on_progress(stream, file_handle, bytes_remaining):
    total = stream.filesize
    count = total - bytes_remaining
    display_progress_bar(count, total)


def download(url, itag):
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
    yt = YouTube(url)
    for stream in yt.streams.all():
        print(stream)


if __name__ == '__main__':
    main()
