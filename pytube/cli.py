# -*- coding: utf-8 -*-
"""A simple command line application to download youtube videos."""
from __future__ import absolute_import
from __future__ import print_function

import argparse
import datetime as dt
import gzip
import json
import logging
import os
import sys

from pytube import __version__
from pytube import YouTube


logger = logging.getLogger(__name__)


def main():
    """Command line application to download youtube videos."""
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument('url', help='The YouTube /watch url', nargs='?')
    parser.add_argument(
        '--version', action='version',
        version='%(prog)s ' + __version__,
    )
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
        '-v', '--verbose', action='count', default=0, dest='verbosity',
        help='Verbosity level',
    )
    parser.add_argument(
        '--build-playback-report', action='store_true', help=(
            'Save the html and js to disk'
        ),
    )

    args = parser.parse_args()
    logging.getLogger().setLevel(max(3 - args.verbosity, 0) * 10)

    if not args.url:
        parser.print_help()
        sys.exit(1)

    if args.list:
        display_streams(args.url)

    elif args.build_playback_report:
        build_playback_report(args.url)

    elif args.itag:
        download(args.url, args.itag)


def build_playback_report(url):
    """Serialize the request data to json for offline debugging.

    :param str url:
        A valid YouTube watch URL.
    """
    yt = YouTube(url)
    ts = int(dt.datetime.utcnow().timestamp())
    fp = os.path.join(
        os.getcwd(),
        'yt-video-{yt.video_id}-{ts}.json.tar.gz'.format(yt=yt, ts=ts),
    )

    js = yt.js
    watch_html = yt.watch_html
    vid_info = yt.vid_info

    with gzip.open(fp, 'wb') as fh:
        fh.write(
            json.dumps({
                'url': url,
                'js': js,
                'watch_html': watch_html,
                'video_info': vid_info,
            })
            .encode('utf8'),
        )


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


def on_progress(stream, chunk, file_handle, bytes_remaining):
    """On download progress callback function.

    :param object stream:
        An instance of :class:`Stream <Stream>` being downloaded.
    :param file_handle:
        The file handle where the media is being written to.
    :type file_handle:
        :py:class:`io.BufferedWriter`
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
    stream = yt.streams.get_by_itag(itag)
    print('\n{fn} | {fs} bytes'.format(
        fn=stream.default_filename,
        fs=stream.filesize,
    ))
    try:
        stream.download()
        sys.stdout.write('\n')
    except KeyboardInterrupt:
        sys.exit()


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
