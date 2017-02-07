======
pytube
======

.. image:: https://img.shields.io/pypi/v/pytube.svg
  :alt: Pypi
  :target: https://pypi.python.org/pypi/pytube/

.. image:: https://img.shields.io/pypi/pyversions/pytube.svg
  :alt: Python Versions
  :target: https://pypi.python.org/pypi/pytube/

.. image:: https://travis-ci.org/nficano/pytube.svg?branch=master
   :alt: Build status
   :target: https://travis-ci.org/nficano/pytube

.. image:: https://coveralls.io/repos/nficano/pytube/badge.svg?branch=master&service=github
  :alt: Coverage
  :target: https://coveralls.io/github/nficano/pytube?branch=master

*pytube* is a lightweight, dependency-free Python library (and command-line utility) for downloading YouTube Videos.

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

    from pytube import YouTube

    # not necessary, just for demo purposes.
    from pprint import pprint

    yt = YouTube("http://www.youtube.com/watch?v=Ik-RsDGPI5Y")

    # Once set, you can see all the codec and quality options YouTube has made
    # available for the perticular video by printing videos.

    print(yt.get_videos())

    # [<Video: MPEG-4 Visual (.3gp) - 144p>,
    #  <Video: MPEG-4 Visual (.3gp) - 240p>,
    #  <Video: Sorenson H.263 (.flv) - 240p>,
    #  <Video: H.264 (.flv) - 360p>,
    #  <Video: H.264 (.flv) - 480p>,
    #  <Video: H.264 (.mp4) - 360p>,
    #  <Video: H.264 (.mp4) - 720p>,
    #  <Video: VP8 (.webm) - 360p>,
    #  <Video: VP8 (.webm) - 480p>]

    # The filename is automatically generated based on the video title.  You
    # can override this by manually setting the filename.

    # view the auto generated filename:
    print(yt.filename)

    # Pulp Fiction - Dancing Scene [HD]

    # set the filename:
    yt.set_filename('Dancing Scene from Pulp Fiction')

    # You can also filter the criteria by filetype.
    print(yt.filter('flv'))

    # [<Video: Sorenson H.263 (.flv) - 240p>,
    #  <Video: H.264 (.flv) - 360p>,
    #  <Video: H.264 (.flv) - 480p>]

    # Notice that the list is ordered by lowest resolution to highest. If you
    # wanted the highest resolution available for a specific file type, you
    # can simply do:
    print(yt.filter('mp4')[-1])
    # <Video: H.264 (.mp4) - 720p>

    # You can also get all videos for a given resolution
    print(yt.filter(resolution='480p'))

    # [<Video: H.264 (.flv) - 480p>,
    #  <Video: VP8 (.webm) - 480p>]

    # To select a video by a specific resolution and filetype you can use the get
    # method.

    video = yt.get('mp4', '720p')

    # NOTE: get() can only be used if and only if one object matches your criteria.
    # for example:

    print(yt.videos)

    #[<Video: MPEG-4 Visual (.3gp) - 144p>,
    # <Video: MPEG-4 Visual (.3gp) - 240p>,
    # <Video: Sorenson H.263 (.flv) - 240p>,
    # <Video: H.264 (.flv) - 360p>,
    # <Video: H.264 (.flv) - 480p>,
    # <Video: H.264 (.mp4) - 360p>,
    # <Video: H.264 (.mp4) - 720p>,
    # <Video: VP8 (.webm) - 360p>,
    # <Video: VP8 (.webm) - 480p>]

    # Since we have two H.264 (.mp4) available to us... now if we try to call get()
    # on mp4...

    video = yt.get('mp4')
    # MultipleObjectsReturned: 2 videos met criteria.

    # In this case, we'll need to specify both the codec (mp4) and resolution
    # (either 360p or 720p).

    # Okay, let's download it! (a destination directory is required)
    video.download('/tmp/')

Command-line usage
==================

You can download a video by simply passing the ``-e`` (or ``--extension=``) switch and
setting it to the desired filetype:

.. code:: bash

   $ pytube -e mp4 http://www.youtube.com/watch?v=Ik-RsDGPI5Y


Same thing for specifying a resolution:

.. code:: bash

   $ pytube -r 720p http://www.youtube.com/watch?v=Ik-RsDGPI5Y


You can also specify a download file path (``-p`` or ``--path=``):

.. code:: bash

   $ pytube -e mp4 -p ~/Downloads/ http://www.youtube.com/watch?v=Ik-RsDGPI5Y

and/or optionally choose the filename (``-f`` or ``--filename=``):

.. code:: bash

   $ pytube -e mp4 -f "Dancing Scene from Pulp Fiction" http://www.youtube.com/watch?v=Ik-RsDGPI5Y

You can also specify a resolution or desired filetype:

.. code:: bash

   $ pytube -e mp4 -r 720p http://www.youtube.com/watch?v=Ik-RsDGPI5Y
