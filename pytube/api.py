from __future__ import unicode_literals

from .exceptions import MultipleObjectsReturned, YouTubeError
from .models import Video
from .utils import safe_filename
from urllib import urlencode
from urllib2 import urlopen
from urlparse import urlparse, parse_qs, unquote

import re

YT_BASE_URL = 'http://www.youtube.com/get_video_info'

#YouTube quality and codecs id map.
#source: http://en.wikipedia.org/wiki/YouTube#Quality_and_codecs
YT_ENCODING = {
    #Flash Video
    5: ["flv", "240p", "Sorenson H.263", "N/A", "0.25", "MP3", "64"],
    6: ["flv", "270p", "Sorenson H.263", "N/A", "0.8", "MP3", "64"],
    34: ["flv", "360p", "H.264", "Main", "0.5", "AAC", "128"],
    35: ["flv", "480p", "H.264", "Main", "0.8-1", "AAC", "128"],

    #3GP
    36: ["3gp", "240p", "MPEG-4 Visual", "Simple", "0.17", "AAC", "38"],
    13: ["3gp", "N/A", "MPEG-4 Visual", "N/A", "0.5", "AAC", "N/A"],
    17: ["3gp", "144p", "MPEG-4 Visual", "Simple", "0.05", "AAC", "24"],

    #MPEG-4
    18: ["mp4", "360p", "H.264", "Baseline", "0.5", "AAC", "96"],
    22: ["mp4", "720p", "H.264", "High", "2-2.9", "AAC", "192"],
    37: ["mp4", "1080p", "H.264", "High", "3-4.3", "AAC", "192"],
    38: ["mp4", "3072p", "H.264", "High", "3.5-5", "AAC", "192"],
    82: ["mp4", "360p", "H.264", "3D", "0.5", "AAC", "96"],
    83: ["mp4", "240p", "H.264", "3D", "0.5", "AAC", "96"],
    84: ["mp4", "720p", "H.264", "3D", "2-2.9", "AAC", "152"],
    85: ["mp4", "520p", "H.264", "3D", "2-2.9", "AAC", "152"],

    #WebM
    43: ["webm", "360p", "VP8", "N/A", "0.5", "Vorbis", "128"],
    44: ["webm", "480p", "VP8", "N/A", "1", "Vorbis", "128"],
    45: ["webm", "720p", "VP8", "N/A", "2", "Vorbis", "192"],
    46: ["webm", "1080p", "VP8", "N/A", "N/A", "Vorbis", "192"],
    100: ["webm", "360p", "VP8", "3D", "N/A", "Vorbis", "128"],
    101: ["webm", "360p", "VP8", "3D", "N/A", "Vorbis", "192"],
    102: ["webm", "720p", "VP8", "3D", "N/A", "Vorbis", "192"]
}

# The keys corresponding to the quality/codec map above.
YT_ENCODING_KEYS = (
    'extension', 'resolution', 'video_codec', 'profile', 'video_bitrate',
    'audio_codec', 'audio_bitrate'
)


class YouTube(object):
    _filename = None
    _fmt_values = []
    _video_url = None
    title = None
    videos = []
    # fmt was an undocumented URL parameter that allowed selecting
    # YouTube quality mode without using player user interface.

    @property
    def url(self):
        """Exposes the video url."""
        return self._video_url

    @url.setter
    def url(self, url):
        """ Defines the URL of the YouTube video."""
        self._video_url = url
        #Reset the filename.
        self._filename = None
        #Get the video details.
        self._get_video_info()

    @property
    def filename(self):
        """
        Exposes the title of the video. If this is not set, one is
        generated based on the name of the video.
        """
        if not self._filename:
            self._filename = safe_filename(self.title)
        return self._filename

    @filename.setter
    def filename(self, filename):
        """ Defines the filename."""
        self._filename = filename
        if self.videos:
            for video in self.videos:
                video.filename = filename

    @property
    def video_id(self):
        """Gets the video ID extracted from the URL."""
        parts = urlparse(self._video_url)
        qs = getattr(parts, 'query', None)
        if qs:
            video_id = parse_qs(qs).get('v', None)
            if video_id:
                return video_id.pop()

    def get(self, extension=None, resolution=None):
        """
        Return a single video given an extention and resolution.

        Keyword arguments:
        extention -- The desired file extention (e.g.: mp4).
        resolution -- The desired video broadcasting standard.
        """
        result = []
        for v in self.videos:
            if extension and v.extension != extension:
                continue
            elif resolution and v.resolution != resolution:
                continue
            else:
                result.append(v)
        if not len(result):
            return
        elif len(result) is 1:
            return result[0]
        else:
            d = len(result)
            raise MultipleObjectsReturned("get() returned more than one "
                                          "object -- it returned {}!".format(d))

    def filter(self, extension=None, resolution=None):
        """
        Return a filtered list of videos given an extention and
        resolution criteria.

        Keyword arguments:
        extention -- The desired file extention (e.g.: mp4).
        resolution -- The desired video broadcasting standard.
        """
        results = []
        for v in self.videos:
            if extension and v.extension != extension:
                continue
            elif resolution and v.resolution != resolution:
                continue
            else:
                results.append(v)
        return results

    def _fetch(self, path, data):
        """
        Given a path, traverse the response for the desired data. (A
        modified ver. of my dictionary traverse method:
        https://gist.github.com/2009119)

        Keyword arguments:
        path -- A tuple representing a path to a node within a tree.
        data -- The data containing the tree.
        """
        elem = path[0]
        #Get first element in tuple, and check if it contains a list.
        if type(data) is list:
            # Pop it, and let's continue..
            return self._fetch(path, data.pop())
        #Parse the url encoded data
        data = parse_qs(data)
        #Get the element in our path
        data = data.get(elem, None)
        #Offset the tuple by 1.
        path = path[1::1]
        #Check if the path has reached the end OR the element return
        #nothing.
        if len(path) is 0 or data is None:
            if type(data) is list and len(data) is 1:
                data = data.pop()
            return data
        else:
            # Nope, let's keep diggin'
            return self._fetch(path, data)

    def _parse_stream_map(self, data):
        """
        Python's `parse_qs` can't properly decode the stream map
        containing video data so we use this instead.

        Keyword arguments:
        data -- The parsed response from YouTube.
        """
        videoinfo = {
            "itag": [],
            "url": [],
            "quality": [],
            "fallback_host": [],
            "sig": [],
            "type": []
        }
        text = data["url_encoded_fmt_stream_map"][0]
        # Split individual videos
        videos = text.split(",")
        # Unquote the characters and split to parameters
        videos = [video.split("&") for video in videos]

        for video in videos:
            for kv in video:
                key, value = kv.split("=")
                videoinfo.get(key, []).append(unquote(value))

        return videoinfo

    def _get_video_info(self):
        """
        This is responsable for executing the request, extracting the
        necessary details, and populating the different video
        resolutions and formats into a list.
        """
        querystring = urlencode({'asv': 3, 'el': 'detailpage', 'hl': 'en_US',
                                 'video_id': self.video_id})

        self.title = None
        self.videos = []

        response = urlopen(YT_BASE_URL + '?' + querystring)

        if response:
            content = response.read().decode()
            data = parse_qs(content)
            if 'errorcode' in data:
                error = data.get('reason', 'An unknown error has occurred')
                if isinstance(error, list):
                    error = error.pop()
                raise YouTubeError(error)

            stream_map = self._parse_stream_map(data)
            video_urls = stream_map["url"]
            #Apparently signatures are not needed as of 2014-02-28
            self.title = self._fetch(('title',), content)

            for idx in range(len(video_urls)):
                url = video_urls[idx]
                try:
                    fmt, data = self._extract_fmt(url)
                except (TypeError, KeyError):
                    pass
                else:
                    v = Video(url, self.filename, **data)
                    self.videos.append(v)
                    self._fmt_values.append(fmt)
            self.videos.sort()

    def _extract_fmt(self, text):
        """
        YouTube does not pass you a completely valid URLencoded form,
        I suspect this is suppose to act as a deterrent.. Nothing some
        regulular expressions couldn't handle.

        Keyword arguments:
        text -- The malformed data contained within each url node.
        """
        itag = re.findall('itag=(\d+)', text)
        if itag and len(itag) is 1:
            itag = int(itag[0])
            attr = YT_ENCODING.get(itag, None)
            if not attr:
                return itag, None
            data = {}
            map(lambda k, v: data.update({k: v}), YT_ENCODING_KEYS, attr)
            return itag, data
