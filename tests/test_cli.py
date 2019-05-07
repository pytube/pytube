# -*- coding: utf-8 -*-
import mock

from pytube import cli


@mock.patch('pytube.cli.YouTube')
@mock.patch('pytube.cli.sys')
def test_download(MockYouTube, mock_sys):
    instance = MockYouTube.return_value
    instance.prefetch_init.return_value = None
    instance.streams = mock.Mock()
    cli.download('asdf', 'asdf', None, None)


def test_terminal_geometry():
    win_os = mock.Mock(return_value='Windows')
    assert cli.get_terminal_size(win_os) == (80, 24)
    assert cli.get_terminal_size('asdf') == (80, 24)
