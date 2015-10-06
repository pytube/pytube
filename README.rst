======
pytube
======

.. image:: https://travis-ci.org/nficano/pytube.svg?branch=master
   :alt: Build status
   :target: https://travis-ci.org/nficano/pytube

*pytube* is a lightweight, dependency-free Python library (and cli) for downloading YouTube Videos.

Description
===========

Downloading videos from YouTube shouldn't require some bloated library, it's
unusual to have to do so in the first place. So I present to you, PyTube!

Requirements
============

- Python 2.6+ (2.7 or 3.4 recommended)
- PIP (for some installation methods)
- GIT (for some installation methods)

Installation
============

If you are on Mac OS X or Linux, chances are that one of the following two
commands will work for you:

Using PIP via PyPI

.. code:: bash

    pip install pytube

Using PIP via Github

.. code:: bash

    pip install git+git://github.com/nficano/pytube#egg=pytube

Adding to your ``requirements.txt`` file (run ``pip install -r requirements.txt`` afterwards)

.. code:: bash

    git+ssh://git@github.com/nficano/pytube#egg=pytube

Manually via GIT

.. code:: bash

    git clone git://github.com/NFicano/pytube pytube
    cd pytube
    python setup.py install


Command-Line Usage
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

   $ pytube -e mp4 -f Dancing Scene from Pulp Fiction http://www.youtube.com/watch?v=Ik-RsDGPI5Y



Library Usage
=============

.. code:: python

    from pytube import YouTube

    # not necessary, just for demo purposes
    from pprint import pprint

    yt = YouTube("http://www.youtube.com/watch?v=Ik-RsDGPI5Y")

    # Once set, you can see all the codec and quality options YouTube has made
    # available for the perticular video by printing videos.

    pprint(yt.get_videos())

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
    pprint(yt.filter('flv'))

    # [<Video: Sorenson H.263 (.flv) - 240p>,
    #  <Video: H.264 (.flv) - 360p>,
    #  <Video: H.264 (.flv) - 480p>]

    # Notice that the list is ordered by lowest resolution to highest. If you
    # wanted the highest resolution available for a specific file type, you
    # can simply do:
    print(yt.filter('mp4')[-1])
    # <Video: H.264 (.mp4) - 720p>

    # You can also get all videos for a given resolution
    pprint(yt.filter(resolution='480p'))

    # [<Video: H.264 (.flv) - 480p>,
    # <Video: VP8 (.webm) - 480p>]

    # To select a video by a specific resolution and filetype you can use the get
    # method.

    video = yt.get('mp4', '720p')

    # NOTE: get() can only be used if and only if one object matches your criteria.
    # for example:

    pprint(yt.videos)

    #[<Video: MPEG-4 Visual (.3gp) - 144p>,
    # <Video: MPEG-4 Visual (.3gp) - 240p>,
    # <Video: Sorenson H.263 (.flv) - 240p>,
    # <Video: H.264 (.flv) - 360p>,
    # <Video: H.264 (.flv) - 480p>,
    # <Video: H.264 (.mp4) - 360p>,
    # <Video: H.264 (.mp4) - 720p>,
    # <Video: VP8 (.webm) - 360p>,
    # <Video: VP8 (.webm) - 480p>]

    # Notice we have two H.264 (.mp4) available to us... now if we try to call get()
    # on mp4...

    video = yt.get('mp4')
    # MultipleObjectsReturned: 2 videos met criteria.

    # In this case, we'll need to specify both the codec (mp4) and resolution
    # (either 360p or 720p).

    # Okay, let's download it!
    video.download()

    # Note: If you wanted to choose the output directory, simply pass it as an
    # argument to the download method.
    video.download('/tmp/')
