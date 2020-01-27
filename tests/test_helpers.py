# -*- coding: utf-8 -*-
from unittest import mock

import pytest

from pytube import helpers
from pytube.exceptions import RegexMatchError
from pytube.helpers import deprecated, cache


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
