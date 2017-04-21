#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import argparse
import re
import math

from os import path
from sys import stdout
from time import clock
from urllib2 import urlopen
from subprocess import Popen, PIPE
from pytube.exceptions import PytubeError, FFMpegDoesNotExistError, \
    FFMpegAlreadyExistsError


class FullPaths(argparse.Action):
    """Expand user- and relative-paths"""
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, path.abspath(path.expanduser(values)))


# bundle the ffmpeg functionality in a class
class FFMpeg(object):
    def __init__(self, ffmpeg_path=None):
        """
        :param ffmpeg_path: the path of the ffmpeg binary
        """
        def get_ffmpeg_path():
            for d in os.getenv('PATH', os.defpath).split(':'):
                _ffmpeg_path = os.path.join(d, 'ffmpeg')
                if os.path.exists(_ffmpeg_path) and os.access(_ffmpeg_path, os.X_OK):
                    return _ffmpeg_path
            return None

        self.ffmpeg_path = ffmpeg_path or get_ffmpeg_path()
        # check if ffmpeg_binary is present, if not raise
        # an error
        if not os.path.exists(self.ffmpeg_path):
            raise FFMpegDoesNotExistError('Make sure the ffmpeg binary exists')

    @staticmethod
    def _spawn(cmds):
        """
        Static method to spawn a process using the
        subprocess.Popen class.
        :param cmds: the commands for the process
        :return:
        """
        try:
            p = Popen(cmds, stdin=PIPE, stdout=PIPE,
                      stderr=PIPE)
            stdout, _ = p.communicate()
            return stdout, _
        # what exceptions should we handle in here?
        except Exception:
            pass

    def add_audio_stream(self, video_path, audio_path,
                         output):
        """
        Method to add an audio stream to a video
        which does not have one.
        :param video_path: the path of the video stream
        :param audio_path: the path of the audio stream
        :param output: the final video file
        :return:
        """
        if os.path.exists(output):
            raise FFMpegAlreadyExistsError('%s already exists' % output)
        # define the commands for this operation
        cmds = [self.ffmpeg_path, '-i', video_path, '-i',
                audio_path, '-c:v', 'copy', '-c:a', 'aac',
                output]
        self._spawn(cmds)


def get_itag(url):
    """
    Finds the itag value in a url.
    :param url: the sepcific video url.
    :return:
    """
    # compile the regular expression for
    # matching the itag parameter in the url
    itag_regex = re.compile('itag=(\d+)')
    results = itag_regex.findall(url)

    if len(results):
        return int(results[0])


def download_youtube_data(url, path, chunk_size=8*1024,
                          force_overwrite=False):
    """
    Downloads streams of data from youtube such as audio
    streams, video streams or both.
    :param url: the url of the audio/video to download
    :param path: the file path where to save the data stream
    :param chunk_size: data chunk to receive
    :param force_overwrite: overwrites the existing path
    :return: True or None
    """
    # if the path exists and force_overwrite is not True,
    # then raise an exception
    if os.path.exists(path) and not force_overwrite:
        raise PytubeError('Path already exists')
    # open the url for retrieving data
    response = urlopen(url)
    try:
        with open(path, 'wb') as df:
            while True:
                _buffer = response.read(chunk_size)
                # shitty hack to tell if finished
                if not _buffer:
                    return True
                # write the _buffer to the destination file
                df.write(_buffer)
    except KeyboardInterrupt:
        os.remove(path)
        raise KeyboardInterrupt('Deleting the incomplete file')

    # None is returned by default, but this makes the code more
    # readable
    return None


def truncate(text, max_length=200):
    return text[:max_length].rsplit(' ', 0)[0]


def safe_filename(text, max_length=200):
    """Sanitizes filenames for many operating systems.

    :params text: The unsanitized pending filename.
    """

    # Tidy up ugly formatted filenames.
    text = text.replace('_', ' ')
    text = text.replace(':', ' -')

    # NTFS forbids filenames containing characters in range 0-31 (0x00-0x1F)
    ntfs = [chr(i) for i in range(0, 31)]

    # Removing these SHOULD make most filename safe for a wide range of
    # operating systems.
    paranoid = ['\"', '\#', '\$', '\%', '\'', '\*', '\,', '\.', '\/', '\:',
                '\;', '\<', '\>', '\?', '\\', '\^', '\|', '\~', '\\\\']

    blacklist = re.compile('|'.join(ntfs + paranoid), re.UNICODE)
    filename = blacklist.sub('', text)
    return truncate(filename)


def sizeof(byts):
    """Takes the size of file or folder in bytes and returns size formatted in
    KB, MB, GB, TB or PB.
    :params byts:
        Size of the file in bytes
    """
    sizes = ['bytes', 'KB', 'MB', 'GB', 'TB', 'PB']
    power = int(math.floor(math.log(byts, 1024)))
    value = int(byts/float(1024**power))
    suffix = sizes[power] if byts != 1 else 'byte'
    return '{0} {1}'.format(value, suffix)


def print_status(progress, file_size, start):
    """
    This function - when passed as `on_progress` to `Video.download` - prints
    out the current download progress.

    :params progress:
        The lenght of the currently downloaded bytes.
    :params file_size:
        The total size of the video.
    :params start:
        The time when started
    """

    percent_done = int(progress) * 100. / file_size
    done = int(50 * progress / int(file_size))
    dt = (clock() - start)
    if dt > 0:
        stdout.write("\r  [%s%s][%3.2f%%] %s at %s/s\r " %
                     ('=' * done, ' ' * (50 - done), percent_done,
                      sizeof(file_size), sizeof(progress // dt)))
    stdout.flush()
