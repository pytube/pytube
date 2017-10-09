# -*- coding: utf-8 -*-
def test_pre_signed_video(youtube_captions_and_subtitles):
    assert youtube_captions_and_subtitles.streams.count() == 15
