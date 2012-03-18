python-youtube-downloader
=========================
Still needs a bit of cleaning up, and has a couple bugs, not bad for a
couple hours of hackin'. I should have them fixed quickly though. Enjoy!

TODO
----
1. Finish writing the docstrings.
2. Fix the known bugs.
3. Add a couple small features, like output path.
4. Write unit tests.
5. Add setup.py.
6. Remove requests, its a single GET request - I think urllib2 should suffice.

Installation
------------
1. pip install requests
2. guess that's it.. add it to your PYTHON PATH if you'd like.

Usage example
-------------
::

    >>> from youtube import YouTube
    >>> yt = YouTube()
    >>> yt.url = "http://www.youtube.com/watch?v=oHg5SJYRHA0"

    >>> # View all encoding/quality options.
    >>> yt.videos
    [<Video: flv - 360p>, <Video: mp4 - 360p>, <Video: flv - 224p>]

    >>> # Similar to the Django ORM, you can filter.
    >>> yt.filter('flv')
    [<Video: flv - 360p>, <Video: flv - 224p>]

    >>> yt.filter(res='360p')
    [<Video: flv - 360p>, <Video: mp4 - 360p>]

    >>> # You can even use get()
    >>> rick_astley = yt.get('mp4')

    >>> # Okay, let's download!
    >>> rick_astley.download()
    Downloading: RickRollD.mp4 Bytes: 10407900
    2449408  [23.53%]
