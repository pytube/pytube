# -*- coding: utf-8 -*-
"""
pytube.query
~~~~~~~~~~~~

The :class:`StreamQuery <StreamQuery>` class provides an interface for querying
the available media streams.
"""


class StreamQuery:

    def __init__(self, fmt_streams):
        """Constructs a :class:`StreamQuery <StreamQuery>`.
        """

        # list of :class:`Stream <Stream>` instances
        self.fmt_streams = fmt_streams
        self.itag_index = {int(s.itag): s for s in fmt_streams}

    def filter(
            self, fps=None, res=None, resolution=None, mime_type=None,
            type=None, subtype=None, file_extension=None, abr=None,
            bitrate=None, video_codec=None, audio_codec=None,
            custom_filter_functions=None,
    ):
        """Apply the given filtering criterion to a copy of this
        :class:`StreamQuery <StreamQuery>`.

        :param int fps:
            (optional) The frames per second (30 or 60)
        :param str resolution:
            (optional) Alias to ``res``.
        :param str res:
            (optional) The video resolution (e.g.: 480p, 720p, 1080p)
        :param str mime_type:
            (optional) Two-part identifier for file formats and format contents
            composed of a "type", a "subtype" (e.g.: video/mp4).
        :param str type:
            (optional) Type part of the ``mime_type`` (e.g.: "audio", "video").
        :param str subtype:
            (optional) Sub-type part of the ``mime_type`` (e.g.: "mp4", "mov").
        :param str file_extension:
            (optional) Alias to ``sub_type``.
        :param str abr:
            (optional) Average bitrate (ABR) refers to the average amount of
            data transferred per unit of time (e.g.: 64kbps, 192kbps)
        :param str bitrate:
            (optional) Alias to ``abr``.
        :param str video_codec:
            (optional) Digital video compression format (e.g.: vp9, mp4v.20.3).
        :param str audio_codec:
            (optional) Digital audio compression format (e.g.: vorbis, mp4).
        :param list custom_filter_functions:
            (optional) Interface for defining complex filters without
            subclassing.
        """
        filters = []
        if res or resolution:
            filters.append(lambda s: s.resolution == (res or resolution))

        if fps:
            filters.append(lambda s: s.fps == fps)

        if mime_type:
            filters.append(lambda s: s.mime_type == mime_type)

        if type:
            filters.append(lambda s: s.type == type)

        if subtype or file_extension:
            filters.append(lambda s: s.subtype == (subtype or file_extension))

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

    def get_by_itag(self, itag):
        """Return an instance based on the given itag, or None if not found.

        :param str itag:
            YouTube format identifier code.
        """
        try:
            return self.itag_index[itag]
        except KeyError:
            pass

    def first(self):
        """Return the first result of this query or None if the result doesn't
        contain any streams.

        """
        try:
            return self.fmt_streams[0]
        except IndexError:
            pass

    def last(self):
        """Return the last result of this query or None if the result doesn't
        contain any streams.

        """
        try:
            return self.fmt_streams[-1]
        except IndexError:
            pass

    def count(self):
        """Return the count the query would return."""
        return len(self.fmt_streams)

    def all(self):
        """Return the results represented by this query as a list."""
        return self.fmt_streams
