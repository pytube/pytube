# -*- coding: utf-8 -*-
from unittest import mock

from pytube import cli


@mock.patch("pytube.cli.YouTube")
def test_download(youtube):
    instance = youtube.return_value
    instance.prefetch_descramble.return_value = None
    instance.streams = mock.Mock()
    cli.download(instance, 123)
