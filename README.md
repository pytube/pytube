
<div align="center">
  <p align="center">
	  <a href="https://pypi.org/project/pytube3/"><img src="https://img.shields.io/pypi/v/pytube3.svg" alt="pypi"></a>
	  <a href="https://pypi.python.org/pypi/pytube3/"><img src="https://img.shields.io/pypi/pyversions/pytube3.svg" /></a>
	  <a href="https://travis-ci.com/hbmartin/pytube3/"><img src="https://travis-ci.org/hbmartin/pytube3.svg?branch=master" /></a>
	  <a href='https://pytube3.readthedocs.io/en/latest/?badge=latest'><img src='https://readthedocs.org/projects/pytube3/badge/?version=latest' alt='Documentation Status' /></a>
	  <a href="https://codecov.io/gh/hbmartin/pytube3"><img src="https://codecov.io/gh/hbmartin/pytube3/branch/master/graph/badge.svg" /></a>
	  <a href="https://www.codefactor.io/repository/github/hbmartin/pytube3/overview/master"><img src="https://www.codefactor.io/repository/github/hbmartin/pytube3/badge/master" alt="CodeFactor" /></a>
	  <a href="https://gitter.im/pytube3/community"><img src="https://img.shields.io/badge/chat-gitter-lightgrey" /></a>
  </p>
</div>

# pytube3

## Table of Contents
  * [Installation](#installation)
  * [Quick start](#quick-start)
  * [Features](#features)
  * [Usage](#usage)
  * [Command-line interface](#command-line-interface)
  * [Development](#development)
  * [GUIs and other libraries](#guis-and-other-libraries)

## Installation

Download using pip via pypi.

```bash
$ pip install pytube3 --upgrade
```
(Mac/homebrew users may need to use ``pip3``)


## Quick start
```python
 >>> from pytube import YouTube
 >>> YouTube('https://youtu.be/9bZkp7q19f0').streams.get_highest_resolution().download()
 >>>
 >>> yt = YouTube('http://youtube.com/watch?v=9bZkp7q19f0')
 >>> yt.streams
  ... .filter(progressive=True, file_extension='mp4')
  ... .order_by('resolution')[-1]
  ... .download()
```
A GUI frontend for pytube3 is available at [YouTubeDownload](https://github.com/YouTubeDownload/YouTubeDownload)

## Features
  * Support for Both Progressive & DASH Streams
  * Support for downloading complete playlist
  * Easily Register ``on_download_progress`` & ``on_download_complete`` callbacks
  * Command-line Interfaced Included
  * Caption Track Support
  * Outputs Caption Tracks to .srt format (SubRip Subtitle)
  * Ability to Capture Thumbnail URL.
  * Extensively Documented Source Code
  * No Third-Party Dependencies

## Usage

Let's begin with showing how easy it is to download a video with pytube:

```python
>>> from pytube import YouTube
>>> YouTube('http://youtube.com/watch?v=9bZkp7q19f0').streams[0].download()
```
This example will download the highest quality progressive download stream available.

Next, let's explore how we would view what video streams are available:

```python
>>> yt = YouTube('http://youtube.com/watch?v=9bZkp7q19f0')
>>> print(yt.streams)
 [<Stream: itag="22" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.64001F" acodec="mp4a.40.2">,
 <Stream: itag="43" mime_type="video/webm" res="360p" fps="30fps" vcodec="vp8.0" acodec="vorbis">,
 <Stream: itag="18" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.42001E" acodec="mp4a.40.2">,
 <Stream: itag="36" mime_type="video/3gpp" res="240p" fps="30fps" vcodec="mp4v.20.3" acodec="mp4a.40.2">,
 <Stream: itag="17" mime_type="video/3gpp" res="144p" fps="30fps" vcodec="mp4v.20.3" acodec="mp4a.40.2">,
 <Stream: itag="137" mime_type="video/mp4" res="1080p" fps="30fps" vcodec="avc1.640028">,
 <Stream: itag="248" mime_type="video/webm" res="1080p" fps="30fps" vcodec="vp9">,
 <Stream: itag="136" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.4d401f">,
 <Stream: itag="247" mime_type="video/webm" res="720p" fps="30fps" vcodec="vp9">,
 <Stream: itag="135" mime_type="video/mp4" res="480p" fps="30fps" vcodec="avc1.4d401e">,
 <Stream: itag="244" mime_type="video/webm" res="480p" fps="30fps" vcodec="vp9">,
 <Stream: itag="134" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.4d401e">,
 <Stream: itag="243" mime_type="video/webm" res="360p" fps="30fps" vcodec="vp9">,
 <Stream: itag="133" mime_type="video/mp4" res="240p" fps="30fps" vcodec="avc1.4d4015">,
 <Stream: itag="242" mime_type="video/webm" res="240p" fps="30fps" vcodec="vp9">,
 <Stream: itag="160" mime_type="video/mp4" res="144p" fps="30fps" vcodec="avc1.4d400c">,
 <Stream: itag="278" mime_type="video/webm" res="144p" fps="30fps" vcodec="vp9">,
 <Stream: itag="140" mime_type="audio/mp4" abr="128kbps" acodec="mp4a.40.2">,
 <Stream: itag="171" mime_type="audio/webm" abr="128kbps" acodec="vorbis">,
 <Stream: itag="249" mime_type="audio/webm" abr="50kbps" acodec="opus">,
 <Stream: itag="250" mime_type="audio/webm" abr="70kbps" acodec="opus">,
 <Stream: itag="251" mime_type="audio/webm" abr="160kbps" acodec="opus">]
```

### Selecting an itag

You may notice that some streams listed have both a video codec and audio codec, while others have just video or just audio, this is a result of YouTube supporting a streaming technique called Dynamic Adaptive Streaming over HTTP (DASH).

In the context of pytube, the implications are for the highest quality streams; you now need to download both the audio and video tracks and then post-process them with software like FFmpeg to merge them.

The legacy streams that contain the audio and video in a single file (referred to as "progressive download") are still available, but only for resolutions 720p and below.

To only view these progressive download streams:

```python
 >>> yt.streams.filter(progressive=True)
  [<Stream: itag="22" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.64001F" acodec="mp4a.40.2">,
  <Stream: itag="43" mime_type="video/webm" res="360p" fps="30fps" vcodec="vp8.0" acodec="vorbis">,
  <Stream: itag="18" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.42001E" acodec="mp4a.40.2">,
  <Stream: itag="36" mime_type="video/3gpp" res="240p" fps="30fps" vcodec="mp4v.20.3" acodec="mp4a.40.2">,
  <Stream: itag="17" mime_type="video/3gpp" res="144p" fps="30fps" vcodec="mp4v.20.3" acodec="mp4a.40.2">]
```

Conversely, if you only want to see the DASH streams (also referred to as "adaptive") you can do:

```python
>>> yt.streams.filter(adaptive=True)
 [<Stream: itag="137" mime_type="video/mp4" res="1080p" fps="30fps" vcodec="avc1.640028">,
  <Stream: itag="248" mime_type="video/webm" res="1080p" fps="30fps" vcodec="vp9">,
  <Stream: itag="136" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.4d401f">,
  <Stream: itag="247" mime_type="video/webm" res="720p" fps="30fps" vcodec="vp9">,
  <Stream: itag="135" mime_type="video/mp4" res="480p" fps="30fps" vcodec="avc1.4d401e">,
  <Stream: itag="244" mime_type="video/webm" res="480p" fps="30fps" vcodec="vp9">,
  <Stream: itag="134" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.4d401e">,
  <Stream: itag="243" mime_type="video/webm" res="360p" fps="30fps" vcodec="vp9">,
  <Stream: itag="133" mime_type="video/mp4" res="240p" fps="30fps" vcodec="avc1.4d4015">,
  <Stream: itag="242" mime_type="video/webm" res="240p" fps="30fps" vcodec="vp9">,
  <Stream: itag="160" mime_type="video/mp4" res="144p" fps="30fps" vcodec="avc1.4d400c">,
  <Stream: itag="278" mime_type="video/webm" res="144p" fps="30fps" vcodec="vp9">,
  <Stream: itag="140" mime_type="audio/mp4" abr="128kbps" acodec="mp4a.40.2">,
  <Stream: itag="171" mime_type="audio/webm" abr="128kbps" acodec="vorbis">,
  <Stream: itag="249" mime_type="audio/webm" abr="50kbps" acodec="opus">,
  <Stream: itag="250" mime_type="audio/webm" abr="70kbps" acodec="opus">,
  <Stream: itag="251" mime_type="audio/webm" abr="160kbps" acodec="opus">]
```

### Playlists

You can also download a complete Youtube playlist:

```python
>>> from pytube import Playlist
>>> playlist = Playlist("https://www.youtube.com/playlist?list=PLynhp4cZEpTbRs_PYISQ8v_uwO0_mDg_X")
>>> for video in playlist:
>>> 	video.streams.get_highest_resolution().download()
```
This will download the highest progressive stream available (generally 720p) from the given playlist.

### Filtering

Pytube allows you to filter on every property available (see the documentation for the complete list), let's take a look at some of the most useful ones.

To list the audio only streams:

```python
>>> yt.streams.filter(only_audio=True)
  [<Stream: itag="140" mime_type="audio/mp4" abr="128kbps" acodec="mp4a.40.2">,
  <Stream: itag="171" mime_type="audio/webm" abr="128kbps" acodec="vorbis">,
  <Stream: itag="249" mime_type="audio/webm" abr="50kbps" acodec="opus">,
  <Stream: itag="250" mime_type="audio/webm" abr="70kbps" acodec="opus">,
  <Stream: itag="251" mime_type="audio/webm" abr="160kbps" acodec="opus">]
```

To list only ``mp4`` streams:

```python
>>> yt.streams.filter(subtype='mp4')
 [<Stream: itag="22" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.64001F" acodec="mp4a.40.2">,
  <Stream: itag="18" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.42001E" acodec="mp4a.40.2">,
  <Stream: itag="137" mime_type="video/mp4" res="1080p" fps="30fps" vcodec="avc1.640028">,
  <Stream: itag="136" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.4d401f">,
  <Stream: itag="135" mime_type="video/mp4" res="480p" fps="30fps" vcodec="avc1.4d401e">,
  <Stream: itag="134" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.4d401e">,
  <Stream: itag="133" mime_type="video/mp4" res="240p" fps="30fps" vcodec="avc1.4d4015">,
  <Stream: itag="160" mime_type="video/mp4" res="144p" fps="30fps" vcodec="avc1.4d400c">,
  <Stream: itag="140" mime_type="audio/mp4" abr="128kbps" acodec="mp4a.40.2">]
```

Multiple filters can also be specified:

```python
>>> yt.streams.filter(subtype='mp4', progressive=True)
>>> # this can also be expressed as:
>>> yt.streams.filter(subtype='mp4').filter(progressive=True)
  [<Stream: itag="22" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.64001F" acodec="mp4a.40.2">,
  <Stream: itag="18" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.42001E" acodec="mp4a.40.2">]
```
You also have an interface to select streams by their itag, without needing to filter:

```python
>>> yt.streams.get_by_itag(22)
  <Stream: itag="22" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.64001F" acodec="mp4a.40.2">
```

If you need to optimize for a specific feature, such as the "highest resolution" or "lowest average bitrate":

```python
>>> yt.streams.filter(progressive=True).order_by('resolution').desc()
```
Note: Using ``order_by`` on a given attribute will filter out all streams missing that attribute.

### Callbacks

If your application requires post-processing logic, pytube allows you to specify an "on download complete" callback function:

```python
 >>> def convert_to_aac(stream: Stream, file_path: str):
         return  # do work

 >>> yt.register_on_complete_callback(convert_to_aac)
```

Similarly, if your application requires on-download progress logic, pytube exposes a callback for this as well:

```python
 >>> def show_progress_bar(stream: Stream, chunk: bytes, bytes_remaining: int):
         return  # do work

 >>> yt.register_on_progress_callback(show_progress_bar)
```

## Command-line interface

pytube3 ships with a simple CLI interface for downloading videos, playlists, and captions.

Let's start with downloading:

```bash
$ pytube3 http://youtube.com/watch?v=9bZkp7q19f0 --itag=18
```
To view available streams:

```bash
$ pytube3 http://youtube.com/watch?v=9bZkp7q19f0 --list
```

The complete set of flags are:

```
usage: pytube3 [-h] [--version] [--itag ITAG] [-r RESOLUTION] [-l] [-v]
               [--build-playback-report] [-c [CAPTION_CODE]] [-t TARGET]
               [-a [AUDIO]] [-f [FFMPEG]]
               [url]

Command line application to download youtube videos.

positional arguments:
  url                   The YouTube /watch or /playlist url

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --itag ITAG           The itag for the desired stream
  -r RESOLUTION, --resolution RESOLUTION
                        The resolution for the desired stream
  -l, --list            The list option causes pytube cli to return a list of
                        streams available to download
  -v, --verbose         Verbosity level, use up to 4 to increase logging -vvvv
  --build-playback-report
                        Save the html and js to disk
  -c [CAPTION_CODE], --caption-code [CAPTION_CODE]
                        Download srt captions for given language code. Prints
                        available language codes if no argument given
  -t TARGET, --target TARGET
                        The output directory for the downloaded stream.
                        Default is current working directory
  -a [AUDIO], --audio [AUDIO]
                        Download the audio for a given URL at the highest
                        bitrate availableDefaults to mp4 format if none is
                        specified
  -f [FFMPEG], --ffmpeg [FFMPEG]
                        Downloads the audio and video stream for resolution
                        providedIf no resolution is provided, downloads the
                        best resolutionRuns the command line program ffmpeg to
                        combine the audio and video
```


## Development

<a href="https://deepsource.io/gh/hbmartin/pytube3/?ref=repository-badge" target="_blank"><img alt="DeepSource" title="DeepSource" src="https://static.deepsource.io/deepsource-badge-light-mini.svg"></a>
<a href="https://www.codacy.com/manual/hbmartin/pytube3?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=hbmartin/pytube3&amp;utm_campaign=Badge_Grade"><img src="https://api.codacy.com/project/badge/Grade/53794f06983a46829620b3284c6a5596"/></a>
<a href="https://github.com/ambv/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg" /></a>

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

To run code checking before a PR use ``make test``

#### Virtual environment

Virtual environment is setup with [pipenv](https://pipenv-fork.readthedocs.io/en/latest/) and can be automatically activated with [direnv](https://direnv.net/docs/installation.html)

#### Code Formatting

This project is linted with [pyflakes](https://github.com/PyCQA/pyflakes), formatted with [black](https://github.com/ambv/black), and typed with [mypy](https://mypy.readthedocs.io/en/latest/introduction.html)


#### Code of Conduct

Treat other people with helpfulness, gratitude, and consideration! See the [Python Community Code of Conduct](https://www.python.org/psf/codeofconduct/).

## GUIs and other libraries
* [YouTubeDownload](https://github.com/YouTubeDownload/YouTubeDownload) - Featured GUI frontend for pytube3
* [Pytube-GUI](https://github.com/GAO23/Pytube-GUI) - Simple GUI frontend for pytube3
* [StackOverflow questions](https://stackoverflow.com/questions/tagged/pytube)
* [PySlackers](https://pyslackers.com/web) - Python Slack group