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

from .exceptions import MultipleObjectsReturned, YouTubeError, CipherError, \
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
        self._filename = None
        self._fmt_values = []
        self._video_url = None
        self._js_code = False
        self._videos = []
        if url:
            self.from_url(url)

    @property
    def url(self):
        """Get the video url."""
        return self._video_url

    @url.setter
    def url(self, url):
        """Set the YouTube video url (This method is deprecated. Use
        `from_url()` instead).

        :param str url:
            The YouTube video url.
        """
        warnings.warn("url setter deprecated, use `from_url()` "
                      "instead.", DeprecationWarning)
        self.from_url(url)

    def from_url(self, url):
        """Set the YouTube video url.

        :param str url:
            The YouTube video url.
        """
        self._video_url = url

        # Reset the filename.
        self._filename = None

        # Get the video details.
        video_data = self.get_video_data()

        # Set the title.
        self.title = video_data.get("args", {}).get("title")

        js_url = "http:" + video_data.get("assets", {}).get("js")
        stream_map = video_data.get("args", {}).get("stream_map")
        video_urls = stream_map.get("url")

        for i, url in enumerate(video_urls):
            try:
                fmt, fmt_data = self._extract_fmt(url)
                if not fmt_data:
                    log.warn("unable to identify itag=%s", fmt)
                    continue
            except (TypeError, KeyError) as e:
                log.exception("passing on exception %s", e)
                continue

            # If the signature must be ciphered...
            if "signature=" not in url:
                signature = self._get_cipher(stream_map["s"][i], js_url)
                url = "{}&signature={}".format(url, signature)
            self._add_video(url, self.filename, **fmt_data)
            self._fmt_values.append(fmt)

    @property
    def filename(self):
        """Get the title of the video."""
        if not self._filename:
            self._filename = safe_filename(self.title)
            log.debug("generated 'safe' filename: %s", self._filename)
        return self._filename

    @filename.setter
    def filename(self, filename):
        """Set the filename (This method is deprecated. Use `set_filename()`
        instead).

        :param str filename:
            The filename of the video.
        """
        warnings.warn("filename setter deprecated, use `set_filename()` "
                      "instead.", DeprecationWarning)
        self.set_filename(filename)

    def set_filename(self, filename):
        """Set the filename.

        :param str filename:
            The filename of the video.
        """
        self._filename = filename
        if self.get_videos():
            for video in self.get_videos():
                video.filename = filename

    @property
    def video_id(self):
        """Extracts the video id from the url."""
        parts = urlparse(self._video_url)
        qs = getattr(parts, 'query')
        if qs:
            video_id = parse_qs(qs).get('v')
            if video_id:
                return video_id.pop()
        return False

    def get_videos(self):
        """Returns all videos.
        """
        return self._videos

    @property
    def videos(self):
        """Returns all videos
        """
        warnings.warn("videos property deprecated, use `get_videos()` "
                      "instead.", DeprecationWarning)
        return self._videos

    def get(self, extension=None, resolution=None, profile=None):
        """Return a single video given a file extention and/or resolution
        and/or profile.

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
            return DoesNotExist("No videos met criteria.")
        elif matches == 1:
            return result[0]
        else:
            raise MultipleObjectsReturned(
                "{} videos met criteria".format(matches))

    def filter(self, extension=None, resolution=None, profile=None):
        """Return a filtered list of videos given a file extention and/or
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
        """Fetch the page and extract out the video data."""
        self.title = None

        response = urlopen(self.url)

        if not response:
            return False
        html = response.read().decode("utf-8")

        if "og:restrictions:age" in html:
            raise AgeRestricted

        json_object = self._extract_json_data(html)

        if not json_object:
            raise YouTubeError("Unable to extract json.")

        encoded_stream_map = json_object.get("args", {}).get(
            "url_encoded_fmt_stream_map")

        json_object['args']['stream_map'] = self._parse_stream_map(
            encoded_stream_map)
        return json_object

    def _parse_stream_map(self, blob):
        """A modified version of `urlparse.parse_qs` that is able to decode
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

        # Split individual videos
        videos = blob.split(",")
        # Unquote the characters and split to parameters
        videos = [video.split("&") for video in videos]

        for video in videos:
            for kv in video:
                key, value = kv.split("=")
                log.debug('stream map key value: %s => %s', key, value)
                dct.get(key, []).append(unquote(value))
        log.debug('decoded stream map: %s', dct)
        return dct

    def _extract_json_data(self, html):
        """Extract the json from the html.

        :param str html:
            The raw html of the YouTube page.
        """
        # 18 represents the length of "ytplayer.config = ".
        start = html.find("ytplayer.config = ") + 18
        html = html[start:]
        offset = self._find_json_offset(html)

        if not offset:
            return None
        return json.loads(html[:offset])

    def _find_json_offset(self, html):
        """Find where the json object starts.

        :param str html:
            The raw html of the YouTube page.
        """
        brackets = []
        index = 1
        for i, char in enumerate(html):
            if char == "{":
                brackets.append("}")
            elif char == "}":
                brackets.pop()
                if len(brackets) == 0:
                    break
        else:
            return None
        return index + i

    def _get_cipher(self, signature, url):
        """Get the signature using the cipher.

        :param str signature:
            Signature.
        :param str url:
            url of JavaScript file.
        """
        reg_exp = re.compile(r'\.sig\|\|([a-zA-Z0-9$]+)\(')
        if not self._js_code:
            js = urlopen(url).read().decode()
            self._js_code = (js if not self._js_code else self._js_code)
        try:
            results = reg_exp.search(self._js_code)
            if results:
                # return the first matching group
                func = next(g for g in results.groups() if g is not None)

            jsi = JSInterpreter(self._js_code)
            initial_function = jsi.extract_function(func)
            return initial_function([signature])
        except Exception as e:
            raise CipherError("Couldn't cipher the signature. Maybe YouTube "
                              "has changed the cipher algorithm. Notify this "
                              "issue on GitHub: %s" % e)

    def _extract_fmt(self, text):
        """YouTube does not pass you a completely valid URLencoded form, I
        suspect this is suppose to act as a deterrent... Nothing some regex
        couldn't handle.

        :param str text:
            The malformed data contained within each url node.
        """
        reg_exp = re.compile('itag=(\d+)')
        itag = reg_exp.findall(text)
        if itag and len(itag) == 1:
            itag = int(itag[0])
            attr = YT_ENCODING.get(itag, None)
            if not attr:
                return itag, None
            return itag, dict(zip(YT_ENCODING_KEYS, attr))

    def _add_video(self, url, filename, **kwargs):
        """Adds new video object to videos.
        """
        video = Video(url, filename, **kwargs)
        self._videos.append(video)
        self._videos.sort()
        return True
