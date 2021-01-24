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

Neat, right? Next let's see the available media formats::

    >>> yt.streams
    [<Stream: itag="18" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.42001E" acodec="mp4a.40.2" progressive="True" type="video">,
    <Stream: itag="22" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.64001F" acodec="mp4a.40.2" progressive="True" type="video">,
    <Stream: itag="137" mime_type="video/mp4" res="1080p" fps="30fps" vcodec="avc1.640028" progressive="False" type="video">,
    ...
    <Stream: itag="250" mime_type="audio/webm" abr="70kbps" acodec="opus" progressive="False" type="audio">,
    <Stream: itag="251" mime_type="audio/webm" abr="160kbps" acodec="opus" progressive="False" type="audio">]

Let's say we want to get the first stream::

    >>> stream = yt.streams.first()
    >>> stream
    <Stream: itag="18" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.42001E" acodec="mp4a.40.2" progressive="True" type="video">

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

    >>> yt.streams
    [<Stream: itag="18" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.42001E" acodec="mp4a.40.2" progressive="True" type="video">,
    <Stream: itag="22" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.64001F" acodec="mp4a.40.2" progressive="True" type="video">,
    <Stream: itag="137" mime_type="video/mp4" res="1080p" fps="30fps" vcodec="avc1.640028" progressive="False" type="video">,
    ...
    <Stream: itag="250" mime_type="audio/webm" abr="70kbps" acodec="opus" progressive="False" type="audio">,
    <Stream: itag="251" mime_type="audio/webm" abr="160kbps" acodec="opus" progressive="False" type="audio">]


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

    >>> yt.streams.filter(progressive=True)
    [<Stream: itag="18" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.42001E" acodec="mp4a.40.2" progressive="True" type="video">,
    <Stream: itag="22" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.64001F" acodec="mp4a.40.2" progressive="True" type="video">]

Conversely, if you only want to see the DASH streams (also referred to as
"adaptive") you can do::

    >>> yt.streams.filter(adaptive=True)
    [<Stream: itag="137" mime_type="video/mp4" res="1080p" fps="30fps" vcodec="avc1.640028" progressive="False" type="video">,
    <Stream: itag="248" mime_type="video/webm" res="1080p" fps="30fps" vcodec="vp9" progressive="False" type="video">,
    <Stream: itag="399" mime_type="video/mp4" res="None" fps="30fps" vcodec="av01.0.08M.08" progressive="False" type="video">,
    ...
    <Stream: itag="250" mime_type="audio/webm" abr="70kbps" acodec="opus" progressive="False" type="audio">,
    <Stream: itag="251" mime_type="audio/webm" abr="160kbps" acodec="opus" progressive="False" type="audio">]

Pytube allows you to filter on every property available (see
:py:meth:`pytube.StreamQuery.filter` for a complete list of filter options),
let's take a look at some common examples:

Query audio only Streams
------------------------

To query the streams that contain only the audio track::

    >>> yt.streams.filter(only_audio=True)
    [<Stream: itag="140" mime_type="audio/mp4" abr="128kbps" acodec="mp4a.40.2" progressive="False" type="audio">,
    <Stream: itag="249" mime_type="audio/webm" abr="50kbps" acodec="opus" progressive="False" type="audio">,
    <Stream: itag="250" mime_type="audio/webm" abr="70kbps" acodec="opus" progressive="False" type="audio">,
    <Stream: itag="251" mime_type="audio/webm" abr="160kbps" acodec="opus" progressive="False" type="audio">]

Query MPEG-4 Streams
--------------------

To query only streams in the MPEG-4 format::

    >>> yt.streams.filter(file_extension='mp4')
    [<Stream: itag="18" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.42001E" acodec="mp4a.40.2" progressive="True" type="video">,
    <Stream: itag="22" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.64001F" acodec="mp4a.40.2" progressive="True" type="video">,
    <Stream: itag="137" mime_type="video/mp4" res="1080p" fps="30fps" vcodec="avc1.640028" progressive="False" type="video">,
    ...
    <Stream: itag="394" mime_type="video/mp4" res="None" fps="30fps" vcodec="av01.0.00M.08" progressive="False" type="video">,
    <Stream: itag="140" mime_type="audio/mp4" abr="128kbps" acodec="mp4a.40.2" progressive="False" type="audio">]

Get Streams by itag
-------------------

To get a stream by a specific itag::

    >>> yt.streams.get_by_itag('22')
    <Stream: itag="22" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.64001F" acodec="mp4a.40.2" progressive="True" type="video">

Subtitle/Caption Tracks
=======================

Pytube exposes the caption tracks in much the same way as querying the media
streams. Let's begin by switching to a video that contains them::

    >>> yt = YouTube('http://youtube.com/watch?v=2lAe1cqCOXo')
    >>> yt.captions
    {'ar': <Caption lang="Arabic" code="ar">, 'zh-HK': <Caption lang="Chinese (Hong Kong)" code="zh-HK">, 'zh-TW': <Caption lang="Chinese (Taiwan)" code="zh-TW">, 'hr': <Caption lang="Croatian" code="hr">, 'cs': <Caption lang="Czech" code="cs">, 'da': <Caption lang="Danish" code="da">, 'nl': <Caption lang="Dutch" code="nl">, 'en': <Caption lang="English" code="en">, 'en-GB': <Caption lang="English (United Kingdom)" code="en-GB">, 'et': <Caption lang="Estonian" code="et">, 'fil': <Caption lang="Filipino" code="fil">, 'fi': <Caption lang="Finnish" code="fi">, 'fr-CA': <Caption lang="French (Canada)" code="fr-CA">, 'fr-FR': <Caption lang="French (France)" code="fr-FR">, 'de': <Caption lang="German" code="de">, 'el': <Caption lang="Greek" code="el">, 'iw': <Caption lang="Hebrew" code="iw">, 'hu': <Caption lang="Hungarian" code="hu">, 'id': <Caption lang="Indonesian" code="id">, 'it': <Caption lang="Italian" code="it">, 'ja': <Caption lang="Japanese" code="ja">, 'ko': <Caption lang="Korean" code="ko">, 'lv': <Caption lang="Latvian" code="lv">, 'lt': <Caption lang="Lithuanian" code="lt">, 'ms': <Caption lang="Malay" code="ms">, 'no': <Caption lang="Norwegian" code="no">, 'pl': <Caption lang="Polish" code="pl">, 'pt-BR': <Caption lang="Portuguese (Brazil)" code="pt-BR">, 'pt-PT': <Caption lang="Portuguese (Portugal)" code="pt-PT">, 'ro': <Caption lang="Romanian" code="ro">, 'ru': <Caption lang="Russian" code="ru">, 'sk': <Caption lang="Slovak" code="sk">, 'es-419': <Caption lang="Spanish (Latin America)" code="es-419">, 'es-ES': <Caption lang="Spanish (Spain)" code="es-ES">, 'sv': <Caption lang="Swedish" code="sv">, 'th': <Caption lang="Thai" code="th">, 'tr': <Caption lang="Turkish" code="tr">, 'uk': <Caption lang="Ukrainian" code="uk">, 'ur': <Caption lang="Urdu" code="ur">, 'vi': <Caption lang="Vietnamese" code="vi">}

Now let's checkout the english captions::

    >>> caption = yt.captions.get_by_language_code('en')

Great, now let's see how YouTube formats them::

    >>> caption.xml_captions
    '<?xml version="1.0" encoding="utf-8" ?><transcript><text start="10.2" dur="0.94">K-pop!</text>...'

Oh, this isn't very easy to work with, let's convert them to the srt format::

    >>> print(caption.generate_srt_captions())
    1
    00:00:10,200 --> 00:00:11,140
    K-pop!

    2
    00:00:13,400 --> 00:00:16,200
    That is so awkward to watch.
    ...
