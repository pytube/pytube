# -*- coding: utf-8 -*-
"""
pytube.query
~~~~~~~~~~~~

"""


class StreamQuery:
    def __init__(self, fmt_streams):
        self.fmt_streams = fmt_streams
        self.itag_index = {int(s.itag): s for s in fmt_streams}

    def filter(
        self, fps=None, res=None, resolution=None, mime_type=None,
        type=None, subtype=None, abr=None, bitrate=None,
        video_codec=None, audio_codec=None,
        custom_filter_functions=None,
    ):
        filters = []
        if res or resolution:
            filters.append(lambda s: s.resolution == (res or resolution))

        if fps:
            filters.append(lambda s: s.fps == fps)

        if mime_type:
            filters.append(lambda s: s.mime_type == mime_type)

        if type:
            filters.append(lambda s: s.type == type)

        if subtype:
            filters.append(lambda s: s.subtype == subtype)

        if abr or bitrate:
            filters.append(lambda s: s.abr == (abr or bitrate))

        if video_codec:
            filters.append(lambda s: s.video_codec == video_codec)

        if audio_codec:
            filters.append(lambda s: s.audio_codec == audio_codec)

        if custom_filter_functions:
            for fn in custom_filter_functions:
                filters.append(fn)

        fmt_streams = self.fmt_streams
        for fn in filters:
            fmt_streams = list(filter(fn, fmt_streams))
        return StreamQuery(fmt_streams)

    def get(self, itag):
        return self.itag_index[itag]

    def first(self):
        return self.fmt_streams[0]

    def last(self):
        return self.fmt_streams[-1]

    def count(self):
        return len(self.fmt_streams)

    def all(self):
        return self.fmt_streams
