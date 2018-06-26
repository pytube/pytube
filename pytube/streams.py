# -*- coding: utf-8 -*-
"""
This module contains a container for stream manifest data.

A container object for the media stream (video only / audio only / video+audio
combined). This was referred to as ``Video`` in the legacy pytube version, but
has been renamed to accommodate DASH (which serves the audio and video
separately).
"""
from __future__ import absolute_import

import io
import logging
import os
import pprint

from pytube import extract
from pytube import request
from pytube.helpers import safe_filename
from pytube.itags import get_format_profile


logger = logging.getLogger(__name__)


class Stream(object):
    """Container for stream manifest data."""

    def __init__(self, stream, player_config_args, monostate):
        """Construct a :class:`Stream <Stream>`.

        :param dict stream:
            The unscrambled data extracted from YouTube.
        :param dict player_config_args:
            The data object containing video media data like title and
            keywords.
        :param dict monostate:
            Dictionary of data shared across all instances of
            :class:`Stream <Stream>`.
        """
        # A dictionary shared between all instances of :class:`Stream <Stream>`
        # (Borg pattern).
        self._monostate = monostate

        self.abr = None   # average bitrate (audio streams only)
        self.fps = None   # frames per second (video streams only)
        self.itag = None  # stream format id (youtube nomenclature)
        self.res = None   # resolution (e.g.: 480p, 720p, 1080p)
        self.url = None   # signed download url

        self._filesize = None  # filesize in bytes
        self.mime_type = None  # content identifier (e.g.: video/mp4)
        self.type = None       # the part of the mime before the slash
        self.subtype = None    # the part of the mime after the slash

        self.codecs = []         # audio/video encoders (e.g.: vp8, mp4a)
        self.audio_codec = None  # audio codec of the stream (e.g.: vorbis)
        self.video_codec = None  # video codec of the stream (e.g.: vp8)

        # Iterates over the key/values of stream and sets them as class
        # attributes. This is an anti-pattern and should be removed.
        self.set_attributes_from_dict(stream)

        # Additional information about the stream format, such as resolution,
        # frame rate, and whether the stream is live (HLS) or 3D.
        self.fmt_profile = get_format_profile(self.itag)

        # Same as above, except for the format profile attributes.
        self.set_attributes_from_dict(self.fmt_profile)

        # The player configuration which contains information like the video
        # title.
        # TODO(nficano): this should be moved to the monostate.
        self.player_config_args = player_config_args

        # 'video/webm; codecs="vp8, vorbis"' -> 'video/webm', ['vp8', 'vorbis']
        self.mime_type, self.codecs = extract.mime_type_codec(self.type)

        # 'video/webm' -> 'video', 'webm'
        self.type, self.subtype = self.mime_type.split('/')

        # ['vp8', 'vorbis'] -> video_codec: vp8, audio_codec: vorbis. DASH
        # streams return NoneType for audio/video depending.
        self.video_codec, self.audio_codec = self.parse_codecs()

    def set_attributes_from_dict(self, dct):
        """Set class attributes from dictionary items.

        :rtype: None
        """
        for key, val in dct.items():
            setattr(self, key, val)

    @property
    def is_adaptive(self):
        """Whether the stream is DASH.

        :rtype: bool
        """
        # if codecs has two elements (e.g.: ['vp8', 'vorbis']): 2 % 2 = 0
        # if codecs has one element (e.g.: ['vp8']) 1 % 2 = 1
        return len(self.codecs) % 2

    @property
    def is_progressive(self):
        """Whether the stream is progressive.

        :rtype: bool
        """
        return not self.is_adaptive

    @property
    def includes_audio_track(self):
        """Whether the stream only contains audio.

        :rtype: bool
        """
        if self.is_progressive:
            return True
        return self.type == 'audio'

    @property
    def includes_video_track(self):
        """Whether the stream only contains video.

        :rtype: bool
        """
        if self.is_progressive:
            return True
        return self.type == 'video'

    def parse_codecs(self):
        """Get the video/audio codecs from list of codecs.

        Parse a variable length sized list of codecs and returns a
        constant two element tuple, with the video codec as the first element
        and audio as the second. Returns None if one is not available
        (adaptive only).

        :rtype: tuple
        :returns:
            A two element tuple with audio and video codecs.

        """
        video = None
        audio = None
        if not self.is_adaptive:
            video, audio = self.codecs
        elif self.includes_video_track:
            video = self.codecs[0]
        elif self.includes_audio_track:
            audio = self.codecs[0]
        return video, audio

    @property
    def filesize(self):
        """File size of the media stream in bytes.

        :rtype: int
        :returns:
            Filesize (in bytes) of the stream.
        """
        if self._filesize is None:
            headers = request.get(self.url, headers=True)
            self._filesize = int(headers['content-length'])
        return self._filesize

    @property
    def default_filename(self):
        """Generate filename based on the video title.

        :rtype: str
        :returns:
            An os file system compatible filename.
        """
        title = self.player_config_args['title']
        filename = safe_filename(title)
        return '{filename}.{s.subtype}'.format(filename=filename, s=self)

    def download(self, output_path=None, filename=None, filename_prefix=None):
        """Write the media stream to disk.

        :param output_path:
            (optional) Output path for writing media file. If one is not
            specified, defaults to the current working directory.
        :type output_path: str or None
        :param filename:
            (optional) Output filename (stem only) for writing media file.
            If one is not specified, the default filename is used.
        :type filename: str or None
        :param filename_prefix:
            (optional) A string that will be prepended to the filename.
            For example a number in a playlist or the name of a series.
            If one is not specified, nothing will be prepended
            This is seperate from filename so you can use the default
            filename but still add a prefix.
        :type filename_prefix: str or None

        :rtype: str

        """
        output_path = output_path or os.getcwd()
        if filename:
            safe = safe_filename(filename)
            filename = '{filename}.{s.subtype}'.format(filename=safe, s=self)
        filename = filename or self.default_filename

        if filename_prefix:
            filename = '{prefix}{filename}'\
                .format(
                    prefix=safe_filename(filename_prefix),
                    filename=filename,
                )

        # file path
        fp = os.path.join(output_path, filename)
        bytes_remaining = self.filesize
        logger.debug(
            'downloading (%s total bytes) file to %s',
            self.filesize, fp,
        )

        with open(fp, 'wb') as fh:
            for chunk in request.get(self.url, streaming=True):
                # reduce the (bytes) remainder by the length of the chunk.
                bytes_remaining -= len(chunk)
                # send to the on_progress callback.
                self.on_progress(chunk, fh, bytes_remaining)
            self.on_complete(fh)
        return fp

    def stream_to_buffer(self):
        """Write the media stream to buffer

        :rtype: io.BytesIO buffer
        """
        buffer = io.BytesIO()
        bytes_remaining = self.filesize
        logger.debug(
            'downloading (%s total bytes) file to BytesIO buffer',
            self.filesize,
        )

        for chunk in request.get(self.url, streaming=True):
            # reduce the (bytes) remainder by the length of the chunk.
            bytes_remaining -= len(chunk)
            # send to the on_progress callback.
            self.on_progress(chunk, buffer, bytes_remaining)
        self.on_complete(buffer)
        return buffer

    def on_progress(self, chunk, file_handler, bytes_remaining):
        """On progress callback function.

        This function writes the binary data to the file, then checks if an
        additional callback is defined in the monostate. This is exposed to
        allow things like displaying a progress bar.

        :param str chunk:
            Segment of media file binary data, not yet written to disk.
        :param file_handler:
            The file handle where the media is being written to.
        :type file_handler:
            :py:class:`io.BufferedWriter`
        :param int bytes_remaining:
            The delta between the total file size in bytes and amount already
            downloaded.

        :rtype: None

        """
        file_handler.write(chunk)
        logger.debug(
            'download progress\n%s',
            pprint.pformat(
                {
                    'chunk_size': len(chunk),
                    'bytes_remaining': bytes_remaining,
                }, indent=2,
            ),
        )
        on_progress = self._monostate['on_progress']
        if on_progress:
            logger.debug('calling on_progress callback %s', on_progress)
            on_progress(self, chunk, file_handler, bytes_remaining)

    def on_complete(self, file_handle):
        """On download complete handler function.

        :param file_handle:
            The file handle where the media is being written to.
        :type file_handle:
            :py:class:`io.BufferedWriter`

        :rtype: None

        """
        logger.debug('download finished')
        on_complete = self._monostate['on_complete']
        if on_complete:
            logger.debug('calling on_complete callback %s', on_complete)
            on_complete(self, file_handle)

    def __repr__(self):
        """Printable object representation.

        :rtype: str
        :returns:
            A string representation of a :class:`Stream <Stream>` object.
        """
        # TODO(nficano): this can probably be written better.
        parts = ['itag="{s.itag}"', 'mime_type="{s.mime_type}"']
        if self.includes_video_track:
            parts.extend(['res="{s.resolution}"', 'fps="{s.fps}fps"'])
            if not self.is_adaptive:
                parts.extend([
                    'vcodec="{s.video_codec}"',
                    'acodec="{s.audio_codec}"',
                ])
            else:
                parts.extend(['vcodec="{s.video_codec}"'])
        else:
            parts.extend(['abr="{s.abr}"', 'acodec="{s.audio_codec}"'])
        parts = ' '.join(parts).format(s=self)
        return '<Stream: {parts}>'.format(parts=parts)
