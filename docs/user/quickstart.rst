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


Working with Streams
====================

The next section will explore the various options available for working with media
streams, but before we can dive in, we need to review a new-ish streaming technique
adopted by YouTube.

DASH vs Progressive Streams
---------------------------

Begin by running the following::

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

Query audio only Streams
------------------------

To query the streams that contain only the audio track::

    >>> yt.streams.filter(only_audio=True).all()
    [<Stream: itag="140" mime_type="audio/mp4" abr="128kbps" acodec="mp4a.40.2">,
    <Stream: itag="171" mime_type="audio/webm" abr="128kbps" acodec="vorbis">]

Query MPEG-4 Streams
--------------------

To query only streams in the MPEG-4 format::

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

Get Streams by itag
-------------------

To get a stream by a specific itag::

    >>> yt.streams.get_by_itag('22')
    <Stream: itag="22" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.64001F" acodec="mp4a.40.2">

Subtitle/Caption Tracks
=======================

Pytube exposes the caption tracks in much the same way as querying the media
streams. Let's begin by switching to a video that contains them::

    >>> yt = YouTube('https://youtube.com/watch?v=XJGiS83eQLk')
    >>> yt.captions.all()
    [<Caption lang="Arabic" code="ar">,
    <Caption lang="English (auto-generated)" code="en">,
    <Caption lang="English" code="en">,
    <Caption lang="English (United Kingdom)" code="en-GB">,
    <Caption lang="German" code="de">,
    <Caption lang="Greek" code="el">,
    <Caption lang="Indonesian" code="id">,
    <Caption lang="Sinhala" code="si">,
    <Caption lang="Spanish" code="es">,
    <Caption lang="Turkish" code="tr">]

Now let's checkout the english captions::

    >>> caption = yt.captions.get_by_language_code('en')

Great, now let's see how YouTube formats them::

    >>> caption.xml_captions
    '<?xml version="1.0" encoding="utf-8" ?><transcript><text start="0" dur="5.541">well i&amp;#39...'

Oh, this isn't very easy to work with, let's convert them to the srt format::

    >>> print(caption.generate_srt_captions())
    1
    000:000:00,000 --> 000:000:05,541
    well i'm just an editor and i dont know what to type

    2
    000:000:05,541 --> 000:000:12,321
    not new to video. In fact, most films before 1930 were silent and used captions with video

    ...
