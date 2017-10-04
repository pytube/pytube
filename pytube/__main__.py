# -*- coding: utf-8 -*-
"""
pytube.__main__
~~~~~~~~~~~~~~~

This module implements the core interface for pytube.

"""
import json

from pytube import download
from pytube import extract
from pytube import mixins
from pytube.query import StreamQuery
from pytube.streams import Stream


class YouTube:
    def __init__(
        self, url=None, defer_init=False, on_progress_callback=None,
        on_complete_callback=None,
    ):
        self.js = None
        self.js_url = None
        self.vid_info = None
        self.vid_info_url = None
        self.watch_html = None
        self.player_config = None
        self.fmt_streams = []
        self.video_id = extract.video_id(url)
        self.watch_url = extract.watch_url(self.video_id)
        self.shared_stream_state = {
            'on_progress': on_progress_callback,
            'on_complete': on_complete_callback,
        }

        if url and not defer_init:
            self.init()

    def init(self):
        self.prefetch()
        self.vid_info = extract.decode_video_info(self.vid_info)

        trad_fmts = 'url_encoded_fmt_stream_map'
        dash_fmts = 'adaptive_fmts'
        mixins.apply_fmt_decoder(self.vid_info, trad_fmts)
        mixins.apply_fmt_decoder(self.vid_info, dash_fmts)
        mixins.apply_fmt_decoder(self.player_config['args'], trad_fmts)
        mixins.apply_fmt_decoder(self.player_config['args'], dash_fmts)
        mixins.apply_cipher(self.player_config['args'], trad_fmts, self.js)
        mixins.apply_cipher(self.player_config['args'], dash_fmts, self.js)
        mixins.apply(self.player_config['args'], 'player_response', json.loads)
        self.build_stream_objects(trad_fmts)
        self.build_stream_objects(dash_fmts)

    def prefetch(self):
        self.watch_html = download.get(url=self.watch_url)
        self.vid_info_url = extract.video_info_url(
            video_id=self.video_id,
            watch_url=self.watch_url,
            watch_html=self.watch_html,
        )
        self.js_url = extract.js_url(self.watch_html)
        self.js = download.get(url=self.js_url)
        self.vid_info = download.get(url=self.vid_info_url)
        self.player_config = extract.get_ytplayer_config(self.watch_html)

    def build_stream_objects(self, fmt):
        streams = self.player_config['args'][fmt]
        for stream in streams:
            video = Stream(
                stream=stream,
                player_config=self.player_config,
                shared_stream_state=self.shared_stream_state,
            )
            self.fmt_streams.append(video)

    @property
    def streams(self):
        """Interface to query non-dash streams."""
        return StreamQuery([s for s in self.fmt_streams if not s.is_dash])

    @property
    def dash_streams(self):
        """Interface to query dash streams."""
        return StreamQuery([s for s in self.fmt_streams if s.is_dash])

    def register_on_progress_callback(self, fn):
        self.shared_stream_state['on_progress'] = fn

    def register_on_complete_callback(self, fn):
        self.shared_stream_state['on_complete'] = fn
