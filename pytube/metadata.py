# -*- coding: utf-8 -*-
"""This module contains the YouTubeMetadata class."""
from typing import Dict
from typing import List
from typing import Optional


class YouTubeMetadata:
    def __init__(self, metadata: List):
        self._metadata: List = metadata
        self._dict_repr = {}
        for el in metadata:
            # We only add metadata to the dict if it has a simpleText title.
            if 'title' in el and 'simpleText' in el['title']:
                metadata_title = el['title']['simpleText']
            else:
                continue

            metadata_contents = el['contents'][0]
            if 'simpleText' in metadata_contents:
                self._dict_repr[metadata_title] = metadata_contents['simpleText']
            elif 'runs' in metadata_contents:
                self._dict_repr[metadata_title] = metadata_contents['runs'][0]['text']

    def __iter__(self):
        for key in self._dict_repr:
            yield (key, self._dict_repr[key])

    def __getitem__(self, key):
        return self._dict_repr[key]

    def __setitem__(self, key, value):
        self._dict_repr[key] = value

    def __delitem__(self, key):
        del self._dict_repr[key]

    def __contains__(self, key):
        return key in self._dict_repr

    def __len__(self):
        return len(self._dict_repr)

    @property
    def metadata(self) -> Optional[Dict]:
        return self._metadata
