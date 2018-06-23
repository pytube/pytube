# -*- coding: utf-8 -*-
"""This module provides a query interface for media streams and captions."""


class StreamQuery:
    """Interface for querying the available media streams."""

    def __init__(self, fmt_streams):
        """Construct a :class:`StreamQuery <StreamQuery>`.

        param list fmt_streams:
            list of :class:`Stream <Stream>` instances.
        """
        self.fmt_streams = fmt_streams
        self.itag_index = {int(s.itag): s for s in fmt_streams}

    def filter(
            self, fps=None, res=None, resolution=None, mime_type=None,
            type=None, subtype=None, file_extension=None, abr=None,
            bitrate=None, video_codec=None, audio_codec=None,
            only_audio=None, only_video=None,
            progressive=None, adaptive=None,
            custom_filter_functions=None,
    ):
        """Apply the given filtering criterion.

        :param fps:
            (optional) The frames per second.
        :type fps:
            int or None

        :param resolution:
            (optional) Alias to ``res``.
        :type res:
            str or None

        :param res:
            (optional) The video resolution.
        :type resolution:
            str or None

        :param mime_type:
            (optional) Two-part identifier for file formats and format contents
            composed of a "type", a "subtype".
        :type mime_type:
            str or None

        :param type:
            (optional) Type part of the ``mime_type`` (e.g.: audio, video).
        :type type:
            str or None

        :param subtype:
            (optional) Sub-type part of the ``mime_type`` (e.g.: mp4, mov).
        :type subtype:
            str or None

        :param file_extension:
            (optional) Alias to ``sub_type``.
        :type file_extension:
            str or None

        :param abr:
            (optional) Average bitrate (ABR) refers to the average amount of
            data transferred per unit of time (e.g.: 64kbps, 192kbps).
        :type abr:
            str or None

        :param bitrate:
            (optional) Alias to ``abr``.
        :type bitrate:
            str or None

        :param video_codec:
            (optional) Video compression format.
        :type video_codec:
            str or None

        :param audio_codec:
            (optional) Audio compression format.
        :type audio_codec:
            str or None

        :param bool progressive:
            Excludes adaptive streams (one file contains both audio and video
            tracks).

        :param bool adaptive:
            Excludes progressive streams (audio and video are on separate
            tracks).

        :param bool only_audio:
            Excludes streams with video tracks.

        :param bool only_video:
            Excludes streams with audio tracks.

        :param custom_filter_functions:
            (optional) Interface for defining complex filters without
            subclassing.
        :type custom_filter_functions:
            list or None

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

        if only_audio:
            filters.append(
                lambda s: (
                    s.includes_audio_track and not s.includes_video_track
                ),
            )

        if only_video:
            filters.append(
                lambda s: (
                    s.includes_video_track and not s.includes_audio_track
                ),
            )

        if progressive:
            filters.append(lambda s: s.is_progressive)

        if adaptive:
            filters.append(lambda s: s.is_adaptive)

        if custom_filter_functions:
            for fn in custom_filter_functions:
                filters.append(fn)

        fmt_streams = self.fmt_streams
        for fn in filters:
            fmt_streams = list(filter(fn, fmt_streams))
        return StreamQuery(fmt_streams)

    def order_by(self, attribute_name):
        """Apply a sort order to a resultset.

        :param str attribute_name:
            The name of the attribute to sort by.
        """
        fmt_streams = sorted(
            self.fmt_streams,
            key=lambda s: getattr(s, attribute_name),
        )
        return StreamQuery(fmt_streams)

    def desc(self):
        """Sort streams in descending order.

        :rtype: :class:`StreamQuery <StreamQuery>`

        """
        return StreamQuery(self.fmt_streams[::-1])

    def asc(self):
        """Sort streams in ascending order.

        :rtype: :class:`StreamQuery <StreamQuery>`

        """
        return self

    def get_by_itag(self, itag):
        """Get the corresponding :class:`Stream <Stream>` for a given itag.

        :param str itag:
            YouTube format identifier code.
        :rtype: :class:`Stream <Stream>` or None
        :returns:
            The :class:`Stream <Stream>` matching the given itag or None if
            not found.

        """
        try:
            return self.itag_index[itag]
        except KeyError:
            pass

    def first(self):
        """Get the first :class:`Stream <Stream>` in the results.

        :rtype: :class:`Stream <Stream>` or None
        :returns:
            the first result of this query or None if the result doesn't
            contain any streams.

        """
        try:
            return self.fmt_streams[0]
        except IndexError:
            pass

    def last(self):
        """Get the last :class:`Stream <Stream>` in the results.

        :rtype: :class:`Stream <Stream>` or None
        :returns:
            Return the last result of this query or None if the result
            doesn't contain any streams.

        """
        try:
            return self.fmt_streams[-1]
        except IndexError:
            pass

    def count(self):
        """Get the count the query would return.

        :rtype: int

        """
        return len(self.fmt_streams)

    def all(self):
        """Get all the results represented by this query as a list.

        :rtype: list

        """
        return self.fmt_streams


class CaptionQuery:
    """Interface for querying the available captions."""

    def __init__(self, captions):
        """Construct a :class:`Caption <Caption>`.

        param list captions:
            list of :class:`Caption <Caption>` instances.

        """
        self.captions = captions
        self.lang_code_index = {c.code: c for c in captions}

    def get_by_language_code(self, lang_code):
        """Get the :class:`Caption <Caption>` for a given ``lang_code``.

        :param str lang_code:
            The code that identifies the caption language.
        :rtype: :class:`Caption <Caption>` or None
        :returns:
            The :class:`Caption <Caption>` matching the given ``lang_code`` or
            None if it does not exist.
        """
        return self.lang_code_index.get(lang_code)

    def all(self):
        """Get all the results represented by this query as a list.

        :rtype: list

        """
        return self.captions
