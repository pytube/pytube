"""
This module contains a container for stream manifest data.

A container object for the media stream (video only / audio only / video+audio
combined). This was referred to as ``Video`` in the legacy pytube version, but
has been renamed to accommodate DASH (which serves the audio and video
separately).
"""
import logging
import os
from math import ceil

from datetime import datetime
import shutil
import sys
from typing import BinaryIO, Callable, Dict, Optional, Tuple
from urllib.error import HTTPError
from urllib.parse import parse_qs

from pytube import extract, request
from pytube.helpers import safe_filename, target_directory
from pytube.itags import get_format_profile
from pytube.monostate import Monostate

logger = logging.getLogger(__name__)


class Stream:
    """Container for stream manifest data."""

    def __init__(
        self, stream: Dict, monostate: Monostate
    ):
        """Construct a :class:`Stream <Stream>`.

        :param dict stream:
            The unscrambled data extracted from YouTube.
        :param dict monostate:
            Dictionary of data shared across all instances of
            :class:`Stream <Stream>`.
        """
        # A dictionary shared between all instances of :class:`Stream <Stream>`
        # (Borg pattern).
        self._monostate = monostate

        self.url = stream["url"]  # signed download url
        self.itag = int(
            stream["itag"]
        )  # stream format id (youtube nomenclature)

        # set type and codec info

        # 'video/webm; codecs="vp8, vorbis"' -> 'video/webm', ['vp8', 'vorbis']
        self.mime_type, self.codecs = extract.mime_type_codec(stream["mimeType"])

        # 'video/webm' -> 'video', 'webm'
        self.type, self.subtype = self.mime_type.split("/")

        # ['vp8', 'vorbis'] -> video_codec: vp8, audio_codec: vorbis. DASH
        # streams return NoneType for audio/video depending.
        self.video_codec, self.audio_codec = self.parse_codecs()

        self.is_otf: bool = stream["is_otf"]
        self.bitrate: Optional[int] = stream["bitrate"]

        # filesize in bytes
        self._filesize: Optional[int] = int(stream.get('contentLength', 0))
        
        # filesize in kilobytes
        self._filesize_kb: Optional[float] = float(ceil(float(stream.get('contentLength', 0)) / 1024 * 1000) / 1000)
        
        # filesize in megabytes
        self._filesize_mb: Optional[float] = float(ceil(float(stream.get('contentLength', 0)) / 1024 / 1024 * 1000) / 1000)
        
        # filesize in gigabytes(fingers crossed we don't need terabytes going forward though)
        self._filesize_gb: Optional[float] = float(ceil(float(stream.get('contentLength', 0)) / 1024 / 1024 / 1024 * 1000) / 1000)

        # Additional information about the stream format, such as resolution,
        # frame rate, and whether the stream is live (HLS) or 3D.
        itag_profile = get_format_profile(self.itag)
        self.is_dash = itag_profile["is_dash"]
        self.abr = itag_profile["abr"]  # average bitrate (audio streams only)
        if 'fps' in stream:
            self.fps = stream['fps']  # Video streams only
        self.resolution = itag_profile[
            "resolution"
        ]  # resolution (e.g.: "480p")
        self.is_3d = itag_profile["is_3d"]
        self.is_hdr = itag_profile["is_hdr"]
        self.is_live = itag_profile["is_live"]

        # --- Progress bar variables ---
        # 'pb' stands for 'progress bar'

        # If true, then progress bar will be shown
        self._pb_show: bool = False

        # Segment character of progress bar
        self._pb_character: str = '█'

        # Number of segments. If value equal to -1,
        # then terminal column value will be got
        self._pb_width: int = -1

        # Value to scale number of segments
        self._pb_scale: float = 0.55

        # Custom display function. If is None, 
        # then progress bar will be just printed to standard output
        self._pb_custom_function: Optional[Callable[[str], None]] = None

        # If true, then progress bar will only contain '_pb_character' and spaces.
        # Example of a progress bar depending on the value:
        #   >>> self._pb_is_raw_string = False
        #    '|███████████████████████████████████████| 100.0%'
        #   >>> self._pb_is_raw_string = True
        #    '███████████████████████████████████████'
        self._pb_is_raw_string: bool = False

    @property
    def is_adaptive(self) -> bool:
        """Whether the stream is DASH.

        :rtype: bool
        """
        # if codecs has two elements (e.g.: ['vp8', 'vorbis']): 2 % 2 = 0
        # if codecs has one element (e.g.: ['vp8']) 1 % 2 = 1
        return bool(len(self.codecs) % 2)

    @property
    def is_progressive(self) -> bool:
        """Whether the stream is progressive.

        :rtype: bool
        """
        return not self.is_adaptive

    @property
    def includes_audio_track(self) -> bool:
        """Whether the stream only contains audio.

        :rtype: bool
        """
        return self.is_progressive or self.type == "audio"

    @property
    def includes_video_track(self) -> bool:
        """Whether the stream only contains video.

        :rtype: bool
        """
        return self.is_progressive or self.type == "video"

    def parse_codecs(self) -> Tuple[Optional[str], Optional[str]]:
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
    def filesize(self) -> int:
        """File size of the media stream in bytes.

        :rtype: int
        :returns:
            Filesize (in bytes) of the stream.
        """
        if self._filesize == 0:
            try:
                self._filesize = request.filesize(self.url)
            except HTTPError as e:
                if e.code != 404:
                    raise
                self._filesize = request.seq_filesize(self.url)
        return self._filesize
    
    @property
    def filesize_kb(self) -> float:
        """File size of the media stream in kilobytes.

        :rtype: float
        :returns:
            Rounded filesize (in kilobytes) of the stream.
        """
        if self._filesize_kb == 0:
            try:
                self._filesize_kb = float(ceil(request.filesize(self.url)/1024 * 1000) / 1000)
            except HTTPError as e:
                if e.code != 404:
                    raise
                self._filesize_kb = float(ceil(request.seq_filesize(self.url)/1024 * 1000) / 1000)
        return self._filesize_kb
    
    @property
    def filesize_mb(self) -> float:
        """File size of the media stream in megabytes.

        :rtype: float
        :returns:
            Rounded filesize (in megabytes) of the stream.
        """
        if self._filesize_mb == 0:
            try:
                self._filesize_mb = float(ceil(request.filesize(self.url)/1024/1024 * 1000) / 1000)
            except HTTPError as e:
                if e.code != 404:
                    raise
                self._filesize_mb = float(ceil(request.seq_filesize(self.url)/1024/1024 * 1000) / 1000)
        return self._filesize_mb

    @property
    def filesize_gb(self) -> float:
        """File size of the media stream in gigabytes.

        :rtype: float
        :returns:
            Rounded filesize (in gigabytes) of the stream.
        """
        if self._filesize_gb == 0:
            try:
                self._filesize_gb = float(ceil(request.filesize(self.url)/1024/1024/1024 * 1000) / 1000)
            except HTTPError as e:
                if e.code != 404:
                    raise
                self._filesize_gb = float(ceil(request.seq_filesize(self.url)/1024/1024/1024 * 1000) / 1000)
        return self._filesize_gb
    
    @property
    def title(self) -> str:
        """Get title of video

        :rtype: str
        :returns:
            Youtube video title
        """
        return self._monostate.title or "Unknown YouTube Video Title"

    @property
    def filesize_approx(self) -> int:
        """Get approximate filesize of the video

        Falls back to HTTP call if there is not sufficient information to approximate

        :rtype: int
        :returns: size of video in bytes
        """
        if self._monostate.duration and self.bitrate:
            bits_in_byte = 8
            return int(
                (self._monostate.duration * self.bitrate) / bits_in_byte
            )

        return self.filesize

    @property
    def expiration(self) -> datetime:
        expire = parse_qs(self.url.split("?")[1])["expire"][0]
        return datetime.utcfromtimestamp(int(expire))

    @property
    def default_filename(self) -> str:
        """Generate filename based on the video title.

        :rtype: str
        :returns:
            An os file system compatible filename.
        """
        filename = safe_filename(self.title)
        return f"{filename}.{self.subtype}"

    def download(
        self,
        output_path: Optional[str] = None,
        filename: Optional[str] = None,
        filename_prefix: Optional[str] = None,
        skip_existing: bool = True,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = 0
    ) -> str:
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
            This is separate from filename so you can use the default
            filename but still add a prefix.
        :type filename_prefix: str or None
        :param skip_existing:
            (optional) Skip existing files, defaults to True
        :type skip_existing: bool
        :param timeout:
            (optional) Request timeout length in seconds. Uses system default.
        :type timeout: int
        :param max_retries:
            (optional) Number of retries to attempt after socket timeout. Defaults to 0.
        :type max_retries: int
        :returns:
            Path to the saved video
        :rtype: str

        """
        file_path = self.get_file_path(
            filename=filename,
            output_path=output_path,
            filename_prefix=filename_prefix,
        )

        if skip_existing and self.exists_at_path(file_path):
            logger.debug(f'file {file_path} already exists, skipping')
            self.on_complete(file_path)
            return file_path

        bytes_remaining = self.filesize
        logger.debug(f'downloading ({self.filesize} total bytes) file to {file_path}')

        with open(file_path, "wb") as fh:
            try:
                for chunk in request.stream(
                    self.url,
                    timeout=timeout,
                    max_retries=max_retries
                ):
                    # reduce the (bytes) remainder by the length of the chunk.
                    bytes_remaining -= len(chunk)
                    # send to the on_progress callback.
                    self.on_progress(chunk, fh, bytes_remaining)
            except HTTPError as e:
                if e.code != 404:
                    raise
                # Some adaptive streams need to be requested with sequence numbers
                for chunk in request.seq_stream(
                    self.url,
                    timeout=timeout,
                    max_retries=max_retries
                ):
                    # reduce the (bytes) remainder by the length of the chunk.
                    bytes_remaining -= len(chunk)
                    # send to the on_progress callback.
                    self.on_progress(chunk, fh, bytes_remaining)
        self.on_complete(file_path)
        return file_path

    def get_file_path(
        self,
        filename: Optional[str] = None,
        output_path: Optional[str] = None,
        filename_prefix: Optional[str] = None,
    ) -> str:
        if not filename:
            filename = self.default_filename
        if filename_prefix:
            filename = f"{filename_prefix}{filename}"
        return os.path.join(target_directory(output_path), filename)

    def exists_at_path(self, file_path: str) -> bool:
        return (
            os.path.isfile(file_path)
            and os.path.getsize(file_path) == self.filesize
        )

    def stream_to_buffer(self, buffer: BinaryIO) -> None:
        """Write the media stream to buffer

        :rtype: io.BytesIO buffer
        """
        bytes_remaining = self.filesize
        logger.info(
            "downloading (%s total bytes) file to buffer", self.filesize,
        )

        for chunk in request.stream(self.url):
            # reduce the (bytes) remainder by the length of the chunk.
            bytes_remaining -= len(chunk)
            # send to the on_progress callback.
            self.on_progress(chunk, buffer, bytes_remaining)
        self.on_complete(None)

    def on_progress(
        self, chunk: bytes, file_handler: BinaryIO, bytes_remaining: int
    ):
        """On progress callback function.

        This function writes the binary data to the file, then checks if an
        additional callback is defined in the monostate. This is exposed to
        allow things like displaying a progress bar.

        :param bytes chunk:
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

        # Show progress bar if 'self.config_progress_bar(show=True, ...)' method was called
        if self._pb_show:
            self.__show_progress_bar(bytes_remaining)

        file_handler.write(chunk)
        logger.debug("download remaining: %s", bytes_remaining)
        if self._monostate.on_progress:
            self._monostate.on_progress(self, chunk, bytes_remaining)

    def on_complete(self, file_path: Optional[str]):
        """On download complete handler function.

        :param file_path:
            The file handle where the media is being written to.
        :type file_path: str

        :rtype: None

        """
        logger.debug("download finished")
        on_complete = self._monostate.on_complete
        if on_complete:
            logger.debug("calling on_complete callback %s", on_complete)
            on_complete(self, file_path)

    def configure_progress_bar(self, *,
        show: bool,
        character: str = '█',
        scale: float = 0.55,
        width: int = -1,
        custom_function: Optional[Callable[[str], None]] = None,
        raw_string: bool = False,
    ) -> 'Stream':
        """Configure a simple, pretty progress bar.

        Example:
        ~~~~~~~~
         |███████████████████████████████████████| 100.0%

        :param show: (Required) If set to true, then progress bar will be shown.
        :type: bool
        :param character: Character to use for presenting progress segment.
        :type: str
        :param scale: Scale multiplier to reduce progress bar size.
        :type: float
        :param width: Width of a progress bar. If set to -1, then terminal column width will be used as default.
        :type: int
        :param custom_function: (Optional) Custom display function. If is None, then progress bar will be just printed to standard output
        :type: ((str) -> None)
        :param raw_string: Display only progress segments without percentage and additional formatting.
        Useful with custom function.
        Example of a progress bar depending on the value:
            >>> raw_string = False
            '|████████████████████████████████████   | 82.95%'
            >>> raw_string = True
            '█████████████████████████████████████  '
        :type: bool

        :rtype: Stream
        :returns: an instance of this class
        """

        # Setup all attributes for the progress bar
        self._pb_show = show
        self._pb_character = character
        self._pb_width = max(width, -1) # accept integers: [-1; +infinity)
        self._pb_scale = scale
        self._pb_custom_function = custom_function
        self._pb_is_raw_string = raw_string

        return self

    def __repr__(self) -> str:
        """Printable object representation.

        :rtype: str
        :returns:
            A string representation of a :class:`Stream <Stream>` object.
        """
        parts = ['itag="{s.itag}"', 'mime_type="{s.mime_type}"']
        if self.includes_video_track:
            parts.extend(['res="{s.resolution}"', 'fps="{s.fps}fps"'])
            if not self.is_adaptive:
                parts.extend(
                    ['vcodec="{s.video_codec}"', 'acodec="{s.audio_codec}"',]
                )
            else:
                parts.extend(['vcodec="{s.video_codec}"'])
        else:
            parts.extend(['abr="{s.abr}"', 'acodec="{s.audio_codec}"'])
        parts.extend(['progressive="{s.is_progressive}"', 'type="{s.type}"'])
        return f"<Stream: {' '.join(parts).format(s=self)}>"

    def __show_progress_bar(self, bytes_remaining: int):
        """Display a simple, pretty progress bar during a downloading process.

        Copy of 'pytube.cli.display_progress_bar' function with some changes.

        Example:
        ~~~~~~~~
         |███████████████████████████████████████| 100.0%

        :param bytes_remaining: Number of bytes left to download
        :type: int
        """

        bytes_received = self.filesize - bytes_remaining

        # Determine the width of a segments of a progress bar
        if self._pb_width == -1: # by a number of columns in a terminal
            columns = shutil.get_terminal_size().columns
        else: # by the specified value
            columns = self._pb_width

        # Adjust width with scaling value
        max_width = int(columns * self._pb_scale)

        # Construct resulting progress bar
        filled = int(round(max_width * bytes_received / float(self.filesize)))
        remaining = max_width - filled
        progress_bar = self._pb_character * filled + " " * remaining
        percent = round(100.0 * bytes_received / float(self.filesize), 1)

        # Determine a format of the final progress bar
        if not self._pb_is_raw_string:
            text = f" |{progress_bar}| {percent}%\r"
        else:
            text = progress_bar

        # Determine a way to display progress bar
        if self._pb_custom_function is not None:
            self._pb_custom_function(text)
        else:
            sys.stdout.write(text)
            sys.stdout.flush()
