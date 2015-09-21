#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from os import remove
from os.path import normpath, isfile, isdir
from time import clock
import logging

try:
    from urllib2 import urlopen
except ImportError:
    from urllib.request import urlopen

from pytube.utils import sizeof


class Video(object):
    """Class representation of a single instance of a YouTube video.
    """
    def __init__(self, url, filename, **attributes):
        """
        Define the variables required to declare a new video.

        :param extention:
            The file extention the video should be saved as.
        :param resolution:
            The broadcasting standard of the video.
        :param url:
            The url of the video. (e.g.: youtube.com/watch?v=..)
        :param filename:
            The filename (minus the extention) to save the video.
        """

        self.url = url
        self.filename = filename
        self.__dict__.update(**attributes)

    def download(self, path='', chunk_size=8 * 1024, on_progress=None,
                 on_finish=None, force_overwrite=False):
        """
        Downloads the file of the URL defined within the class
        instance.

        :param path:
            Destination directory
        :param chunk_size:
            File size (in bytes) to write to buffer at a time (default: 8
            bytes).
        :param on_progress:
            A function to be called every time the buffer was written
            out. Arguments passed are the current and the full size.
        :param on_finish:
            To be called when the download is finished. The full path to the
            file is passed as an argument.
        """

        if isdir(normpath(path)):
            path = (normpath(path) + '/' if path else '')
            fullpath = '{0}{1}.{2}'.format(path, self.filename, self.extension)
        else:
            fullpath = normpath(path)

        # Check for conflicting filenames
        if isfile(fullpath) and not force_overwrite:
            raise OSError("\Error: Conflicting filename:'{}'".format(
                self.filename))

        response = urlopen(self.url)
        meta_data = dict(response.info().items())
        file_size = int(meta_data.get("Content-Length") or
                        meta_data.get("content-length"))
        self._bytes_received = 0
        start = clock()
        try:
            with open(fullpath, 'wb') as dst_file:
                # Print downloading message.
                logging.info("Downloading: '%s.%s' (Bytes: %s) to path: %s",
                             self.filename, self.extension, sizeof(file_size),
                             path)
                while True:
                    self._buffer = response.read(chunk_size)
                    if not self._buffer:
                        if on_finish:
                            on_finish(fullpath)
                        break

                    self._bytes_received += len(self._buffer)
                    dst_file.write(self._buffer)
                    if on_progress:
                        on_progress(self._bytes_received, file_size, start)

        # Catch possible exceptions occurring during download
        except IOError:
            raise IOError("Error: Failed to open file. Check that: ('{0}'), "
                          "is a valid pathname. " "Or that ('{1}.{2}') is a "
                          "valid filename.".format(path, self.filename,
                                                   self.extension))

        except BufferError:
            raise BufferError("Error: Failed on writing buffer. Failed "
                              "to write video to file.")

        except KeyboardInterrupt:
            remove(fullpath)
            raise KeyboardInterrupt("Interrupt signal given. Deleting "
                                    "incomplete video('{0}.{1}')."
                                    .format(self.filename, self.extension))

    def __repr__(self):
        """A cleaner representation of the class instance."""
        return "<Video: {0} (.{1}) - {2} - {3}>".format(
            self.video_codec, self.extension, self.resolution, self.profile)

    def __lt__(self, other):
        if isinstance(other, Video):
            v1 = "{0} {1}".format(self.extension, self.resolution)
            v2 = "{0} {1}".format(other.extension, other.resolution)
            return (v1 > v2) - (v1 < v2) < 0
