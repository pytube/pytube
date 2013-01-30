import argparse

from .api import YouTube
from .utils import print_status


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
    yt.url = args.url

    if args.filename:
        yt.filename = args.filename

    if args.ext and args.res:
        # There's only ope video that matches both so get it
        vid = yt.get(args.ext, args.res)
    elif args.ext:
        # There are several videos with the same extension
        videos = yt.filter(extension=args.ext)
        # Select the highest resolution one
        vid = max(videos)
    elif args.res:
        # There are several videos with the same extension
        videos = yt.filter(resolution=args.res)
        # Select the highest resolution one
        vid = max(videos)
    else:
        # If nothing is specified get the highest resolution one
        vid = max(yt.videos)

    vid.download(path=args.path, on_progress=print_status)
