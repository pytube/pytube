<div align="center">
  <p>
    <a href="#"><img src="https://assets.nickficano.com/gh-pytube.min.svg" width="456" height="143" alt="pytube logo" /></a>
  </p>
  <p align="center">
	<a href="https://pypi.org/project/pytube/"><img src="https://img.shields.io/pypi/dm/pytube?style=flat-square" alt="pypi"/></a>
	<a href="https://pytube.io/en/latest/"><img src="https://readthedocs.org/projects/python-pytube/badge/?version=latest&style=flat-square" /></a>
	<a href="https://pypi.org/project/pytube/"><img src="https://img.shields.io/pypi/v/pytube?style=flat-square" /></a>
  </p>
</div>

### Actively soliciting contributors!

Have ideas for how pytube can be improved? Feel free to open an issue or a pull request!

# pytube

*pytube* is a genuine, lightweight, dependency-free Python library (and command-line utility) for downloading YouTube videos.

## Documentation

Detailed documentation about the usage of the library can be found at [pytube.io](https://pytube.io). This is recommended for most cases. If you want to hastily download a single video, the [quick start](#Quickstart) guide below might be what you're looking for.

## Description

YouTube is the most popular video-sharing platform in the world and as a hacker, you may encounter a situation where you want to script something to download videos. For this, I present to you: *pytube*.

*pytube* is a lightweight library written in Python. It has no third-party
dependencies and aims to be highly reliable.

*pytube* also makes pipelining easy, allowing you to specify callback functions for different download events, such as  ``on progress`` or ``on complete``.

Furthermore, *pytube* includes a command-line utility, allowing you to download videos right from the terminal.

## Features

- Support for both progressive & DASH streams
- Support for downloading the complete playlist
- Easily register ``on_download_progress`` & ``on_download_complete`` callbacks
- Command-line interfaced included
- Caption track support
- Outputs caption tracks to .srt format (SubRip Subtitle)
- Ability to capture thumbnail URL
- Extensively documented source code
- No third-party dependencies

## Quickstart

This guide covers the most basic usage of the library. For more detailed information, please refer to [pytube.io](https://pytube.io).

### Installation

Pytube requires an installation of Python 3.6 or greater, as well as pip. (Pip is typically bundled with Python [installations](https://python.org/downloads).)

To install from PyPI with pip:

```bash
$ python -m pip install pytube
```

Sometimes, the PyPI release becomes slightly outdated. To install from the source with pip:

```bash
$ python -m pip install git+https://github.com/pytube/pytube
```

### Using pytube in a Python script

To download a video using the library in a script, you'll need to import the YouTube class from the library and pass an argument of the video URL. From there, you can access the streams and download them.

```python
 >>> from pytube import YouTube
 >>> YouTube('https://youtu.be/2lAe1cqCOXo').streams.first().download()
 >>> yt = YouTube('http://youtube.com/watch?v=2lAe1cqCOXo')
 >>> yt.streams
  ... .filter(progressive=True, file_extension='mp4')
  ... .order_by('resolution')
  ... .desc()
  ... .first()
  ... .download()
```

### Using the command-line interface

Using the CLI is remarkably straightforward as well. To download a video at the highest progressive quality, you can use the following command:
```bash
$ pytube https://youtube.com/watch?v=2lAe1cqCOXo
```

You can also do the same for a playlist:
```bash
$ pytube https://www.youtube.com/playlist?list=PLS1QulWo1RIaJECMeUT4LFwJ-ghgoSH6n
```
