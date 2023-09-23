.. _exceptions:

Exception handling
==================

Pytube implements a number of useful exceptions for handling program flow.
There are a number of cases where pytube simply cannot access videos on YouTube
and relies on the user to handle these exceptions. Generally speaking, if a
video is unaccessible for any reason, this can be caught with the generic
VideoUnavailable exception. This could be used, for example, to skip private
videos in a playlist, videos that are region-restricted, and more.

Let's see what your code might look like if you need to do exception handling::

    >>> from pytube import Playlist, YouTube
    >>> from pytube.exceptions import VideoUnavailable
    >>> playlist_url = 'https://youtube.com/playlist?list=special_playlist_id'
    >>> p = Playlist(playlist_url)
    >>> for url in p.video_urls:
    ...     try:
    ...         yt = YouTube(url)
    ...     except VideoUnavailable:
    ...         print(f'Video {url} is unavaialable, skipping.')
    ...     else:
    ...         print(f'Downloading video: {url}')
    ...         yt.streams.first().download()

This will automatically skip over videos that could not be downloaded due to a
limitation with the pytube library. You can find more details about what
specific exceptions can be handled here: :py:mod:`pytube.exceptions`.
