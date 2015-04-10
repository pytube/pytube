from __future__ import print_function
from pytube import YouTube
from pprint import pprint



yt = YouTube()

yt.url = "http://www.youtube.com/watch?v=Ik-RsDGPI5Y"
pprint(yt.videos)
# view the auto generated filename:

print(yt.filename)
yt.filename = 'Dancing'
video = yt.get('mp4', '720p')


video.download('/home/user/') #video.download('/tmp/')
