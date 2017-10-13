# -*- coding: utf-8 -*-
class Caption:
    def __init__(self, caption_track):
        self.url = caption_track.get('baseUrl')
        self.name = caption_track['name']['simpleText']
        self.code = caption_track['languageCode']

    def __repr__(self):
        return'<Caption lang="{s.name}" code="{s.code}">'.format(s=self)
