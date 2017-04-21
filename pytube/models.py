#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from utils import download_youtube_data, FFMpeg

try:
    from urllib2 import urlopen
except ImportError:
    from urllib.request import urlopen


class Video(object):
    """Class representation of a single instance of a YouTube video.
    """
    def __init__(self, url, filename, extension, resolution=None,
                 video_codec=None, profile=None, video_bitrate=None,
                 audio_codec=None, audio_bitrate=None):
        """Sets-up the video object.

        :param str url:
            The url of the video. (e.g.: https://youtube.com/watch?v=...)
        :param str filename:
            The filename (minus the extention) to save the video.
        :param str extention:
            The desired file extention (e.g.: mp4, flv, webm).
        :param str resolution:
            *Optional* The broadcasting standard (e.g.: 720p, 1080p).
        :param str video_codec:
            *Optional* The codec used to encode the video.
        :param str profile:
            *Optional* The arbitrary quality profile.
        :param str video_bitrate:
            *Optional* The bitrate of the video over sampling interval.
        :param str audio_codec:
            *Optional* The codec used to encode the audio.
        :param str audio_bitrate:
            *Optional* The bitrate of the video's audio over sampling interval.
        """
        self.url = url
        self.filename = filename
        self.extension = extension
        self.resolution = resolution
        self.video_codec = video_codec
        self.profile = profile
        self.video_bitrate = video_bitrate
        self.audio_codec = audio_codec
        self.audio_bitrate = audio_bitrate
        # audio url for the 1080p stream
        self.audio_url = None

    def download(self, base_path, force_overwrite=False):
        """Downloads the video.

        :param str base_path:
            The destination output directory.
        :param bool force_overwrite:
            *Optional* force a file overwrite if conflicting one exists.
        """
        # check if the base_path exists or not
        if not os.path.exists(base_path):
            raise OSError('Please provide an existing base path')
        base_path = os.path.normpath(base_path)
        # create the video path to save the video stream
        video_name = '.'.join([self.filename, self.extension])
        video_path = os.path.join(base_path, video_name)
        # download the video data
        video = download_youtube_data(url=self.url, path=video_path,
                                      force_overwrite=force_overwrite)
        # check if self.audio_url is not None, if so then download
        # the audio stream too and add it to the video
        if self.audio_url is not None:
            # is it always the .webm extension for the audio stream?
            audio_path = os.path.join(base_path, 'audio.webm')
            audio = download_youtube_data(url=self.audio_url,
                                          path=audio_path)
            if audio and video:
                # add the audio stream to the video stream
                output = '.'.join(['%s-%s' % (self.filename, self.resolution),
                                   self.extension])
                output = os.path.join(base_path, output)
                # instantiate the FFMpeg instance
                f = FFMpeg()
                f.add_audio_stream(video_path, audio_path, output)
                # remove the separate streams when done with ffmpeg
                os.remove(video_path)
                os.remove(audio_path)
                return True

        return video

    def __repr__(self):
        """A clean representation of the class instance."""
        return "<Video: {0} (.{1}) - {2} - {3}>".format(
            self.video_codec, self.extension, self.resolution, self.profile)

    def __lt__(self, other):
        """The "less than" (lt) method is used for comparing video object to
        one another. This useful when sorting.

        :param other:
            The instance of the other video instance for comparison.
        """
        if isinstance(other, Video):
            v1 = "{0} {1}".format(self.extension, self.resolution)
            v2 = "{0} {1}".format(other.extension, other.resolution)
            return (v1 > v2) - (v1 < v2) < 0
