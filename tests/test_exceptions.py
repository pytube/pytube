# -*- coding: utf-8 -*-
from pytube.exceptions import ExtractError


def test_is_expected():
    try:
        raise ExtractError('ppfff', video_id='YLnZklYFe7E')
    except ExtractError as e:
        assert e.video_id == 'YLnZklYFe7E'
