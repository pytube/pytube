======
pytube
======

A lightweight, dependency-free Python library for downloading YouTube Videos.

Description
===========

Downloading videos from YouTube shouldn't require some bloatware application,
it's usually a niche condition you want to do so in the first place. So I
present to you, PyTube!

Requirements
============

- Python 2.6+ (2.7 or 3.4 recommended)
- PIP (for some installation methods)
- GIT (for some installation methods)

Installation
============

If you are on Mac OS X or Linux, chances are that one of the following two commands will work for you:

Using PIP via PyPI

.. code:: bash

    pip install pytube

Using PIP via Github

.. code:: bash

    pip install git+git://github.com/NFicano/pytube.git@0.3.1#egg=pytube

Adding to your ``requirements.txt`` file (run ``pip install -r requirements.txt`` afterwards)

.. code:: bash

    git+ssh://git@github.com/NFicano/pytube.git@0.3.1#egg=pytube

Manually via GIT

.. code:: bash

    git clone git://github.com/NFicano/pytube.git pytube
    cd pytube
    python setup.py install

Roadmap
=======

The only features I see implementing in the near future are:

- refactor console printing into separate command-line utility.
- Add nosetests
- Add Sphinx documentation

Usage Example
=============

.. code:: python

    from pytube import YouTube

    # not necessary, just for demo purposes
    from pprint import pprint

    yt = YouTube()

    # Set the video URL.
    yt.from_url("http://www.youtube.com/watch?v=Ik-RsDGPI5Y")

    # Once set, you can see all the codec and quality options YouTube has made
    # available for the perticular video by printing videos.

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

    # The filename is automatically generated based on the video title.
    # You can override this by manually setting the filename.

    # view the auto generated filename:
    from __future__ import print_function
    print(yt.filename)

    #Pulp Fiction - Dancing Scene [HD]

    # set the filename:
    yt.set_filename('Dancing Scene from Pulp Fiction')

    # You can also filter the criteria by filetype.

    pprint(yt.filter('flv'))

    #[<Video: Sorenson H.263 (.flv) - 240p>,
    # <Video: H.264 (.flv) - 360p>,
    # <Video: H.264 (.flv) - 480p>]

    # notice that the list is ordered by lowest resolution to highest. If you
    # wanted the highest resolution available for a specific file type, you
    # can simply do:
    print(yt.filter('mp4')[-1])
    #<Video: H.264 (.mp4) - 720p>

    # you can also get all videos for a given resolution
    pprint(yt.filter(resolution='480p'))

    #[<Video: H.264 (.flv) - 480p>,
    #<Video: VP8 (.webm) - 480p>]

    # to select a video by a specific resolution and filetype you can use the get
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

    # Notice we have two H.264 (.mp4) available to us.. now if we try to call get()
    # on mp4..

    video = yt.get('mp4')
    # MultipleObjectsReturned: get() returned more than one object -- it returned 2!

    # In this case, we'll need to specify both the codec (mp4) and resolution
    # (either 360p or 720p).

    # Okay, let's download it!
    video.download()

    # Downloading: Pulp Fiction - Dancing Scene.mp4 Bytes: 37561829
    # 37561829  [100.00%]

    # Note: If you wanted to choose the output directory, simply pass it as an
    # argument to the download method.
    video.download('/tmp/')


Background
==========

After missing the deadline to register for PyCon 2012, I decided to write what
became PyTube and crawler to collect all the YouTube links for the talks
on PyVideos_.

To avoid having to encode them to mp4 (so I could watch them on my iPhone)
I wrote it so you could specify an encoding format.

In recently weeks interest has picked up in the project, so I decided to
dedicate more time to further its development and actively maintain it.

Philosophy
==========

My only real goal for this is to never require any third party dependancies,
to keep it simple and make it reliable.

.. _PyVideos: http://pyvideo.org/
