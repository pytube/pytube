# -*- coding: utf-8 -*-
import pytest

from pytube import cipher
from pytube.exceptions import RegexMatchError


def test_map_functions():
    with pytest.raises(RegexMatchError):
        cipher.map_functions("asdf")


def test_get_initial_function_name_with_no_match_should_error():
    with pytest.raises(RegexMatchError):
        cipher.get_initial_function_name("asdf")


def test_get_transform_object_with_no_match_should_error():
    with pytest.raises(RegexMatchError):
        cipher.get_transform_object("asdf", var="lt")


def test_parse_function_with_match():
    fn_name, fn_arg = cipher.parse_function("DE.AJ(a,15)")
    assert fn_name == "AJ"
    assert fn_arg == 15


def test_parse_function_with_no_match_should_error():
    with pytest.raises(RegexMatchError):
        cipher.parse_function("asdf")


def test_reverse():
    reversed_array = cipher.reverse([1, 2, 3, 4], None)
    assert reversed_array == [4, 3, 2, 1]
