<div align="center">
  <p>
  <img src="https://assets.nickficano.com/gh-pytube.min.svg" width="456" height="143" alt="pytube logo" />
  </p>
  <p align="center">
	  <img src="https://img.shields.io/pypi/v/pytube.svg" alt="pypi">
	  <a href="https://travis-ci.org/nficano/pytube">
      <img src="https://travis-ci.org/nficano/pytube.svg?branch=master" />
    </a>
	  <a href="http://python-pytube.readthedocs.io/en/latest/?badge=latest">
      <img src="https://readthedocs.org/projects/python-pytube/badge/?version=latest" />
    </a>
	  <a href="https://codecov.io/gh/nficano/pytube">
      <img src="https://codecov.io/gh/nficano/pytube/branch/master/graph/badge.svg" />
    </a>
    <a href="https://pypi.org/project/pytube/">
      <img src="https://img.shields.io/pypi/dm/pytube.svg" alt="pypi">
    </a>
	  <a href="https://pypi.python.org/pypi/pytube/">
      <img src="https://img.shields.io/pypi/pyversions/pytube.svg" />
    </a>
  </p>
</div>


###  Actively soliciting contributers!
Have ideas for how pytube can be improved? Feel free to open an issue or a pull
request!

# pytube
*pytube* is a very serious, lightweight, dependency-free Python library (and
command-line utility) for downloading YouTube Videos.

## Installation
Pytube requires an installation of python 3.6 or greater, as well as pip.
Pip is typically bundled with python installations, and you can find options
for how to install python at https://python.org.

To install from pypi with pip:

```bash
$ python -m pip install pytube
```

Sometime, the pypi release becomes slightly outdated. To install from the
source with pip:

```bash
$ python -m pip install git+https://github.com/pytube/pytube
```

## Description
YouTube is the most popular video-sharing platform in the world and as a hacker
you may encounter a situation where you want to script something to download
videos. For this I present to you *pytube*.

*pytube* is a lightweight library written in Python. It has no third party
dependencies and aims to be highly reliable.

*pytube* also makes pipelining easy, allowing you to specify callback functions
for different download events, such as  ``on progress`` or ``on complete``.

Finally *pytube* also includes a command-line utility, allowing you to quickly
download videos right from terminal.

### Behold, a perfect balance of simplicity versus flexibility:

```python
 >>> YouTube('https://youtu.be/2lAe1cqCOXo').streams.first().download()
 >>> yt = YouTube('http://youtube.com/watch?v=2lAe1cqCOXo')
 >>> yt.streams
  ... .filter(progressive=True, file_extension='mp4')
  ... .order_by('resolution')
  ... .desc()
  ... .first()
  ... .download()
```

## Features
- Support for both progressive & DASH streams
- Support for downloading complete playlist
- Easily register ``on_download_progress`` & ``on_download_complete`` callbacks
- Command-line interfaced included
- Caption track support
- Outputs caption tracks to .srt format (SubRip Subtitle)
- Ability to capture thumbnail URL
- Extensively documented source code
- No third-party dependencies

## Getting started

Let's begin with showing how easy it is to download a video with pytube:

```python
>>> from pytube import YouTube
>>> YouTube('https://youtube.com/watch?v=2lAe1cqCOXo').streams.first().download()
```
This example will download the highest quality progressive download stream
available.

Next, let's explore how we would view what video streams are available:

```python
>>> yt = YouTube('https://youtube.com/watch?v=2lAe1cqCOXo')
>>> yt.streams
 [<Stream: itag="18" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.42001E" acodec="mp4a.40.2" progressive="True" type="video">,
 <Stream: itag="22" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.64001F" acodec="mp4a.40.2" progressive="True" type="video">,
 <Stream: itag="137" mime_type="video/mp4" res="1080p" fps="30fps" vcodec="avc1.640028" progressive="False" type="video">,
 ...
 <Stream: itag="250" mime_type="audio/webm" abr="70kbps" acodec="opus" progressive="False" type="audio">,
 <Stream: itag="251" mime_type="audio/webm" abr="160kbps" acodec="opus" progressive="False" type="audio">]
```
You may notice that some streams listed have both a video codec and audio
codec, while others have just video or just audio, this is a result of YouTube
supporting a streaming technique called Dynamic Adaptive Streaming over HTTP
(DASH).

In the context of pytube, the implications are for the highest quality streams;
you now need to download both the audio and video tracks and then post-process
them with software like FFmpeg to merge them.

The legacy streams that contain the audio and video in a single file (referred
to as "progressive download") are still available, but only for resolutions
720p and below.

Pytube allows you to filter on every property available (see the documentation
for the complete list), let's take a look at some of the most useful ones.

To only view these progressive download streams:

```python
 >>> yt.streams.filter(progressive=True)
  [<Stream: itag="18" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.42001E" acodec="mp4a.40.2" progressive="True" type="video">,
  <Stream: itag="22" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.64001F" acodec="mp4a.40.2" progressive="True" type="video">]
```

Conversely, if you only want to see the DASH streams (also referred to as
"adaptive") you can do:

```python
>>> yt.streams.filter(adaptive=True)
 [<Stream: itag="137" mime_type="video/mp4" res="1080p" fps="30fps" vcodec="avc1.640028" progressive="False" type="video">,
 <Stream: itag="248" mime_type="video/webm" res="1080p" fps="30fps" vcodec="vp9" progressive="False" type="video">,
 <Stream: itag="399" mime_type="video/mp4" res="None" fps="30fps" vcodec="av01.0.08M.08" progressive="False" type="video">,
 ...
 <Stream: itag="250" mime_type="audio/webm" abr="70kbps" acodec="opus" progressive="False" type="audio">,
 <Stream: itag="251" mime_type="audio/webm" abr="160kbps" acodec="opus" progressive="False" type="audio">]
```

You can also interact with Youtube playlists:

```python
>>> from pytube import Playlist
>>> pl = Playlist("https://www.youtube.com/watch?v=Edpy1szoG80&list=PL153hDY-y1E00uQtCVCVC8xJ25TYX8yPU")
>>> for video in pl.videos:
>>>     video.streams.first().download()
```


To list the audio only streams:

```python
>>> yt.streams.filter(only_audio=True)
  [<Stream: itag="140" mime_type="audio/mp4" abr="128kbps" acodec="mp4a.40.2" progressive="False" type="audio">,
  <Stream: itag="249" mime_type="audio/webm" abr="50kbps" acodec="opus" progressive="False" type="audio">,
  <Stream: itag="250" mime_type="audio/webm" abr="70kbps" acodec="opus" progressive="False" type="audio">,
  <Stream: itag="251" mime_type="audio/webm" abr="160kbps" acodec="opus" progressive="False" type="audio">]
```

To list only ``mp4`` streams:

```python
>>> yt.streams.filter(subtype='mp4').all()
 [<Stream: itag="18" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.42001E" acodec="mp4a.40.2" progressive="True" type="video">,
 <Stream: itag="22" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.64001F" acodec="mp4a.40.2" progressive="True" type="video">,
 <Stream: itag="137" mime_type="video/mp4" res="1080p" fps="30fps" vcodec="avc1.640028" progressive="False" type="video">,
 ...
 <Stream: itag="394" mime_type="video/mp4" res="None" fps="30fps" vcodec="av01.0.00M.08" progressive="False" type="video">,
 <Stream: itag="140" mime_type="audio/mp4" abr="128kbps" acodec="mp4a.40.2" progressive="False" type="audio">]
```

Multiple filters can also be specified:

```python
>>> yt.streams.filter(subtype='mp4', progressive=True).all()
>>> # this can also be expressed as:
>>> yt.streams.filter(subtype='mp4').filter(progressive=True).all()
  [<Stream: itag="18" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.42001E" acodec="mp4a.40.2" progressive="True" type="video">,
  <Stream: itag="22" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.64001F" acodec="mp4a.40.2" progressive="True" type="video">]
```
You also have an interface to select streams by their itag, without needing to
filter:

```python
>>> yt.streams.get_by_itag(22)
  <Stream: itag="22" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.64001F" acodec="mp4a.40.2" progressive="True" type="video">
```

If you need to optimize for a specific feature, such as the "highest
resolution" or "lowest average bitrate":

```python
>>> yt.streams.filter(progressive=True).order_by('resolution').desc().all()
  [<Stream: itag="22" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.64001F" acodec="mp4a.40.2" progressive="True" type="video">,
  <Stream: itag="18" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.42001E" acodec="mp4a.40.2" progressive="True" type="video">]
```
Note that ``order_by`` cannot be used if your attribute is undefined in any of
the Stream instances, so be sure to apply a filter to remove those before
calling it.

If your application requires post-processing logic, pytube allows you to
specify an "on download complete" callback function:

```python
 >>> def convert_to_aac(stream, file_handle):
         return  # do work

 >>> yt.register_on_complete_callback(convert_to_aac)
```

Similarly, if your application requires on-download progress logic, pytube
exposes a callback for this as well:

```python
 >>> def show_progress_bar(stream, chunk, bytes_remaining):
         return  # do work

 >>> yt.register_on_progress_callback(show_progress_bar)
```

Download video(s) to specific directory with specific name:

```python
>>> yt = YouTube('https://youtube.com/watch?v=2lAe1cqCOXo')
>>> yt.streams.first().download(output_path="/tmp" ,filename='output')
```

## Command-line interface

Pytube also ships with a tiny cli interface for downloading and probing videos.

Let's start with downloading:

```bash
$ pytube http://youtube.com/watch?v=2lAe1cqCOXo --itag=22
```
To view available streams:

```bash
$ pytube http://youtube.com/watch?v=2lAe1cqCOXo --list
```

Finally, if you're filing a bug report, the cli contains a switch called
``--build-playback-report``, which bundles up the state, allowing others
to easily replay your issue.
