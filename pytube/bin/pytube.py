#!/usr/bin/env python

import sys
import argparse

from pytube import YouTube
from pytube.utils import print_status
from pytube.exceptions import YouTubeError


def _main():
    parser = argparse.ArgumentParser(description='YouTube video downloader')
    parser.add_argument("url", help="The URL of the Video to be downloaded")
    parser.add_argument("--extension", "-e",
                        help="The requested format of the video", dest="ext")
    parser.add_argument("--resolution", "-r",
                        help="The requested resolution", dest="res")
    parser.add_argument("--path", "-p",
                        help="The path to save the video to.", dest="path")
    parser.add_argument("--filename", "-f",
                        dest="filename",
                        help=("The filename, without extension, "
                              "to save the video in."))

    args = parser.parse_args()

    yt =  YouTube()
    try:
        yt.url = args.url
    except YouTubeError:
        print "Incorrect video URL."
        sys.exit(1)

    if args.filename:
        yt.filename = args.filename

    if args.ext and args.res:
        # There's only ope video that matches both so get it
        vid = yt.get(args.ext, args.res)
        # Check if there's a video returned
        if not vid:
            print "There's no video with the specified format/resolution combination."
            sys.exit(1)

    elif args.ext:
        # There are several videos with the same extension
        videos = yt.filter(extension=args.ext)
        # Check if we have a video
        if not videos:
            print "There are no videos in the specified format."
            sys.exit(1)
        # Select the highest resolution one
        vid = max(videos)
    elif args.res:
        # There might be several videos in the same resolution
        videos = yt.filter(res=args.res)
        # Check if we have a video
        if not videos:
            print "There are no videos in the specified in the specified resolution."
            sys.exit(1)
        # Select the highest resolution one
        vid = max(videos)
    else:
        # If nothing is specified get the highest resolution one
        vid = max(yt.videos)

    try:
        vid.download(path=args.path, on_progress=print_status)
    except KeyboardInterrupt:
        print "Download interrupted."
        sys.exit(1)
