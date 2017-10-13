# -*- coding: utf-8 -*-
import mock

from pytube import cli


@mock.patch('pytube.cli.YouTube')
@mock.patch('pytube.cli.sys')
def test_download(MockYouTube, mock_sys):
    instance = MockYouTube.return_value
    instance.prefetch_init.return_value = None
    instance.streams = mock.Mock()
    cli.download('asdf', 'asdf')
