import json
import pytest

from pytube.exceptions import HTMLParseError
from pytube.parser import parse_for_object


def test_invalid_start():
    with pytest.raises(HTMLParseError):
        parse_for_object('test = {}', r'invalid_regex')


def test_parse_simple_empty_object():
    result = parse_for_object('test = {}', r'test\s*=\s*')
    assert result == {}


def test_parse_longer_empty_object():
    test_html = """test = {


    }"""
    result = parse_for_object(test_html, r'test\s*=\s*')
    assert result == {}


def test_parse_empty_object_with_trailing_characters():
    test_html = 'test = {};'
    result = parse_for_object(test_html, r'test\s*=\s*')
    assert result == {}


def test_parse_simple_object():
    test_html = 'test = {"foo": [], "bar": {}};'
    result = parse_for_object(test_html, r'test\s*=\s*')
    assert result == {
        'foo': [],
        'bar': {}
    }


def test_parse_context_closer_in_string_value():
    test_html = 'test = {"foo": "};"};'
    result = parse_for_object(test_html, r'test\s*=\s*')
    assert result == {
        'foo': '};'
    }


def test_parse_object_requiring_ast():
    invalid_json = '{"foo": "bar",}'
    test_html = f'test = {invalid_json}'
    with pytest.raises(json.decoder.JSONDecodeError):
        json.loads(invalid_json)
    result = parse_for_object(test_html, r'test\s*=\s*')
    assert result == {
        'foo': 'bar'
    }
