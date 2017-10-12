# -*- coding: utf-8 -*-
def test_pre_signed_video(presigned_video):
    assert presigned_video.streams.count() == 15
