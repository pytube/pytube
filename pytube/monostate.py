import io
from typing import Any, Optional
from typing_extensions import Protocol

# from __future__ import annotations


class OnProgress(Protocol):
    def __call__(
        self,
        stream: Any,
        chunk: Any,
        file_handler: io.BufferedWriter,
        bytes_remaining: int,
    ) -> None:
        ...

    """On download progress callback function.

    :param stream:
        An instance of :class:`Stream <Stream>` being downloaded.
    :type stream:
        :py:class:`pytube.Stream`
    :param str chunk:
        Segment of media file binary data, not yet written to disk.
    :param file_handler:
        The file handle where the media is being written to.
    :type file_handler:
        :py:class:`io.BufferedWriter`
    :param int bytes_remaining:
        How many bytes have been downloaded.

    """


class OnComplete(Protocol):
    def __call__(self, stream: Any, file_handler: io.BufferedWriter) -> None:
        ...

    """On download complete handler function.

    :param stream:
        An instance of :class:`Stream <Stream>` being downloaded.
    :type stream:
        :py:class:`pytube.Stream`
    :param file_handler:
        The file handle where the media is being written to.
    :type file_handler:
        :py:class:`io.BufferedWriter`

    :rtype: None
    """


class Monostate:
    def __init__(
        self, on_progress: Optional[OnProgress], on_complete: Optional[OnComplete]
    ):
        self.on_progress = on_progress
        self.on_complete = on_complete
