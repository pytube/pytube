# -*- coding: utf-8 -*-
import gzip
import io
import json
import os
from unittest import mock

import pytest

from pytube import helpers
from pytube.exceptions import RegexMatchError
from pytube.helpers import cache
from pytube.helpers import deprecated
from pytube.helpers import setup_logger
from pytube.helpers import target_directory
from pytube.helpers import create_mock_video_gz


def test_regex_search_no_match():
    with pytest.raises(RegexMatchError):
        helpers.regex_search("^a$", "", group=0)


def test_regex_search():
    assert helpers.regex_search("^a$", "a", group=0) == "a"


def test_safe_filename():
    """Unsafe characters get stripped from generated filename"""
    assert helpers.safe_filename("abc1245$$") == "abc1245"
    assert helpers.safe_filename("abc##") == "abc"


@mock.patch("warnings.warn")
def test_deprecated(warn):
    @deprecated("oh no")
    def deprecated_function():
        return None

    deprecated_function()
    warn.assert_called_with(
        "Call to deprecated function deprecated_function (oh no).",
        category=DeprecationWarning,
        stacklevel=2,
    )


def test_cache():
    call_count = 0

    @cache
    def cached_func(stuff):
        nonlocal call_count
        call_count += 1
        return stuff

    cached_func("hi")
    cached_func("hi")
    cached_func("bye")
    cached_func("bye")

    assert call_count == 2


@mock.patch("os.path.isabs", return_value=False)
@mock.patch("os.getcwd", return_value="/cwd")
@mock.patch("os.makedirs")
def test_target_directory_with_relative_path(_, __, makedirs):  # noqa: PT019
    assert target_directory("test") == os.path.join("/cwd", "test")
    makedirs.assert_called()


@mock.patch("os.path.isabs", return_value=True)
@mock.patch("os.makedirs")
def test_target_directory_with_absolute_path(_, makedirs):  # noqa: PT019
    assert target_directory("/test") == "/test"
    makedirs.assert_called()


@mock.patch("os.getcwd", return_value="/cwd")
@mock.patch("os.makedirs")
def test_target_directory_with_no_path(_, makedirs):  # noqa: PT019
    assert target_directory() == "/cwd"
    makedirs.assert_called()


@mock.patch("pytube.helpers.logging")
def test_setup_logger(logging):
    # Given
    logger = logging.getLogger.return_value
    # When
    setup_logger(20)
    # Then
    logging.getLogger.assert_called_with("pytube")
    logger.addHandler.assert_called()
    logger.setLevel.assert_called_with(20)


@mock.patch('builtins.open', new_callable=mock.mock_open)
def test_create_mock_video_gz(mock_open):
    video_id = '9bZkp7q19f0'
    gzip_filename = 'yt-video-%s.json.gz' % video_id

    # Generate the mock video.json.gz file from a video id
    result_data = create_mock_video_gz(video_id)

    # Assert that a write was only made once
    mock_open.assert_called_once_with(gzip_filename, 'wb')

    # The result data should look like this:
    gzip_file = io.BytesIO()
    with gzip.GzipFile(filename=gzip_filename, fileobj=gzip_file, mode='wb') as f:
        f.write(json.dumps(result_data).encode('utf-8'))
    gzip_data = gzip_file.getvalue()

    file_handle = mock_open.return_value.__enter__.return_value

    # For some reason, write gets called multiple times, so we have to
    #  concatenate all the write calls to get the full data before we compare
    #  it to the BytesIO object value.
    full_content = b''
    for call in file_handle.write.call_args_list:
        args, kwargs = call
        for arg in args:
            full_content += arg

    assert gzip_data == full_content
