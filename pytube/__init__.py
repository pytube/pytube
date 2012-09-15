from os.path import normpath
from urllib import urlencode
from urllib2 import urlopen
from urlparse import urlparse, parse_qs

import re

YT_BASE_URL = 'http://www.youtube.com/get_video_info'

# YouTube media encoding options.
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

YT_ENCODING_KEYS = (
    'extension', 'resolution', 'video_codec', 'profile', 'video_bitrate',
    'audio_codec', 'audio_bitrate'
)


class MultipleObjectsReturned(Exception):
    pass

class YouTubeError(Exception):
    pass

class Video(object):
    """
    Class representation of a single instance of a YouTube video.
    """
    def __init__(self, url, filename, **attributes):
        """
        Define the variables required to declare a new video.

        Keyword arguments:
        extention -- The file extention the video should be saved as.
        resolution -- The broadcasting standard of the video.
        url -- The url of the video. (e.g.: youtube.com/watch?v=..)
        filename -- The filename (minus the extention) to save the video.
        """

        self.url = url
        self.filename = filename
        self.__dict__.update(**attributes)

    def download(self, path=None):
        """
        Downloads the file of the URL defined within the class
        instance.

        Keyword arguments:
        path -- Destination directory
        """

        path = (normpath(path) + '/' if path else '')
        response = urlopen(self.url)
        with open(path + self.filename, 'wb') as dst_file:
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

    def __repr__(self):
        """A cleaner representation of the class instance."""
        return "<Video: %s (.%s) - %s>" % (self.video_codec, self.extension,
            self.resolution)

    def __cmp__(self, other):
        if type(other) == Video:
            v1 = "%s %s" % (self.extension, self.resolution)
            v2 = "%s %s" % (other.extension, other.resolution)
            return cmp(v1, v2)


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

    @property
    def video_id(self):
        """Gets the video ID extracted from the URL."""
        parts = urlparse(self._video_url)
        qs = getattr(parts, 'query', None)
        if qs:
            video_id = parse_qs(qs).get('v', None)
            if video_id:
                return video_id.pop()

    def get(self, extension=None, res=None):
        """
        Return a single video given an extention and resolution.

        Keyword arguments:
        extention -- The desired file extention (e.g.: mp4).
        res -- The desired broadcasting standard of the video (e.g.: 1080p).
        """
        result = []
        for v in self.videos:
            if extension and v.extension != extension:
                continue
            elif res and v.resolution != res:
                continue
            else:
                result.append(v)
        if not len(result):
            return
        elif len(result) is 1:
            return result[0]
        else:
            raise MultipleObjectsReturned("get() returned more than one " \
                "object -- it returned %d!" % len(result))

    def filter(self, extension=None, res=None):
        """
        Return a filtered list of videos given an extention and
        resolution criteria.

        Keyword arguments:
        extention -- The desired file extention (e.g.: mp4).
        res -- The desired broadcasting standard of the video (e.g.: 1080p).
        """
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
        """
        Given a path, traverse the response for the desired data. (A
        modified ver. of my dictionary traverse method:
        https://gist.github.com/2009119)

        Keyword arguments:
        path -- A tuple representing a path to a node within a tree.
        data -- The data containing the tree.
        """
        elem = path[0]
        #Get first element in tulip, and check if it contains a list.
        if type(data) is list:
            # Pop it, and let's continue..
            return self._fetch(path, data.pop())
        #Parse the url encoded data
        data = parse_qs(data)
        #Get the element in our path
        data = data.get(elem, None)
        #Offset the tulip by 1.
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

    def _get_video_info(self):
        """
        This is responsable for executing the request, extracting the
        necessary details, and populating the different video
        resolutions and formats into a list.
        """
        querystring = urlencode({
                'asv': 3,
                'el': 'detailpage',
                'hl': 'en_US',
                'video_id': self.video_id
        })

        self.title = None
        self.videos = []

        response = urlopen(YT_BASE_URL + '?' + querystring)

        if response:
            content = response.read()
            data = parse_qs(content)
            if 'errorcode' in data:
                error = data.get('reason', 'An unknown error has occurred')
                if isinstance(error, list):
                    error = error.pop()
                raise YouTubeError(error)

            #Use my cool traversing method to extract the specific
            #attribute from the response body.
            path = ('url_encoded_fmt_stream_map', 'itag')
            #Using the ``itag`` (otherwised referred to as ``fmf``, set the
            #available encoding options.
            encoding_options = self._fetch(path, content)
            self.title = self._fetch(('title',), content)

            for video in encoding_options:
                url = self._extract_url(video)
                if not url:
                    #Sometimes the regex for matching the video returns
                    #a single empty element, so we'll skip those here.
                    continue
                try:
                    fmt, data = self._extract_fmt(video)
                    filename = "%s.%s" % (self.filename, data['extension'])
                except TypeError, KeyError:
                    pass
                else:
                    v = Video(url, filename, **data)
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

    def _extract_url(self, text):
        """
        (I hate to be redundant here, but whatever) YouTube does not
        pass you a completely valid URLencoded form, I suspect this is
        suppose to act as a deterrent.. Nothing some regulular
        expressions couldn't handle.

        Keyword arguments:
        text -- The malformed data contained in the itag node.
        """
        url = re.findall('url=(.*)', text)
        if url and len(url) is 1:
            return url[0]


def safe_filename(text, max_length=200):
    """
    Sanitizes filenames for many operating systems.

    Keyword arguments:
    text -- The unsanitized pending filename.
    """
    #Quickly truncates long filenames.
    truncate = lambda text: text[:max_length].rsplit(' ', 0)[0]

    #Tidy up ugly formatted filenames.
    text = text.replace('_', ' ')
    text = text.replace(':', ' -')

    #NTFS forbids filenames containing characters in range 0-31 (0x00-0x1F)
    ntfs = [chr(i) for i in range(0, 31)]

    #Removing these SHOULD make most filename safe for a wide range
    #of operating systems.
    paranoid = ['\"', '\#', '\$', '\%', '\'', '\*', '\,', '\.', '\/', '\:',
        '\;', '\<', '\>', '\?', '\\', '\^', '\|', '\~', '\\\\']

    blacklist = re.compile('|'.join(ntfs + paranoid), re.UNICODE)
    filename = blacklist.sub('', text)
    return truncate(filename)
