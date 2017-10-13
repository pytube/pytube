# -*- coding: utf-8 -*-
"""This module contrains a container for caption tracks."""
from pytube import request
from pytube.helpers import xml_caption_to_srt


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
        return xml_caption_to_srt(self.xml_captions)

    def __repr__(self):
        """Printable object representation."""
        return'<Caption lang="{s.name}" code="{s.code}">'.format(s=self)
