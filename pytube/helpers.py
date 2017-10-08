# -*- coding: utf-8 -*-
"""
pytube.helpers
~~~~~~~~~~~~~~

Various helper functions implemented by pytube.

"""
import functools
import re


def apply_mixin(dct, key, func, *args, **kwargs):
    """Applies an inplace data mutation to a dictionary.

    :param dict dct:
        Dictionary to apply mixin function to.
    :param str key:
        Key within dictionary to apply mixin function to.
    :param callable func:
        Transform function to apply to dct[key].
    :param \*args:
        (optional) positional arguments that ``func`` takes.
    :param \*\*kwargs:
        (optional) keyword arguments that ``func`` takes.
    """
    dct[key] = func(dct[key], *args, **kwargs)


def safe_filename(s, max_length=255):
    """Attempts to sanitize an arbitrary string making it safe to use as a
    filename (see: https://en.wikipedia.org/wiki/Filename).

    :param str text:
        A string to make safe for use as a file name.
    :param int max_length:
        The maximum filename character length.
    """

    # Characters in range 0-31 (0x00-0x1F) are not allowed in NTFS filenames.
    ntfs_chrs = [chr(i) for i in range(0, 31)]
    chrs = [
        '\"', '\#', '\$', '\%', '\'', '\*', '\,', '\.', '\/', '\:',
        '\;', '\<', '\>', '\?', '\\', '\^', '\|', '\~', '\\\\',
    ]
    pattern = '|'.join(ntfs_chrs + chrs)
    regex = re.compile(pattern, re.UNICODE)
    filename = regex.sub('', s)
    return filename[:max_length].rsplit(' ', 0)[0]


def memoize(func):
    """A function decorator that caches input arguments for return values, to
    avoid recomputation on repeat calls.
    """
    cache = func.cache = {}

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    return wrapper
