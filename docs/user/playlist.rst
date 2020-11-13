.. _install:

Using Playlists
===============

This guide will walk you through the basics of working with pytube Playlists.

Creating a Playlist
-------------------

Using pytube to interact with playlists is very simple. 
Begin by importing the Playlist class::

    >>> from pytube import Playlist

Now let's create a playlist object. You can do this by initializing the object with a playlist URL::

    >>> p = Playlist('https://www.youtube.com/playlist?list=PLS1QulWo1RIaJECMeUT4LFwJ-ghgoSH6n')

Or you can create one from a video link in a playlist::

    >>> p = Playlist('https://www.youtube.com/watch?v=41qgdwd3zAg&list=PLS1QulWo1RIaJECMeUT4LFwJ-ghgoSH6n')

Now, we have a :class:`Playlist <pytube.Playlist>` object called ``p`` that we can do some work with.

Interacting with a playlist
---------------------------

Fundamentally, a Playlist object is just a container for YouTube objects.

If, for example, we wanted to download all of the videos in a playlist, we would do the following::

    >>> print(f'Downloading: {p.title}')
    Downloading: Python Tutorial for Beginers (For Absolute Beginners)
    >>> for video in p.videos:
    >>>     video.streams.first().download()

Or, if we're only interested in the URLs for the videos, we can look at those as well::

    >>> for url in p.video_urls[:3]:
    >>>     print(url)
    Python Tutorial for Beginers 1 - Getting Started and Installing Python (For Absolute Beginners)
    Python Tutorial for Beginers 2 - Numbers and Math in Python
    Python Tutorial for Beginers 3 - Variables and Inputs

And that's basically all there is to it! The Playlist class is relatively straightforward.