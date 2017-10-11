# -*- coding: utf-8 -*-
"""Library specific exception definitions."""
import socket
import sys
from traceback import format_tb

from pytube.compat import URLError


class PytubeError(Exception):
    """Base pytube exception that all others inherent.

    This is done to not pollute the built-in exceptions, which *could* result
    in unintended errors being unexpectedly and incorrectly handled within
    implementers code.
    """


class ExtractError(PytubeError):
    """Data extraction based exception."""

    def __init__(self, msg, tb=None, expected=False, video_id=None):
        """Construct an instance of a :class:`ExtractError <ExtractError>`.

        :param str msg:
            User defined error message.
        :param list tb:
            Stack trace leading up to the exception.
        :param bool expected:
            Whether the exception being raised requires filing a bug report.
        :param str video_id:
            A YouTube video identifer.
        """
        # get information about the most recent exception caught by an except
        # clause
        exception_type, _, _ = sys.exc_info()

        if exception_type in (URLError, socket.timeout):
            expected = True

        if video_id is not None:
            msg = '{video_id}: {msg}'.format(video_id=video_id, msg=msg)

        if not expected:
            # TODO(nficano): bug report
            pass

        super(ExtractError, self).__init__(msg)

        self.traceback = tb
        self.exc_info = sys.exc_info()
        self.video_id = video_id

    def format_traceback(self):
        """Pretty-print the traceback."""
        if self.traceback:
            return ''.join(format_tb(self.traceback))


class RegexMatchError(ExtractError):
    """Regex pattern did not return any matches."""


class AgeRestrictionError(ExtractError):
    """Content is age restricted."""
