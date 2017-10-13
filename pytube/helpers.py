# -*- coding: utf-8 -*-
"""Various helper functions implemented by pytube."""
from __future__ import absolute_import

import logging
import math
import pprint
import re
import time
import xml.etree.ElementTree as ElementTree

from pytube.compat import unescape
from pytube.compat import unicode
from pytube.exceptions import RegexMatchError


logger = logging.getLogger(__name__)


def regex_search(pattern, string, groups=False, group=None, flags=0):
    """Shortcut method to search a string for a given pattern.

    :param str pattern:
        A regular expression pattern.
    :param str string:
        A target string to search.
    :param bool groups:
        Should the return value be ``.groups()``.
    :param int group:
        Index of group to return.
    """
    regex = re.compile(pattern, flags)
    results = regex.search(string)
    if not results:
        raise RegexMatchError(
            'regex pattern ({pattern}) had zero matches'
            .format(pattern=pattern),
        )
    else:
        logger.debug(
            'finished regex search: %s',
            pprint.pformat(
                {
                    'pattern': pattern,
                    'results': results.group(0),
                }, indent=2,
            ),
        )
        if groups:
            return results.groups()
        elif group is not None:
            return results.group(group)
        else:
            return results


def apply_mixin(dct, key, func, *args, **kwargs):
    r"""Apply in-place data mutation to a dictionary.

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
    """Sanitize a string making it safe to use as a filename.

    This function was based off the limitations outlined here:
    https://en.wikipedia.org/wiki/Filename.

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
    return unicode(filename[:max_length].rsplit(' ', 0)[0])


def float_to_srt_time_format(d):
    """Convert decimal durations into proper srt format.

    :rtype: str
    :returns:
        SubRip Subtitle (str) formatted time duration.

    >>> float_to_srt_time_format(3.89)
    '00:00:03,890'
    """
    frac, whole = math.modf(d)
    time_fmt = time.strftime('0%H:0%M:%S,', time.gmtime(whole))
    ms = '{:.3f}'.format(frac).replace('0.', '')
    return time_fmt + ms


def xml_caption_to_srt(xml_captions):
    """Convert xml caption tracks to "SubRip Subtitle (srt)".

    :param str xml_captions:
        XML formatted caption tracks.
    """
    segments = []
    root = ElementTree.fromstring(xml_captions)
    for i, child in enumerate(root.getchildren()):
        text = child.text or ''
        caption = unescape(
            text
            .replace('\n', ' ')
            .replace('  ', ' '),
        )
        duration = float(child.attrib['dur'])
        start = float(child.attrib['start'])
        end = start + duration
        sequence_number = i + 1  # convert from 0-indexed to 1.
        line = (
            '{seq}\n{start} --> {end}\n{text}\n'.format(
                seq=sequence_number,
                start=float_to_srt_time_format(start),
                end=float_to_srt_time_format(end),
                text=caption,
            )
        )
        segments.append(line)
    return '\n'.join(segments).strip()
