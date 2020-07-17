#!/usr/bin/env python3
# flake8: noqa: E402
import json
import sys
from os import path

from pytube import YouTube

currentdir = path.dirname(path.realpath(__file__))
parentdir = path.dirname(currentdir)
sys.path.append(parentdir)


yt = YouTube(sys.argv[1], defer_prefetch_init=True)
yt.prefetch()
output = {
    "url": sys.argv[1],
    "watch_html": yt.watch_html,
    "video_info": yt.vid_info,
    "js": yt.js,
    "embed_html": yt.embed_html,
}

outpath = path.join(currentdir, "mocks", "yt-video-" + yt.video_id + ".json")
print("Writing to: " + outpath)
with open(outpath, "w") as f:
    json.dump(output, f)
