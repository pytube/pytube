# -*- coding: utf-8 -*-
import pytest

from pytube import cipher
from pytube.exceptions import RegexMatchError


def test_map_functions():
    with pytest.raises(RegexMatchError):
        cipher.map_functions('asdf')
