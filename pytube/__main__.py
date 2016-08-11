#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import os
import argparse

from . import YouTube
from .utils import print_status, FullPaths
from .exceptions import PytubeError
from pprint import pprint


def main():
    parser = argparse.ArgumentParser(description='YouTube video downloader')
    parser.add_argument("url", help=(
        "The URL of the Video to be downloaded"))
    parser.add_argument("--extension", "-e", dest="ext", help=(
        "The requested format of the video"))
    parser.add_argument("--resolution", "-r", dest="res", help=(
        "The requested resolution"))
    parser.add_argument("--path", "-p", action=FullPaths, default=os.getcwd(),
                        dest="path", help=("The path to save the video to."))
    parser.add_argument("--filename", "-f", dest="filename", help=(
        "The filename, without extension, to save the video in."))

    args = parser.parse_args()

    try:
        yt = YouTube(args.url)
        videos = []
        for i, video in enumerate(yt.get_videos()):
            ext = video.extension
            res = video.resolution
            videos.append("{} {}".format(ext, res))
    except PytubeError:
        print("Incorrect video URL.")
        sys.exit(1)

    if args.filename:
        yt.set_filename(args.filename)

    if args.ext or args.res:
        if not all([args.ext, args.res]):
            print("Make sure you give either of the below specified "
                  "format/resolution combination.")
            pprint(videos)
            sys.exit(1)

    if args.ext and args.res:
        # There's only ope video that matches both so get it
        vid = yt.get(args.ext, args.res)
        # Check if there's a video returned
        if not vid:
            print("There's no video with the specified format/resolution "
                  "combination.")
            pprint(videos)
            sys.exit(1)

    elif args.ext:
        # There are several videos with the same extension
        videos = yt.filter(extension=args.ext)
        # Check if we have a video
        if not videos:
            print("There are no videos in the specified format.")
            sys.exit(1)
        # Select the highest resolution one
        vid = max(videos)
    elif args.res:
        # There might be several videos in the same resolution
        videos = yt.filter(resolution=args.res)
        # Check if we have a video
        if not videos:
            print("There are no videos in the specified in the specified "
                  "resolution.")
            sys.exit(1)
        # Select the highest resolution one
        vid = max(videos)
    else:
        # If nothing is specified get the highest resolution one
        vid = max(yt.get_videos())

    try:
        vid.download(path=args.path, on_progress=print_status)
    except KeyboardInterrupt:
        print("Download interrupted.")
        sys.exit(1)

if __name__ == '__main__':
    main()
