import gzip
import io
import json
import os
import pytest
from unittest import mock

from pytube import helpers
from pytube.exceptions import RegexMatchError
from pytube.helpers import cache, create_mock_html_json, deprecated, setup_logger
from pytube.helpers import target_directory, uniqueify


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
@mock.patch('pytube.request.urlopen')
def test_create_mock_html_json(mock_url_open, mock_open):
    video_id = '2lAe1cqCOXo'
    gzip_html_filename = 'yt-video-%s-html.json.gz' % video_id

    # Get the pytube directory in order to navigate to /tests/mocks
    pytube_dir_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            os.path.pardir
        )
    )
    pytube_mocks_path = os.path.join(pytube_dir_path, 'tests', 'mocks')
    gzip_html_filepath = os.path.join(pytube_mocks_path, gzip_html_filename)

    # Mock the responses to YouTube
    mock_url_open_object = mock.Mock()

    # Order is:
    # 1. watch_html -- must have jsurl match
    # 2. embed html
    # 3. watch html
    # 4. raw vid info
    mock_url_open_object.read.side_effect = [
        (b'yt.setConfig({"PLAYER_CONFIG":{"args":[]}});ytInitialData = {};ytInitialPlayerResponse = {};'  # noqa: E501
         b'"jsUrl":"/s/player/13371337/player_ias.vflset/en_US/base.js"'),
        b'embed_html',
        b'watch_html',
        b'{\"responseContext\":{}}',
    ]
    mock_url_open.return_value = mock_url_open_object

    # Generate a json with sample html json
    result_data = create_mock_html_json(video_id)

    # Assert that a write was only made once
    mock_open.assert_called_once_with(gzip_html_filepath, 'wb')

    # The result data should look like this:
    gzip_file = io.BytesIO()
    with gzip.GzipFile(
        filename=gzip_html_filename,
        fileobj=gzip_file,
        mode='wb'
    ) as f:
        f.write(json.dumps(result_data).encode('utf-8'))
    gzip_data = gzip_file.getvalue()

    file_handle = mock_open.return_value.__enter__.return_value

    # For some reason, write gets called multiple times, so we have to
    #  concatenate all the write calls to get the full data before we compare
    #  it to the BytesIO object value.
    full_content = b''
    for call in file_handle.write.call_args_list:
        args, kwargs = call
        full_content += b''.join(args)

    # The file header includes time metadata, so *occasionally* a single
    #  byte will be off at the very beginning. In theory, this difference
    #  should only affect bytes 5-8 (or [4:8] because of zero-indexing),
    #  but I've excluded the 10-byte metadata header altogether from the
    #  check, just to be safe.
    # Source: https://en.wikipedia.org/wiki/Gzip#File_format
    assert gzip_data[10:] == full_content[10:]


def test_uniqueify():
    non_unique_list = [1, 2, 3, 3, 4, 5]
    expected = [1, 2, 3, 4, 5]
    result = uniqueify(non_unique_list)
    assert result == expected
