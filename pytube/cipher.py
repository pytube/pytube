# -*- coding: utf-8 -*-
"""
This module countains all logic necessary to decipher the signature.

YouTube's strategy to restrict downloading videos is to send a ciphered version
of the signature to the client, along with the decryption algorithm obfuscated
in JavaScript. For the clients to play the videos, JavaScript must take the
ciphered version, cycle it through a series of "transform functions," and then
signs the media URL with the output.

This module is responsible for (1) finding and extracting those "transform
functions" (2) maps them to Python equivalents and (3) taking the ciphered
signature and decoding it.

"""
from __future__ import absolute_import

import logging
import pprint
import re
from itertools import chain

from pytube.exceptions import RegexMatchError
from pytube.helpers import regex_search


logger = logging.getLogger(__name__)


def get_initial_function_name(js):
    """Extract the name of the function responsible for computing the signature.

    :param str js:
        The contents of the base.js asset file.

    """
    # c&&d.set("signature", EE(c));
    pattern = [
        r'yt\.akamaized\.net/\)\s*\|\|\s*'
        r'.*?\s*c\s*&&\s*d\.set\([^,]+\s*,\s*(?:encodeURIComponent'
        r'\s*\()?(?P<sig>[a-zA-Z0-9$]+)\(',
        r'\.sig\|\|(?P<sig>[a-zA-Z0-9$]+)\(',
        r'\bc\s*&&\s*d\.set\([^,]+\s*,\s*(?:encodeURIComponent'
        r'\s*\()?(?P<sig>[a-zA-Z0-9$]+)\(',
    ]
    logger.debug('finding initial function name')
    return regex_search(pattern, js, group=1)


def get_transform_plan(js):
    """Extract the "transform plan".

    The "transform plan" is the functions that the ciphered signature is
    cycled through to obtain the actual signature.

    :param str js:
        The contents of the base.js asset file.

    **Example**:

    >>> get_transform_plan(js)
    ['DE.AJ(a,15)',
    'DE.VR(a,3)',
    'DE.AJ(a,51)',
    'DE.VR(a,3)',
    'DE.kT(a,51)',
    'DE.kT(a,8)',
    'DE.VR(a,3)',
    'DE.kT(a,21)']
    """
    name = re.escape(get_initial_function_name(js))
    pattern = r'%s=function\(\w\){[a-z=\.\(\"\)]*;(.*);(?:.+)}' % name
    logger.debug('getting transform plan')
    return regex_search(pattern, js, group=1).split(';')


def get_transform_object(js, var):
    """Extract the "transform object".

    The "transform object" contains the function definitions referenced in the
    "transform plan". The ``var`` argument is the obfuscated variable name
    which contains these functions, for example, given the function call
    ``DE.AJ(a,15)`` returned by the transform plan, "DE" would be the var.

    :param str js:
        The contents of the base.js asset file.
    :param str var:
        The obfuscated variable name that stores an object with all functions
        that descrambles the signature.

    **Example**:

    >>> get_transform_object(js, 'DE')
    ['AJ:function(a){a.reverse()}',
    'VR:function(a,b){a.splice(0,b)}',
    'kT:function(a,b){var c=a[0];a[0]=a[b%a.length];a[b]=c}']

    """
    pattern = r'var %s={(.*?)};' % re.escape(var)
    logger.debug('getting transform object')
    return (
        regex_search(pattern, js, group=1, flags=re.DOTALL)
        .replace('\n', ' ')
        .split(', ')
    )


def get_transform_map(js, var):
    """Build a transform function lookup.

    Build a lookup table of obfuscated JavaScript function names to the
    Python equivalents.

    :param str js:
        The contents of the base.js asset file.
    :param str var:
        The obfuscated variable name that stores an object with all functions
        that descrambles the signature.

    """
    transform_object = get_transform_object(js, var)
    mapper = {}
    for obj in transform_object:
        # AJ:function(a){a.reverse()} => AJ, function(a){a.reverse()}
        name, function = obj.split(':', 1)
        fn = map_functions(function)
        mapper[name] = fn
    return mapper


def reverse(arr, b):
    """Reverse elements in a list.

    This function is equivalent to:

    .. code-block:: javascript

       function(a, b) { a.reverse() }

    This method takes an unused ``b`` variable as their transform functions
    universally sent two arguments.

    **Example**:

    >>> reverse([1, 2, 3, 4])
    [4, 3, 2, 1]
    """
    return arr[::-1]


def splice(arr, b):
    """Add/remove items to/from a list.

    This function is equivalent to:

    .. code-block:: javascript

       function(a, b) { a.splice(0, b) }

    **Example**:

    >>> splice([1, 2, 3, 4], 2)
    [1, 2]
    """
    return arr[:b] + arr[b * 2:]


def swap(arr, b):
    """Swap positions at b modulus the list length.

    This function is equivalent to:

    .. code-block:: javascript

       function(a, b) { var c=a[0];a[0]=a[b%a.length];a[b]=c }

    **Example**:

    >>> swap([1, 2, 3, 4], 2)
    [3, 2, 1, 4]
    """
    r = b % len(arr)
    return list(chain([arr[r]], arr[1:r], [arr[0]], arr[r + 1:]))


def map_functions(js_func):
    """For a given JavaScript transform function, return the Python equivalent.

    :param str js_func:
        The JavaScript version of the transform function.

    """
    mapper = (
        # function(a){a.reverse()}
        ('{\w\.reverse\(\)}', reverse),
        # function(a,b){a.splice(0,b)}
        ('{\w\.splice\(0,\w\)}', splice),
        # function(a,b){var c=a[0];a[0]=a[b%a.length];a[b]=c}
        ('{var\s\w=\w\[0\];\w\[0\]=\w\[\w\%\w.length\];\w\[\w\]=\w}', swap),
        # function(a,b){var c=a[0];a[0]=a[b%a.length];a[b%a.length]=c}
        (
            '{var\s\w=\w\[0\];\w\[0\]=\w\[\w\%\w.length\];'
            '\w\[\w\%\w.length\]=\w}', swap,
        ),
    )

    for pattern, fn in mapper:
        if re.search(pattern, js_func):
            return fn
    raise RegexMatchError(
        'could not find python equivalent function for: ',
        js_func,
    )


def parse_function(js_func):
    """Parse the Javascript transform function.

    Break a JavaScript transform function down into a two element ``tuple``
    containing the function name and some integer-based argument.

    :param str js_func:
        The JavaScript version of the transform function.
    :rtype: tuple
    :returns:
        two element tuple containing the function name and an argument.

    **Example**:

    >>> parse_function('DE.AJ(a,15)')
    ('AJ', 15)

    """
    logger.debug('parsing transform function')
    return regex_search(r'\w+\.(\w+)\(\w,(\d+)\)', js_func, groups=True)


def get_signature(js, ciphered_signature):
    """Decipher the signature.

    Taking the ciphered signature, applies the transform functions.

    :param str js:
        The contents of the base.js asset file.
    :param str ciphered_signature:
        The ciphered signature sent in the ``player_config``.
    :rtype: str
    :returns:
       Decrypted signature required to download the media content.

    """
    tplan = get_transform_plan(js)
    # DE.AJ(a,15) => DE, AJ(a,15)
    var, _ = tplan[0].split('.')
    tmap = get_transform_map(js, var)
    signature = [s for s in ciphered_signature]

    for js_func in tplan:
        name, argument = parse_function(js_func)
        signature = tmap[name](signature, int(argument))
        logger.debug(
            'applied transform function\n%s', pprint.pformat(
                {
                    'output': ''.join(signature),
                    'js_function': name,
                    'argument': int(argument),
                    'function': tmap[name],
                }, indent=2,
            ),
        )
    return ''.join(signature)
