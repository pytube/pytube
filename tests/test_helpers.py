# -*- coding: utf-8 -*-
import pytest

from pytube import helpers
from pytube.exceptions import RegexMatchError


def test_regex_search_no_match():
    with pytest.raises(RegexMatchError):
        helpers.regex_search('^a$', '', groups=True)


def test_regex_search():
    # TODO(nficano): should check isinstance
    assert helpers.regex_search('^a$', 'a') is not None


def test_safe_filename():
    """Unsafe characters get stripped from generated filename"""
    assert helpers.safe_filename('abc1245$$') == 'abc1245'
    assert helpers.safe_filename('abc##') == 'abc'
