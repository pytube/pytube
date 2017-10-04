# -*- coding: utf-8 -*-
"""
pytube.streams
~~~~~~~~~~~~~~

A container object for the media stream (video only / audio only / video+audio
combined). This was referred to as ``Video`` in the legacy pytube version, but
has been renamed to accommodate DASH (which serves the audio and video
separately).
"""
import os
import re

from pytube import request
from pytube.helpers import memoize
from pytube.helpers import safe_filename
from pytube.itags import get_format_profile


class Stream:
    """The media stream container"""

    def __init__(self, stream, player_config, monostate):
        # A dictionary shared between all instances of :class:`Stream <Stream>`
        # (Borg pattern).
        self._monostate = monostate

        self.abr = None   # average bitrate (audio streams only)
        self.fps = None   # frames per second (video streams only)
        self.itag = None  # stream format id (youtube nomenclature)
        self.res = None   # resolution (e.g.: 480p, 720p, 1080p)
        self.url = None   # signed download url

        self.mime_type = None  # content identifer (e.g.: video/mp4)
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
        # TODO(nficano): this should be moved to the momostate.
        self.player_config = player_config

        # 'video/webm; codecs="vp8, vorbis"' -> 'video/webm', ['vp8', 'vorbis']
        self.mime_type, self.codecs = self.parse_type()

        # 'video/webm' -> 'video', 'webm'
        self.type, self.subtype = self.mime_type.split('/')

        # ['vp8', 'vorbis'] -> video_codec: vp8, audio_codec: vorbis. DASH
        # streams return NoneType for audio/video depending.
        self.video_codec, self.audio_codec = self.parse_codecs()

    def set_attributes_from_dict(self, dct):
        for key, val in dct.items():
            setattr(self, key, val)

    @property
    def is_dash(self):
        """Whether the stream is DASH."""
        # if codecs has two elements (e.g.: ['vp8', 'vorbis']): 2 % 2 = 0
        # if codecs has one element (e.g.: ['vp8']) 1 % 2 = 1
        return len(self.codecs) % 2

    @property
    def is_audio(self):
        """Whether the stream only contains audio (DASH only)."""
        return self.type == 'audio'

    @property
    def is_video(self):
        """Whether the stream only contains video (DASH only)."""
        return self.type == 'video'

    def parse_codecs(self):
        video = None
        audio = None
        if not self.is_dash:
            video, audio = self.codecs
        elif self.is_video:
            video = self.codecs[0]
        elif self.is_audio:
            audio = self.codecs[0]
        return video, audio

    def parse_type(self):
        regex = re.compile(r'(\w+\/\w+)\;\scodecs=\"([a-zA-Z-0-9.,\s]*)\"')
        mime_type, codecs = regex.search(self.type).groups()
        return mime_type, [c.strip() for c in codecs.split(',')]

    @property
    @memoize
    def filesize(self):
        """The file size of the media stream in bytes."""
        headers = request.get(self.url, headers=True)
        return int(headers['Content-Length'])

    @property
    def default_filename(self):
        """A generated filename based on the video title, but sanitized for the
        filesystem.
        """
        title = self.player_config['args']['title']
        filename = safe_filename(title)
        return '{filename}.{s.subtype}'.format(filename=filename, s=self)

    def download(self, output_path=None):
        """Write the media stream to disk."""

        # TODO(nficano): allow a filename to specified.
        # use the provided output path or use working directory if one is not
        # provided.
        output_path = output_path or os.getcwd()

        # file path
        fp = os.path.join(output_path, self.default_filename)
        bytes_remaining = self.filesize

        with open(fp, 'wb') as fh:
            for chunk in request.get(self.url, streaming=True):
                # reduce the (bytes) remainder by the length of the chunk.
                bytes_remaining -= len(chunk)
                # send to the on_progress callback.
                self.on_progress(chunk, fh, bytes_remaining)

    def on_progress(self, chunk, file_handler, bytes_remaining):
        """The on progress callback. This function writes the binary data to
        the file, then checks if an additional callback is defined in the
        monostate. This is exposed to allow things like displaying a progress
        bar.
        """
        file_handler.write(chunk)
        on_progress = self._monostate['on_progress']
        if on_progress:
            on_progress(self, chunk, bytes_remaining)

    def on_complete(self, fh):
        on_complete = self._monostate['on_complete']
        if on_complete:
            on_complete(self, fh)

    def __repr__(self):
        parts = ['itag="{s.itag}"', 'mime_type="{s.mime_type}"']
        if self.is_video:
            parts.extend(['res="{s.resolution}"', 'fps="{s.fps}fps"'])
            if not self.is_dash:
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
