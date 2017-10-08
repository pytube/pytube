# -*- coding: utf-8 -*-
"""
pytube.__main__
~~~~~~~~~~~~~~~

This module implements the core developer interface for pytube.

"""
from __future__ import absolute_import

import json
import logging

from pytube import extract
from pytube import mixins
from pytube import request
from pytube import Stream
from pytube import StreamQuery
from pytube.helpers import apply_mixin
from pytube.helpers import memoize


logger = logging.getLogger(__name__)


class YouTube(object):

    def __init__(
        self, url=None, defer_init=False, on_progress_callback=None,
        on_complete_callback=None,
    ):
        """Constructs a :class:`YouTube <YouTube>`.

        :param str url:
            A valid YouTube watch URL.
        :param bool defer_init:
            Defers executing any network requests.
        :param func on_progress_callback:
            (Optional) User defined callback function for stream download
            progress events.
        :param func on_complete_callback:
            (Optional) User defined callback function for stream download
            complete events.

        """
        self.js = None      # js fetched by js_url
        self.js_url = None  # the url to the js, parsed from watch html

        # note: vid_info can possibly be removed, the fmt stream data contained
        # in here doesn't compute a usable signature and the rest of the data
        # may be redundant.

        self.vid_info = None      # content fetched by vid_info_url
        self.vid_info_url = None  # the url to vid info, parsed from watch html

        self.watch_html = None     # the html of /watch?v=<video_id>
        self.player_config = None  # inline js in the html containing streams

        self.fmt_streams = []  # list of :class:`Stream <Stream>` instances

        # video_id part of /watch?v=<video_id>
        self.video_id = extract.video_id(url)

        # https://www.youtube.com/watch?v=<video_id>
        self.watch_url = extract.watch_url(self.video_id)

        # A dictionary shared between all instances of :class:`Stream <Stream>`
        # (Borg pattern).
        self.stream_monostate = {
            # user defined callback functions
            'on_progress': on_progress_callback,
            'on_complete': on_complete_callback,
        }

        if url and not defer_init:
            self.init()

    def init(self):
        """Makes all necessary network requests, data transforms, and popluates
        the instances of :class:`Stream <Stream>`.

        """
        logger.info('init started')
        self.prefetch()

        progressive_fmts = 'url_encoded_fmt_stream_map'
        adaptive_fmts = 'adaptive_fmts'
        config_args = self.player_config['args']

        # unscrambles the data necessary to access the streams and metadata.
        mixins.apply_descrambler(config_args, progressive_fmts)
        mixins.apply_descrambler(config_args, adaptive_fmts)

        # apply the signature to the download url.
        mixins.apply_signature(config_args, progressive_fmts, self.js)
        mixins.apply_signature(config_args, adaptive_fmts, self.js)

        # load the player_response object (contains subtitle information)
        apply_mixin(config_args, 'player_response', json.loads)

        # build instances of :class:`Stream <Stream>`
        self.initialize_stream_objects(progressive_fmts)
        self.initialize_stream_objects(adaptive_fmts)
        logger.info('init finished successfully')

    def prefetch(self):
        """Eagerly executes all necessary network requests so all other
        operations don't does need to make calls outside of the interpreter
        which blocks for long periods of time.

        """
        self.watch_html = request.get(url=self.watch_url)
        self.vid_info_url = extract.video_info_url(
            video_id=self.video_id,
            watch_url=self.watch_url,
            watch_html=self.watch_html,
        )
        self.js_url = extract.js_url(self.watch_html)
        self.js, self.vid_info = request.get(urls=[
            self.js_url,
            self.vid_info_url,
        ])
        self.player_config = extract.get_ytplayer_config(self.watch_html)

    def initialize_stream_objects(self, fmt):
        """Takes the unscrambled stream data and uses it to initialize
        instances of :class:`Stream <Stream>` for each media stream.

        :param str fmt:
            Key in stream manifest ("player_config") containing progressive
            download or adaptive streams (e.g.: "url_encoded_fmt_stream_map" or
            "adaptive_fmts").

        """
        stream_manifest = self.player_config['args'][fmt]
        for stream in stream_manifest:
            video = Stream(
                stream=stream,
                player_config=self.player_config,
                monostate=self.stream_monostate,
            )
            self.fmt_streams.append(video)

    @property
    @memoize
    def progressive_streams(self):
        """Interface to query progressive download streams."""
        return StreamQuery([s for s in self.fmt_streams if not s.is_adaptive])

    @property
    @memoize
    def adaptive_streams(self):
        """Interface to query adaptive (DASH) streams."""
        return StreamQuery([s for s in self.fmt_streams if s.is_adaptive])

    @property
    @memoize
    def streams(self):
        """Interface to query both adaptive (DASH) and progressive streams."""
        return StreamQuery([s for s in self.fmt_streams])

    def register_on_progress_callback(self, func):
        """Registers an on download progess callback function after object
        initialization.

        :param callable func:
            A callback function that takes ``stream``, ``chunk``,
            ``file_handle``, ``bytes_remaining`` as parameters.
        """
        self._monostate['on_progress'] = func

    def register_on_complete_callback(self, func):
        """Registers an on download complete callback function after object
        initialization.

        :param callable func:
            A callback function that takes ``stream`` and  ``file_handle``.
        """
        self._monostate['on_complete'] = func
