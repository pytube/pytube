<div align="center">
  <p>
  <img src="https://assets.nickficano.com/gh-pytube.min.svg" width="456" height="143" alt="pytube logo" />
  </p>
  <p align="center">
	  <img src="https://img.shields.io/pypi/v/pytube.svg" alt="pypi">
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

## Getting Started

We have extensive documentation for how to use the code on
[readthedocs](https://python-pytube.readthedocs.io), and highly recommend
checking that out for most use cases!
