![pytube](https://s3.amazonaws.com/assets.nickficano.com/pytube_logo.png)

# A lightwight, dependency-free YouTube Video download library, written in Python.

Downloading videos from YouTube shouldn't require some bloatware application,
its usually a niche condition you need to do so in the first place.

## Background

After missing the deadline to register for PyCon 2012, I decided to write what
became PyTube and crawler to collect all the YouTube links for the talks
on [PyVideos.org](http://pyvideo.org/).

To avoid having to encode them to mp4 (so I could watch them on my iPhone)
I wrote it so you could specify an encoding format.

In recently weeks interest has picked up in the project, so I decided to
dedicate more time to further its development and actively maintain it.

## Principals 

My only real goals for this is to never require any third party dependancies,
to keep it simple and make it reliable.

## Planned Features

The only features I see implementing in the near future are:

- Allow it to run as a command-line utility. 
- Making it compatible with Python 3.


## Usage

``` python
from youtube import YouTube

# not necessary, just for demo purposes
from pprint import pprint as pp

yt = YouTube()

# Set the video URL.
yt.url = "http://www.youtube.com/watch?v=Ik-RsDGPI5Y"

# Once set, you can see all the codec and quality options YouTube has made
# available for the perticular video by printing videos.

pp(yt.videos)

#[<Video: 3gp - 144p>,
# <Video: 3gp - 144p>,
# <Video: 3gp - 240p>,
# <Video: 3gp - 240p>,
# <Video: flv - 224p>,
# <Video: flv - 224p>,
# <Video: flv - 360p>,
# <Video: flv - 360p>,
# <Video: flv - 480p>,
# <Video: flv - 480p>,
# <Video: mp4 - 360p>,
# <Video: mp4 - 360p>,
# <Video: mp4 - 720p>,
# <Video: mp4 - 720p>,
# <Video: webm - 360p>,
# <Video: webm - 360p>,
# <Video: webm - 480p>,
# <Video: webm - 480p>]

# The filename is automatically generated based on the video title.
# You can override this by manually setting the filename.

# view the auto generated filename:
print yt.filename

#Pulp Fiction - Dancing Scene [HD]

# set the filename:
yt.filename = 'Dancing Scene from Pulp Fiction'

# You can also filter the criteria by filetype.

pp(yt.filter('flv'))

# [<Video: flv - 224p>,
# <Video: flv - 224p>,
# <Video: flv - 360p>,
# <Video: flv - 360p>,
# <Video: flv - 480p>,
# <Video: flv - 480p>]

# and by resolution
pp(yt.filter(res='480p'))

# [<Video: flv - 480p>,
# <Video: flv - 480p>,
# <Video: webm - 480p>,
# <Video: webm - 480p>]

# to select a video by a specific resolution and filetype you can use the get
# method.

video = yt.get('mp4', '720p')

# Okay, let's download it!
video.download()

# Downloading: Pulp Fiction - Dancing Scene.mp4 Bytes: 37561829
# 37561829  [100.00%]

# Note: If you wanted to choose the output directory, simply pass it as an 
# argument to the download method.
video.download('/tmp/')
```
