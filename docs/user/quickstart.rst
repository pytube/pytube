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

    >>> yt = YouTube('https://www.youtube.com/watch?v=9bZkp7q19f0')

Now, we have a :class:`YouTube <pytube.YouTube>` object called ``yt``.

The pytube API makes all information intuitive to access. For example, this is
how you would get the video's title::

    >>> yt.title
    PSY - GANGNAM STYLE(강남스타일) M/V

And this would be how you would get the thumbnail url::

    >>> yt.thumbnail_url
    'https://i.ytimg.com/vi/mTOYClXhJD0/default.jpg'

Neat, right? Next let's see the available media formats::

    >>> yt.streams.all()
    [<Stream: itag="22" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.64001F" acodec="mp4a.40.2">,
    <Stream: itag="43" mime_type="video/webm" res="360p" fps="30fps" vcodec="vp8.0" acodec="vorbis">,
    <Stream: itag="18" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.42001E" acodec="mp4a.40.2">,
    <Stream: itag="36" mime_type="video/3gpp" res="240p" fps="30fps" vcodec="mp4v.20.3" acodec="mp4a.40.2">,
    <Stream: itag="17" mime_type="video/3gpp" res="144p" fps="30fps" vcodec="mp4v.20.3" acodec="mp4a.40.2">,
    <Stream: itag="137" mime_type="video/mp4" res="1080p" fps="30fps" vcodec="avc1.640028">,
    <Stream: itag="136" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.4d401f">,
    <Stream: itag="135" mime_type="video/mp4" res="480p" fps="30fps" vcodec="avc1.4d401f">,
    <Stream: itag="134" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.4d401e">,
    <Stream: itag="133" mime_type="video/mp4" res="240p" fps="30fps" vcodec="avc1.4d4015">,
    <Stream: itag="160" mime_type="video/mp4" res="144p" fps="30fps" vcodec="avc1.4d400c">,
    <Stream: itag="140" mime_type="audio/mp4" abr="128kbps" acodec="mp4a.40.2">,
    <Stream: itag="171" mime_type="audio/webm" abr="128kbps" acodec="vorbis">]

Let's say we want to get the first stream::

    >>> stream = yt.streams.first()
    >>> stream
    <Stream: itag="22" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.64001F" acodec="mp4a.40.2">

And to download it to the current working directory::

    >>> stream.download()

You can also specify a destination path::

    >>> stream.download('/tmp')


Working with streams
--------------------

Now let's explore the various options available for filtering streams. Begin by
running the following again (*note these results can change over time*)::

    >>> yt.streams.all()
    [<Stream: itag="22" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.64001F" acodec="mp4a.40.2">,
    <Stream: itag="43" mime_type="video/webm" res="360p" fps="30fps" vcodec="vp8.0" acodec="vorbis">,
    <Stream: itag="18" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.42001E" acodec="mp4a.40.2">,
    <Stream: itag="36" mime_type="video/3gpp" res="240p" fps="30fps" vcodec="mp4v.20.3" acodec="mp4a.40.2">,
    <Stream: itag="17" mime_type="video/3gpp" res="144p" fps="30fps" vcodec="mp4v.20.3" acodec="mp4a.40.2">,
    <Stream: itag="137" mime_type="video/mp4" res="1080p" fps="30fps" vcodec="avc1.640028">,
    <Stream: itag="136" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.4d401f">,
    <Stream: itag="135" mime_type="video/mp4" res="480p" fps="30fps" vcodec="avc1.4d401f">,
    <Stream: itag="134" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.4d401e">,
    <Stream: itag="133" mime_type="video/mp4" res="240p" fps="30fps" vcodec="avc1.4d4015">,
    <Stream: itag="160" mime_type="video/mp4" res="144p" fps="30fps" vcodec="avc1.4d400c">,
    <Stream: itag="140" mime_type="audio/mp4" abr="128kbps" acodec="mp4a.40.2">,
    <Stream: itag="171" mime_type="audio/webm" abr="128kbps" acodec="vorbis">]


You may notice that some streams listed have both a video codec and audio
codec, while others have just video or just audio, this is a result of YouTube
supporting a streaming technique called Dynamic Adaptive Streaming over HTTP
(DASH).

In the context of pytube, the implications are for the highest quality streams;
you now need to download both the audio and video tracks and then post-process
them with software like FFmpeg to merge them.

The legacy streams that contain the audio and video in a single file (referred
to as "progressive download") are still available, but only for resolutions
720p and below.

To only view these progressive download streams::

    >>> yt.streams.filter(progressive=True).all()
    [<Stream: itag="22" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.64001F" acodec="mp4a.40.2">,
    <Stream: itag="43" mime_type="video/webm" res="360p" fps="30fps" vcodec="vp8.0" acodec="vorbis">,
    <Stream: itag="18" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.42001E" acodec="mp4a.40.2">,
    <Stream: itag="36" mime_type="video/3gpp" res="240p" fps="30fps" vcodec="mp4v.20.3" acodec="mp4a.40.2">,
    <Stream: itag="17" mime_type="video/3gpp" res="144p" fps="30fps" vcodec="mp4v.20.3" acodec="mp4a.40.2">]

Conversely, if you only want to see the DASH streams (also referred to as
"adaptive") you can do::

    >>> yt.streams.filter(adaptive=True).all()
    [<Stream: itag="137" mime_type="video/mp4" res="1080p" fps="30fps" vcodec="avc1.640028">,
    <Stream: itag="136" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.4d401f">,
    <Stream: itag="135" mime_type="video/mp4" res="480p" fps="30fps" vcodec="avc1.4d401f">,
    <Stream: itag="134" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.4d401e">,
    <Stream: itag="133" mime_type="video/mp4" res="240p" fps="30fps" vcodec="avc1.4d4015">,
    <Stream: itag="160" mime_type="video/mp4" res="144p" fps="30fps" vcodec="avc1.4d400c">,
    <Stream: itag="140" mime_type="audio/mp4" abr="128kbps" acodec="mp4a.40.2">,
    <Stream: itag="171" mime_type="audio/webm" abr="128kbps" acodec="vorbis">]

Pytube allows you to filter on every property available (see
:py:meth:`pytube.StreamQuery.filter` for a complete list of filter options),
let's take a look at some common examples:

Query audio only streams
------------------------

To query the streams that contain only the audio track::

    >>> yt.streams.filter(only_audio=True).all()
    [<Stream: itag="140" mime_type="audio/mp4" abr="128kbps" acodec="mp4a.40.2">,
    <Stream: itag="171" mime_type="audio/webm" abr="128kbps" acodec="vorbis">]

Query mp4 streams
-----------------

To query the streams that are encoded as mp4::

    >>> yt.streams.filter(file_extension='mp4').all()
    [<Stream: itag="22" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.64001F" acodec="mp4a.40.2">,
    <Stream: itag="18" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.42001E" acodec="mp4a.40.2">,
    <Stream: itag="137" mime_type="video/mp4" res="1080p" fps="30fps" vcodec="avc1.640028">,
    <Stream: itag="136" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.4d401f">,
    <Stream: itag="135" mime_type="video/mp4" res="480p" fps="30fps" vcodec="avc1.4d401f">,
    <Stream: itag="134" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.4d401e">,
    <Stream: itag="133" mime_type="video/mp4" res="240p" fps="30fps" vcodec="avc1.4d4015">,
    <Stream: itag="160" mime_type="video/mp4" res="144p" fps="30fps" vcodec="avc1.4d400c">,
    <Stream: itag="140" mime_type="audio/mp4" abr="128kbps" acodec="mp4a.40.2">]
