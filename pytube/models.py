#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from time import clock

try:
    from urllib2 import urlopen
except ImportError:
    from urllib.request import urlopen


class Video(object):
    """Class representation of a single instance of a YouTube video.
    """
    def __init__(self, url, filename, **attributes):
        """Sets-up the video object.

        :param str url:
            The url of the video. (e.g.: https://youtube.com/watch?v=...)
        :param str filename:
            The filename (minus the extention) to save the video.
        :param **attributes:
            Additional keyword arguments for additional quality profile
            attribures.
        """
        self.url = url
        self.filename = filename
        # TODO: this a bit hacky, rewrite to be explicit.
        self.__dict__.update(**attributes)

    def download(self, path='', chunk_size=8 * 1024, on_progress=None,
                 on_finish=None, force_overwrite=False):
        """Downloads the video.

        :param str path:
            The destination output directory.
        :param int chunk_size:
            File size (in bytes) to write to buffer at a time. By default,
            this is set to 8 bytes.
        :param func on_progress:
            The function to be called every time the buffer is written
            to. Arguments passed are the bytes recieved, file size, and start
            datetime.
        :param func on_finish:
            The function to be called when the download is complete. Arguments
            passed are the full path to downloaded the file.
        :param bool force_overwrite:
            Force a file overwrite if conflicting one exists.
        """
        if os.path.isdir(os.path.normpath(path)):
            path = (os.path.normpath(path) + '/' if path else '')
            fullpath = '{}{}.{}'.format(path, self.filename, self.extension)
        else:
            fullpath = os.path.normpath(path)

        # TODO: Move this into cli, this kind of logic probably shouldn't be
        # handled by the library.
        if os.path.isfile(fullpath) and not force_overwrite:
            raise OSError("Conflicting filename:'{}'".format(self.filename))

        response = urlopen(self.url)
        meta_data = dict(response.info().items())
        file_size = int(meta_data.get("Content-Length") or
                        meta_data.get("content-length"))
        self._bytes_received = 0
        start = clock()
        try:
            with open(fullpath, 'wb') as dst_file:
                while True:
                    self._buffer = response.read(chunk_size)
                    # If the buffer is empty (aka no bytes remaining).
                    if not self._buffer:
                        if on_finish:
                            # TODO: We possibly want to flush the
                            # `_bytes_recieved`` buffer before we call
                            # ``on_finish()``.
                            on_finish(fullpath)
                        break

                    self._bytes_received += len(self._buffer)
                    dst_file.write(self._buffer)
                    if on_progress:
                        on_progress(self._bytes_received, file_size, start)

        # Catch possible exceptions occurring during download.
        except IOError:
            raise IOError("Failed to open file.")

        except BufferError:
            raise BufferError("Failed to write video to file.")

        except KeyboardInterrupt:
            # TODO: Move this into the cli, ``KeyboardInterrupt`` handling
            # should be taken care of by the client.
            os.remove(fullpath)
            raise KeyboardInterrupt("Interrupt signal given. Deleting "
                                    "incomplete video.")

    def __repr__(self):
        """A clean representation of the class instance."""
        return "<Video: {} (.{}) - {} - {}>".format(
            self.video_codec, self.extension, self.resolution, self.profile)

    def __lt__(self, other):
        """The "less than" (lt) method is used for comparing video object to
        one another. This useful when sorting.

        :param Video other:
            The instance of the other video instance for comparison.
        """
        if isinstance(other, Video):
            v1 = "{0} {1}".format(self.extension, self.resolution)
            v2 = "{0} {1}".format(other.extension, other.resolution)
            return (v1 > v2) - (v1 < v2) < 0
