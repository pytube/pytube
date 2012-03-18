# Copyright (c) 2012 Nick Ficano.

# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

from urlparse import urlparse, parse_qs
from unicodedata import normalize

import re
import requests
import urllib2

YT_BASE_URL = 'http://www.youtube.com/get_video_info'
# YouTube media encoding options
YT_ENCODING = {
    5: (5, "flv", "224p"),
    6: (6, "flv", "270p"),
    34: (34, "flv", "360p"),
    35: (35, "flv", "480p"),
    18: (18, "mp4", "360p"),
    22: (22, "mp4", "720p"),
    37: (37, "mp4", "1080p"),
    43: (43, "webm", "360p"),
    44: (44, "webm", "480p"),
    45: (45, "webm", "720p"),
    46: (46, "webm", "1080p"),
}


class Video(object):
    """
    Class representation of a single instance of a YouTube video.
    """
    def __init__(self, extension, resolution, url, filename):
        """
        Define the variables required to declare a new video.

        Keyword arguments:
        extention -- The file extention the video should be saved as.
        resolution -- The broadcasting standard of the video.
        url -- The url of the video. (e.g.: http://www.youtube.com/watch?v=..)
        filename -- The filename (minus the extention) to save the video.
        """
        self.extension = extension
        self.resolution = resolution
        self.url = url
        self.filename = filename

    def download(self):
        """Downloads the file of the URL defined within the class instance."""
        response = urllib2.urlopen(self.url)
        #TODO: Allow a destination path to be specified.
        dst_file = open(self.filename, 'wb')
        meta_data = response.info()
        file_size = int(meta_data.getheaders("Content-Length")[0])
        print "Downloading: %s Bytes: %s" % (self.filename, file_size)

        bytes_received = 0
        chunk_size = 8192
        while True:
            buffer = response.read(chunk_size)
            if not buffer:
                break

            bytes_received += len(buffer)
            dst_file.write(buffer)
            percent = bytes_received * 100. / file_size
            status = r"%10d  [%3.2f%%]" % (bytes_received, percent)
            status = status + chr(8) * (len(status) + 1)
            print status,
        dst_file.close()

    def __repr__(self):
        """A cleaner representation of the class instance."""
        return "<Video: %s - %s>" % (self.extension, self.resolution)


class YouTube(object):
    _filename = None
    _fmt_values = []
    _video_url = None
    title = None
    videos = []
    # fmt was an undocumented URL parameter that allowed selecting YouTube
    # quality mode without using player user interface.

    @property
    def url(self):
        """Exposes the video url."""
        return self._video_url

    @url.setter
    def url(self, url):
        self._video_url = url
        self._get_video_info()

    @property
    def filename(self):
        """Exposes the title of the video."""
        if not self._filename:
            self._filename = slugify(self.title)
        return self._filename

    @filename.setter
    def filename(self, filename):
        self._filename = filename

    @property
    def video_id(self):
        parts = urlparse(self._video_url)
        qs = getattr(parts, 'query', None)
        if qs:
            video_id = parse_qs(qs).get('v', None)
            if video_id:
                return video_id.pop()

    def get(self, extension=None, res=None):
        result = []
        for v in self.videos:
            if extension and v.extension != extension:
                continue
            elif res and v.resolution != res:
                continue
            else:
                result.append(v)
        if len(result) is 1:
            #BUG: This fucks up occasionally..
            return result.pop()
        else:
            raise

    def filter(self, extension=None, res=None):
        results = []
        for v in self.videos:
            if extension and v.extension != extension:
                continue
            elif res and v.resolution != res:
                continue
            else:
                results.append(v)
        return results

    def _fetch(self, path, data):
        elem = path[0]
        if type(data) is list:
            return self._fetch(path, data.pop())
        data = parse_qs(data)
        data = data.get(elem, None)
        path = path[1::1]
        if len(path) is 0 or data is None:
            if type(data) is list and len(data) is 1:
                data = data.pop()
            return data
        else:
            return self._fetch(path, data)

    def _get_video_info(self):
        querystring = {
            'asv': 3,
            'el': 'detailpage',
            'hl': 'en_US',
            'video_id': self.video_id
        }

        response = requests.get(YT_BASE_URL, params=querystring)
        if response.ok:
            content = response.content
            path = ('url_encoded_fmt_stream_map', 'itag')
            encoding_options = self._fetch(path, content)
            self.title = self._fetch(('title',), content)

            for video in encoding_options:
                url = self._extract_url(video)
                if not url:
                    continue

                fmt, extension, resolution = self._extract_fmt(video)

                if fmt in self._fmt_values:
                    continue

                filename = "%s.%s" % (self.filename, extension)

                self.videos.append(
                    Video(extension, resolution, url, filename)
                )

                self._fmt_values.append(fmt)

    def _extract_fmt(self, text):
        """
        YouTube does not pass you a completely valid URLencoded form, I suspect
        this is suppose to act as a deterrent.. Nothing some regulular
        expressions couldn't handle.

        Keyword arguments:
        text -- The malformed data contained within each url node.
        """
        itag = re.findall('itag=(\d+)', text)
        if itag and len(itag) is 1:
            itag = int(itag[0])
            return YT_ENCODING.get(itag, None)

    def _extract_url(self, text):
        """
        (I hate to be redundant here, but whatever) YouTube does not pass you a
        completely valid URLencoded form, I suspect this is suppose to act as a
        deterrent.. Nothing some regulular expressions couldn't handle.

        Keyword arguments:
        text -- The malformed data contained in the itag node.
        """
        url = re.findall('url=(.*)', text)
        if url and len(url) is 1:
            return url[0]


def slugify(text):
    """
    Santizes the video text, generating a valid filename.

    Keyword arguments:
    text -- The text corpus to make file name save.
    """
    strip = re.compile(r'[^\w\s-]')

    if not isinstance(text, unicode):
        text = unicode(text)
        #BUG: Fails trying to interpet non-ascii characters.
        #UTF-8.. we get it.
        text = normalize('NFKD', text).encode('ascii', 'ignore')
        text = unicode(strip.sub('', text).strip())
        return unicode(text)
