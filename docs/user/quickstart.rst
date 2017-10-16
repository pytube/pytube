.. _quickstart:

Quickstart
==========

This guide will walk you through the basic usage of pytube.

Let's get started with some examples.

Downloading a Video
-------------------

Downloading a video from YouTube with pytube is incredibly easy.

Begin by importing the YouTube class::

    >>> from pytube import YouTube


Now, let's try to download a video. For this example, let's take something
popular like PSY - Gangnam Style::

    >>> stream = YouTube('https://www.youtube.com/watch?v=9bZkp7q19f0')

Now, we have a :class:`YouTube <pytube.YouTube>` object called ``stream``. We
can get all the information we need from this object.

The pytube API makes all forms of stream information intuitive to access. For
example, this is how you would get the video's title::

    >>> stream.title
    PSY - GANGNAM STYLE(강남스타일) M/V
