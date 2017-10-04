# -*- coding: utf-8 -*-
"""
pytube.streams
~~~~~~~~~~~~~~

"""
import os
import re

from pytube import download
from pytube.helpers import memoize
from pytube.helpers import safe_filename
from pytube.itags import get_format_profile


class Stream:
    def __init__(self, stream, player_config, shared_stream_state):
        self.shared_stream_state = shared_stream_state
        self.abr = None
        self.audio_codec = None
        self.codecs = None
        self.fps = None
        self.itag = None
        self.mime_type = None
        self.res = None
        self.subtype = None
        self.type = None
        self.url = None
        self.video_codec = None

        self.set_attributes_from_dict(stream)
        self.fmt_profile = get_format_profile(self.itag)
        self.set_attributes_from_dict(self.fmt_profile)

        self.player_config = player_config
        self.mime_type, self.codecs = self.parse_type()
        self.type, self.subtype = self.mime_type.split('/')
        self.video_codec, self.audio_codec = self.parse_codecs()

    def set_attributes_from_dict(self, dct):
        for key, val in dct.items():
            setattr(self, key, val)

    @property
    def is_dash(self):
        return len(self.codecs) % 2

    @property
    def is_audio(self):
        return self.type == 'audio'

    @property
    def is_video(self):
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
        headers = download.headers(self.url)
        return int(headers['Content-Length'])

    @property
    def default_filename(self):
        title = self.player_config['args']['title']
        filename = safe_filename(title)
        return '{filename}.{s.subtype}'.format(filename=filename, s=self)

    def on_progress(self, chunk, file_handler, bytes_remaining):
        file_handler.write(chunk)
        on_progress = self.shared_stream_state['on_progress']
        if on_progress:
            on_progress(self, chunk, bytes_remaining)

    def on_complete(self, fh):
        on_complete = self.shared_stream_state['on_complete']
        if on_complete:
            on_complete(self, fh)

    def download(self, output_path=None):
        output_path = output_path or os.getcwd()
        fp = os.path.join(output_path, self.default_filename)
        bytes_remaining = self.filesize
        with open(fp, 'wb') as fh:
            for chunk in download.stream(self.url):
                bytes_remaining -= len(chunk)
                self.on_progress(chunk, fh, bytes_remaining)

    def __repr__(self):
        parts = [
            'itag="{self.itag}"',
            'mime_type="{self.mime_type}"',
        ]
        if self.is_video:
            parts.extend([
                'res="{self.resolution}"',
                'fps="{self.fps}fps"',
            ])
            if not self.is_dash:
                parts.extend([
                    'vcodec="{self.video_codec}"',
                    'acodec="{self.audio_codec}"',
                ])
            else:
                parts.extend([
                    'vcodec="{self.video_codec}"',
                ])
        else:
            parts.extend([
                'abr="{self.abr}"',
                'acodec="{self.audio_codec}"',
            ])
        parts = ' '.join(parts)
        return '<Stream: {parts}>'.format(self=self)
