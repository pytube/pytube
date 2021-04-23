.. _streams:

Working with Streams and StreamQuery
====================================

The next section will explore the various options available for working with
media streams, but before we can dive in, we need to review a new-ish streaming
technique adopted by YouTube. It assumes that you have already created a
YouTube object in your code called "yt".

DASH vs Progressive Streams
---------------------------

Begin by running the following to list all streams::

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

Filtering Streams
=================

Pytube has built-in functionality to filter the streams available in a YouTube
object with the .filter() method. You can pass it a number of different keyword
arguments, so let's review some of the different options you're most likely to
use. For a complete list of available properties to filter on, you can view the
API documentation here: :meth:`pytube.StreamQuery.filter`.

Filtering by streaming method
-----------------------------

As mentioned before, progressive streams have the video and audio in a single
file, but typically do not provide the highest quality media; meanwhile,
adaptive streams split the video and audio tracks but can provide much higher
quality. Pytube makes it easy to filter based on the type of stream that you're
interested.

For example, you can filter to only progressive streams with the following::

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

Filtering for audio-only streams
--------------------------------

To query the streams that contain only the audio track::

    >>> yt.streams.filter(only_audio=True)
    [<Stream: itag="140" mime_type="audio/mp4" abr="128kbps" acodec="mp4a.40.2" progressive="False" type="audio">,
    <Stream: itag="249" mime_type="audio/webm" abr="50kbps" acodec="opus" progressive="False" type="audio">,
    <Stream: itag="250" mime_type="audio/webm" abr="70kbps" acodec="opus" progressive="False" type="audio">,
    <Stream: itag="251" mime_type="audio/webm" abr="160kbps" acodec="opus" progressive="False" type="audio">]

Filtering for MP4 streams
-------------------------

To query only streams in the MP4 format::

    >>> yt.streams.filter(file_extension='mp4')
    [<Stream: itag="18" mime_type="video/mp4" res="360p" fps="30fps" vcodec="avc1.42001E" acodec="mp4a.40.2" progressive="True" type="video">,
    <Stream: itag="22" mime_type="video/mp4" res="720p" fps="30fps" vcodec="avc1.64001F" acodec="mp4a.40.2" progressive="True" type="video">,
    <Stream: itag="137" mime_type="video/mp4" res="1080p" fps="30fps" vcodec="avc1.640028" progressive="False" type="video">,
    ...
    <Stream: itag="394" mime_type="video/mp4" res="None" fps="30fps" vcodec="av01.0.00M.08" progressive="False" type="video">,
    <Stream: itag="140" mime_type="audio/mp4" abr="128kbps" acodec="mp4a.40.2" progressive="False" type="audio">]

Downloading Streams
===================

After you've selected the :class:`Stream <pytube.Stream>` you're interested,
you're ready to interact with it. At this point, you can query information
about the stream, such as its filesize, whether the stream is adaptive, and
more. You can also use the download method to save the file::

    >>> stream = yt.streams.get_by_itag(22)
    >>> stream.download()

The download method has a number of different useful arguments, which are
documented in the API reference here: :meth:`pytube.Stream.download`.
