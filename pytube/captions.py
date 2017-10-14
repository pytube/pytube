# -*- coding: utf-8 -*-
"""This module contrains a container for caption tracks."""
import math
import time
import xml.etree.ElementTree as ElementTree

from pytube import request
from pytube.compat import unescape


class Caption:
    """Container for caption tracks."""

    def __init__(self, caption_track):
        """Construct a :class:`Caption <Caption>`.

        :param dict caption_track:
            Caption track data extracted from ``watch_html``.
        """
        self.url = caption_track.get('baseUrl')
        self.name = caption_track['name']['simpleText']
        self.code = caption_track['languageCode']

    @property
    def xml_captions(self):
        """Download the xml caption tracks."""
        return request.get(self.url)

    def generate_srt_captions(self):
        """Generate "SubRip Subtitle" captions.

        Takes the xml captions from :meth:`~pytube.Caption.xml_captions` and
        recompiles them into the "SubRip Subtitle" format.
        """
        return self.xml_caption_to_srt(self.xml_captions)

    def float_to_srt_time_format(self, d):
        """Convert decimal durations into proper srt format.

        :rtype: str
        :returns:
            SubRip Subtitle (str) formatted time duration.

        >>> float_to_srt_time_format(3.89)
        '00:00:03,890'
        """
        frac, whole = math.modf(d)
        time_fmt = time.strftime('0%H:0%M:%S,', time.gmtime(whole))
        ms = '{:.3f}'.format(frac).replace('0.', '')
        return time_fmt + ms

    def xml_caption_to_srt(self, xml_captions):
        """Convert xml caption tracks to "SubRip Subtitle (srt)".

        :param str xml_captions:
            XML formatted caption tracks.
        """
        segments = []
        root = ElementTree.fromstring(xml_captions)
        for i, child in enumerate(root.getchildren()):
            text = child.text or ''
            caption = unescape(
                text
                .replace('\n', ' ')
                .replace('  ', ' '),
            )
            duration = float(child.attrib['dur'])
            start = float(child.attrib['start'])
            end = start + duration
            sequence_number = i + 1  # convert from 0-indexed to 1.
            line = (
                '{seq}\n{start} --> {end}\n{text}\n'.format(
                    seq=sequence_number,
                    start=self.float_to_srt_time_format(start),
                    end=self.float_to_srt_time_format(end),
                    text=caption,
                )
            )
            segments.append(line)
        return '\n'.join(segments).strip()

    def __repr__(self):
        """Printable object representation."""
        return'<Caption lang="{s.name}" code="{s.code}">'.format(s=self)
