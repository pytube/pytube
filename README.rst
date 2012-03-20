python-youtube-downloader
=========================
Still needs a bit of cleaning up, and has a couple bugs, not bad for a
couple hours of hackin'. I should have them fixed quickly though. Enjoy!

TODO
----
1. Add a couple small features, like output path.
2. Write unit tests.
3. Add setup.py.

Installation
------------
1. Add it to your PYTHON PATH if you'd like, not much to her.

Usage example
-------------
::

    >>> from youtube import YouTube
    >>> yt = YouTube()
    >>> yt.url = "http://www.youtube.com/watch?v=Ik-RsDGPI5Y"

    >>> # View all encoding/quality options.
    >>> yt.videos
    [<Video: mp4 - 720p>,
    <Video: webm - 480p>,
    <Video: flv - 480p>,
    <Video: webm - 360p>,
    <Video: flv - 360p>,
    <Video: mp4 - 360p>,
    <Video: flv - 224p>]

    >>> #Set the filename, or get the default.
    >>> yt.filename
    'Pulp Fiction - Dancing Scene'

    >>> # Similar to the Django ORM, you can filter.
    >>> yt.filter('flv')
    [<Video: flv - 480p>, <Video: flv - 360p>, <Video: flv - 224p>]

    >>> yt.filter(res='480p')
    [<Video: webm - 480p>, <Video: flv - 480p>]

    >>> # You can even use get()
    >>> video = yt.get('mp4', '720p')

    >>> # Okay, let's download!
    >>> video.download()
    Downloading: Pulp Fiction - Dancing Scene.mp4 Bytes: 37561829
    37561829  [100.00%]
