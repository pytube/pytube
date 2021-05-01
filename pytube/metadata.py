"""This module contains the YouTubeMetadata class."""
import json
from typing import Dict, List, Optional


class YouTubeMetadata:
    def __init__(self, metadata: List):
        self._raw_metadata: List = metadata
        self._metadata = [{}]

        for el in metadata:
            # We only add metadata to the dict if it has a simpleText title.
            if 'title' in el and 'simpleText' in el['title']:
                metadata_title = el['title']['simpleText']
            else:
                continue

            contents = el['contents'][0]
            if 'simpleText' in contents:
                self._metadata[-1][metadata_title] = contents['simpleText']
            elif 'runs' in contents:
                self._metadata[-1][metadata_title] = contents['runs'][0]['text']

            # Upon reaching a dividing line, create a new grouping
            if el.get('hasDividerLine', False):
                self._metadata.append({})

        # If we happen to create an empty dict at the end, drop it
        if self._metadata[-1] == {}:
            self._metadata = self._metadata[:-1]

    def __getitem__(self, key):
        return self._metadata[key]

    def __iter__(self):
        for el in self._metadata:
            yield el

    def __str__(self):
        return json.dumps(self._metadata)

    @property
    def raw_metadata(self) -> Optional[Dict]:
        return self._raw_metadata

    @property
    def metadata(self):
        return self._metadata
