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
like the YouTube Rewind video for 2019::

    >>> yt = YouTube('http://youtube.com/watch?v=2lAe1cqCOXo')

Now, we have a :class:`YouTube <pytube.YouTube>` object called ``yt``.

The pytube API makes all information intuitive to access. For example, this is
how you would get the video's title::

    >>> yt.title
    YouTube Rewind 2019: For the Record | #YouTubeRewind

And this would be how you would get the thumbnail url::

    >>> yt.thumbnail_url
    'https://i.ytimg.com/vi/2lAe1cqCOXo/maxresdefault.jpg'

Neat, right? For advanced use cases, you can provide some additional arguments
when you create a YouTube object::

    >>> yt = YouTube(
            'http://youtube.com/watch?v=2lAe1cqCOXo',
            on_progress_callback=progress_func,
            on_complete_callback=complete_func,
            proxies=my_proxies,
            use_oauth=False,
            allow_oauth_cache=True
        )

When instantiating a YouTube object, these named arguments can be passed in to
improve functionality. 

The on_progress_callback function will run whenever a chunk is downloaded from
a video, and is called with three arguments: the stream, the data chunk, and
the bytes remaining in the video. This could be used, for example, to display a
progress bar.

The on_complete_callback function will run after a video has been fully
downloaded, and is called with two arguments: the stream and the file path.
This could be used, for example, to perform post-download processing on a video
like trimming the length of it.

The use_oauth and allow_oauth_cache flags allow you to authorize pytube to
interact with YouTube using your account, and can be used to bypass age
restrictions or access private videos and playlists. If allow_oauth_cache is
set to True, you should only be prompted to do so once, after which point
pytube will cache the tokens it needs to act on your behalf. Otherwise, you
will be prompted again for each action that requires you to be authenticated.

Once you have a YouTube object set up, you're ready to start looking at
different media streams for the video, which is discussed in the next section.
