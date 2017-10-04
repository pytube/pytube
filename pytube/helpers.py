# -*- coding: utf-8 -*-
"""
pytube.helpers
~~~~~~~~~~~~~~

Various helper functions implemented by pytube.

"""
import functools
import re


def truncate(text, max_length=200):
    return text[:max_length].rsplit(' ', 0)[0]


def safe_filename(text, max_length=200):
    """Sanitizes filenames for many operating systems."""
    output_text = text

    output_text = (
        text
        .replace('_', ' ')
        .replace(':', ' -')
    )

    # NTFS forbids filenames containing characters in range 0-31 (0x00-0x1F)
    ntfs_illegal_chars = [chr(i) for i in range(0, 31)]

    # Removing these SHOULD make most filename safe for a wide range of
    # operating systems.
    misc_illegal_chars = [
        '\"', '\#', '\$', '\%', '\'', '\*', '\,', '\.', '\/', '\:',
        '\;', '\<', '\>', '\?', '\\', '\^', '\|', '\~', '\\\\',
    ]
    pattern = '|'.join(ntfs_illegal_chars + misc_illegal_chars)
    forbidden_chars = re.compile(pattern, re.UNICODE)
    filename = forbidden_chars.sub('', output_text)
    return truncate(filename)


def memoize(func):
    cache = func.cache = {}

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    return wrapper
