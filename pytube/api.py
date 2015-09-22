#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import logging
import re
import warnings
try:
    from urllib2 import urlopen
    from urlparse import urlparse, parse_qs, unquote
except ImportError:
    from urllib.parse import urlparse, parse_qs, unquote
    from urllib.request import urlopen

from .exceptions import MultipleObjectsReturned, PytubeError, CipherError, \
    DoesNotExist, AgeRestricted
from .jsinterp import JSInterpreter
from .models import Video
from .utils import safe_filename

log = logging.getLogger(__name__)

# YouTube quality and codecs id map.
YT_ENCODING = {
    # flash
    5: ["flv", "240p", "Sorenson H.263", "N/A", "0.25", "MP3", "64"],

    # 3gp
    17: ["3gp", "144p", "MPEG-4 Visual", "Simple", "0.05", "AAC", "24"],
    36: ["3gp", "240p", "MPEG-4 Visual", "Simple", "0.17", "AAC", "38"],

    # webm
    43: ["webm", "360p", "VP8", "N/A", "0.5", "Vorbis", "128"],
    100: ["webm", "360p", "VP8", "3D", "N/A", "Vorbis", "128"],

    # mpeg4
    18: ["mp4", "360p", "H.264", "Baseline", "0.5", "AAC", "96"],
    22: ["mp4", "720p", "H.264", "High", "2-2.9", "AAC", "192"],
    82: ["mp4", "360p", "H.264", "3D", "0.5", "AAC", "96"],
    83: ["mp4", "240p", "H.264", "3D", "0.5", "AAC", "96"],
    84: ["mp4", "720p", "H.264", "3D", "2-2.9", "AAC", "152"],
    85: ["mp4", "1080p", "H.264", "3D", "2-2.9", "AAC", "152"],
}

# The keys corresponding to the quality/codec map above.
YT_ENCODING_KEYS = (
    'extension',
    'resolution',
    'video_codec',
    'profile',
    'video_bitrate',
    'audio_codec',
    'audio_bitrate'
)


class YouTube(object):
    def __init__(self, url=None):
        """Initializes YouTube API wrapper.

        :param str url:
            The url to the YouTube video.
        """
        self._filename = None
        self._video_url = None
        self._js_code = False
        self._videos = []
        if url:
            self.from_url(url)

    @property
    def url(self):
        """Gets the video url."""
        return self._video_url

    @url.setter
    def url(self, url):
        """Sets the url for the video (This method is deprecated. Use
        ``from_url()`` instead).

        :param str url:
            The url to the YouTube video.
        """
        warnings.warn("url setter deprecated, use ``from_url()`` "
                      "instead.", DeprecationWarning)
        self.from_url(url)

    @property
    def video_id(self):
        """Gets the video id by parsing and extracting it from the url."""
        parts = urlparse(self._video_url)
        qs = getattr(parts, 'query')
        if qs:
            video_id = parse_qs(qs).get('v')
            if video_id:
                return video_id.pop()
        return False

    @property
    def filename(self):
        """Gets the filename of the video.  If it hasn't been defined by the
        user, the title will instead be used.
        """
        if not self._filename:
            self._filename = safe_filename(self.title)
            log.debug("generated 'safe' filename: %s", self._filename)
        return self._filename

    @filename.setter
    def filename(self, filename):
        """Sets the filename (This method is deprecated. Use ``set_filename()``
        instead).

        :param str filename:
            The filename of the video.
        """
        warnings.warn("filename setter deprecated. Use ``set_filename()`` "
                      "instead.", DeprecationWarning)
        self.set_filename(filename)

    def set_filename(self, filename):
        """Sets the filename of the video.

        :param str filename:
            The filename of the video.
        """
        # TODO: Check if the filename contains the file extension and either
        # strip it or raise an exception.
        self._filename = filename
        if self.get_videos():
            for video in self.get_videos():
                video.filename = filename
        return True

    def get_videos(self):
        """Gets all videos."""
        return self._videos

    @property
    def videos(self):
        """Gets all videos. (This method is deprecated. Use ``get_videos()``
        instead.
        """
        warnings.warn("videos property deprecated. Use ``get_videos()`` "
                      "instead.", DeprecationWarning)
        return self._videos

    def from_url(self, url):
        """Sets the url for the video.

        :param str url:
            The url to the YouTube video.
        """
        self._video_url = url

        # Reset the filename incase it was previously set.
        self._filename = None

        # Get the video details.
        video_data = self.get_video_data()

        # Set the title.
        self.title = video_data.get("args", {}).get("title")

        # Rewrite and add the url to the javascript, we'll need to fetch this
        # if the YouTube doesn't give us the signature.
        js_url = "http:" + video_data.get("assets", {}).get("js")

        # Just make these easily accessible as variables.
        stream_map = video_data.get("args", {}).get("stream_map")
        video_urls = stream_map.get("url")

        # For each video url, identify the encoding profile and add it to list
        # of available videos.
        for idx, url in enumerate(video_urls):
            try:
                itag, encoding_profile = self._get_encoding_profile(url)
                if not encoding_profile:
                    log.warn("unable to identify profile for itag=%s", itag)
                    continue
            except (TypeError, KeyError) as e:
                log.exception("passing on exception %s", e)
                continue

            # Check if we have the signature, otherwise we'll need to get the
            # cipher from the js.
            if "signature=" not in url:
                log.debug('signature not in url, attempting to resolve the '
                          'cipher...')
                signature = self._get_cipher(stream_map["s"][idx], js_url)
                url = "{}&signature={}".format(url, signature)
            self._add_video(url, self.filename, **encoding_profile)

    def get(self, extension=None, resolution=None, profile=None):
        """Gets a single video given a file extention (and/or resolution
        and/or profile).

        :param str extention:
            The desired file extention (e.g.: mp4).
        :param str resolution:
            The desired video broadcasting standard.
        :param str profile:
            The desired quality profile.
        """
        result = []
        for v in self.get_videos():
            if extension and v.extension != extension:
                continue
            elif resolution and v.resolution != resolution:
                continue
            elif profile and v.profile != profile:
                continue
            else:
                result.append(v)
        matches = len(result)
        if matches <= 0:
            return DoesNotExist("No videos met this criteria.")
        elif matches == 1:
            return result[0]
        else:
            raise MultipleObjectsReturned("Multiple videos met this criteria.")

    def filter(self, extension=None, resolution=None, profile=None):
        """Gets a filtered list of videos given a file extention and/or
        resolution and/or profile.

        :param str extention:
            The desired file extention (e.g.: mp4).
        :param str resolution:
            The desired video broadcasting standard.
        :param str profile:
            The desired quality profile.
        """
        results = []
        for v in self.get_videos():
            if extension and v.extension != extension:
                continue
            elif resolution and v.resolution != resolution:
                continue
            elif profile and v.profile != profile:
                continue
            else:
                results.append(v)
        return results

    def get_video_data(self):
        """Gets the page and extracts out the video data."""
        # Reset the filename incase it was previously set.
        self.title = None
        response = urlopen(self.url)
        if not response:
            raise PytubeError("Unable to open url: %s", self.url)

        html = response.read().decode("utf-8")
        if "og:restrictions:age" in html:
            raise AgeRestricted("Age restricted video. Unable to download "
                                "without being signed in.")

        # Extract out the json data from the html response body.
        json_object = self._get_json_data(html)

        # Here we decode the stream map and bundle it into the json object. We
        # do this just so we just can return one object for the video data.
        encoded_stream_map = json_object.get("args", {}).get(
            "url_encoded_fmt_stream_map")
        json_object['args']['stream_map'] = self._parse_stream_map(
            encoded_stream_map)
        return json_object

    def _parse_stream_map(self, blob):
        """A modified version of ``urlparse.parse_qs`` that's able to decode
        YouTube's stream map.

        :param str blob:
            An encoded blob of text containing the stream map data.
        """
        dct = {
            "itag": [],
            "url": [],
            "quality": [],
            "fallback_host": [],
            "s": [],
            "type": []
        }

        # Split the comma separated videos.
        videos = blob.split(",")

        # Unquote the characters and split to parameters.
        videos = [video.split("&") for video in videos]

        # Split at the equals sign so we can break this key value pairs and
        # toss it into a dictionary.
        for video in videos:
            for kv in video:
                key, value = kv.split("=")
                dct.get(key, []).append(unquote(value))
        log.debug('decoded stream map: %s', dct)
        return dct

    def _get_json_data(self, html):
        """Extract the json out from the html.

        :param str html:
            The raw html of the page.
        """
        # 18 represents the length of "ytplayer.config = ".
        start = html.find("ytplayer.config = ") + 18
        html = html[start:]

        offset = self._get_json_offset(html)
        if not offset:
            raise PytubeError("Unable to extract json.")
        return json.loads(html[:offset])

    def _get_json_offset(self, html):
        """Find where the json object starts.

        :param str html:
            The raw html of the YouTube page.
        """
        brackets = []
        index = 1
        # Determine the offset by pushing/popping brackets until all
        # js expressions are closed.
        for idx, ch in enumerate(html):
            if ch == "{":
                brackets.append("}")
            elif ch == "}":
                brackets.pop()
                if len(brackets) == 0:
                    break
        else:
            raise PytubeError("Unable to determine json offset.")
        return index + idx

    def _get_cipher(self, signature, url):
        """Gets the signature using the cipher.

        :param str signature:
            The url signature.
        :param str url:
            The url of the javascript file.
        """
        reg_exp = re.compile(r'\.sig\|\|([a-zA-Z0-9$]+)\(')
        if not self._js_code:
            response = urlopen(url)
            if not response:
                raise PytubeError("Unable to open url: %s", self.url)
            js = response.read().decode("utf-8")
            self._js_code = (js if not self._js_code else self._js_code)
        try:
            results = reg_exp.search(self._js_code)
            if results:
                # Return the first matching group.
                func = next(g for g in results.groups() if g is not None)

            jsi = JSInterpreter(self._js_code)
            initial_function = jsi.extract_function(func)
            return initial_function([signature])
        except Exception as e:
            raise CipherError("Couldn't cipher the signature. Maybe YouTube "
                              "has changed the cipher algorithm. Notify this "
                              "issue on GitHub: %s" % e)
        return False

    def _get_encoding_profile(self, text):
        """YouTube does not pass you a completely valid URLencoded form, I
        suspect this is supposed to be some sort of a deterrent but nothing
        regex can't handle.

        :param str text:
            The malformed data contained within each url node.
        """
        reg_exp = re.compile('itag=(\d+)')
        itag = reg_exp.findall(text)
        if itag and len(itag) == 1:
            itag = int(itag[0])
            # Given an itag, refer to the YouTube encoding dict to get the
            # properties (media type, resolution, etc) of the video.
            attr = YT_ENCODING.get(itag, None)
            if not attr:
                return itag, None
            return itag, dict(zip(YT_ENCODING_KEYS, attr))
        if not itag:
            raise PytubeError("Unable to get encoding profile, no itag found.")
        elif len(itag) > 1:
            log.warn("Multiple itags found: %s", itag)
            raise PytubeError("Unable to get encoding profile, multiple itags "
                              "found.")
        return False

    def _add_video(self, url, filename, **kwargs):
        """Adds new video object to videos.

        :param str url:
            The signed url to the video.
        :param str filename:
            The filename for the video.
        :param kwargs:
            Additional properties to set for the video object.
        """
        video = Video(url, filename, **kwargs)
        self._videos.append(video)
        self._videos.sort()
        return True
