======
pytube
======

.. image:: https://img.shields.io/pypi/v/pytube.svg
  :alt: Pypi
  :target: https://pypi.python.org/pypi/pytube/

.. image:: https://travis-ci.org/nficano/pytube.svg?branch=master
   :alt: Build status
   :target: https://travis-ci.org/nficano/pytube

.. image:: https://coveralls.io/repos/nficano/pytube/badge.svg?branch=master&service=github
  :alt: Coverage
  :target: https://coveralls.io/github/nficano/pytube?branch=master

*pytube* is a lightweight, dependency-free Python library (and command-line utility) for downloading YouTube Videos.

A call for contributors
=======================
With pytube and `python-lambda <https://github.com/nficano/python-lambda/>`_ both continuing to gain momentum, I'm calling for contributors to help build out new features, review pull requests, fix bugs, and maintain overall code quality. If you're interested, please email me at nficano[at]gmail.com.

Description
===========

YouTube is the most popular video-sharing platform in the world and as a hacker you may encounter a situation where you want to script something to download videos.  For this I present to you *pytube*.

*pytube* is a lightweight library written in Python. It has no third party dependencies and aims to be highly reliable.

*pytube* makes *zero assumptions*, meaning there is no built-in method to get say the *"best"* quality video, *pytube* simply exposes all the available formats and resolutions, giving you the developer the power to define what *"best"* is.

*pytube* also makes pipelining easy, allowing you to specify callback functions for different download events, such as  ``on progress`` or ``on complete``.

Finally *pytube* also includes a command-line utility, allowing you to quickly download videos right from terminal.

Installation
============

Download using pip via pypi.

.. code:: bash

    pip install pytube


Library usage
=============

.. code:: python

   >>> from pytube import YouTube

   >>> yt = YouTube("http://www.youtube.com/watch?v=9bZkp7q19f0")

   >>> # Once set, you can see all the codec and quality options YouTube has made
   >>> # available for the particular video by printing videos.

   >>> yt.streams.all()
   [<Stream: itag="22" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.64001F" acodec="mp4a.40.2">,
   <Stream: itag="43" mime_type="video/webm" res="360p" fps="30fps" vcodec="vp8.0" acodec="vorbis">,
   <Stream: itag="18" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.42001E" acodec="mp4a.40.2">,
   <Stream: itag="36" mime_type="video/3gpp" res="240p" fps="30fps" vcodec="mp4v.20.3" acodec="mp4a.40.2">,
   <Stream: itag="17" mime_type="video/3gpp" res="144p" fps="30fps" vcodec="mp4v.20.3" acodec="mp4a.40.2">]

   >>> # for dash streams
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

   >>> # You can also filter the criteria by filetype.
   >>> yt.dash_streams.filter(audio_codec='opus').all()
   [<Stream: itag="249" mime_type="audio/webm" abr="50kbps" acodec="opus">,
   <Stream: itag="250" mime_type="audio/webm" abr="70kbps" acodec="opus">,
   <Stream: itag="251" mime_type="audio/webm" abr="160kbps" acodec="opus">]

   >>> # Notice that the list is ordered by lowest resolution to highest. If you
   >>> # wanted the highest resolution available for a specific file type, you
   >>> # can do:
   >>> yt.dash_streams.first()
   <Stream: itag="137" mime_type="video/mp4" res="1080p" fps="30fps" vcodec="avc1.640028">

   >>> # You can also get all videos for a given resolution
   >>> yt.dash_streams.filter(resolution='720p').all()
   [<Stream: itag="136" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.4d401f">,
   <Stream: itag="247" mime_type="video/webm" res="720p" fps="30fps" vcodec="vp9">]

   >>> # To select a video by a specific itag you can use the get method.
   >>> yt.dash_streams.get(251)
   <Stream: itag="251" mime_type="audio/webm" abr="160kbps" acodec="opus">

   >>> # Okay, let's download it!
   >>> yt.dash_streams.get(251).download()

Command-line usage
==================

You can download a video by simply passing the ``--itag`` switch:

.. code:: bash

   $ pytube http://www.youtube.com/watch?v=Ik-RsDGPI5Y --itag=22


To list all available formats use the ``--list`` switch:

.. code:: bash

   $ pytube http://www.youtube.com/watch?v=Ik-RsDGPI5Y

Development
===========

Development of "pytube" is facilitated exclusively on GitHub. Contributions in the form of patches, tests and feature creation and/or requests are very welcome and highly encouraged. Please open an issue if this tool does not function as you'd expect.


How to release updates
----------------------

If this is the first time you're releasing to pypi, you'll need to run: ``pip install -r tests/dev_requirements.txt``.

Once complete, execute the following commands:

.. code:: bash

   git checkout master

   # Increment the version number and tag the release.
   bumpversion [major|minor|patch]

   # Upload the distribution to PyPi
   python setup.py sdist bdist_wheel upload

   # Since master often contains work-in-progress changes, increment the version
   # to a patch release to prevent inaccurate attribution.
   bumpversion --no-tag patch

   git push origin master --tags
