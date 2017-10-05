# -*- coding: utf-8 -*-
"""
pytube.cipher
~~~~~~~~~~~~~

"""
from __future__ import absolute_import

import logging
import re
from itertools import chain

from pytube.helpers import memoize


logger = logging.getLogger(__name__)


def get_initial_function_name(js):
    """Extracts the name of the function responsible for computing the signature.
    """
    # c&&d.set("signature", EE(c));
    pattern = r'"signature",\s?([a-zA-Z0-9$]+)\('
    regex = re.compile(pattern)
    return (
        regex
        .search(js)
        .group(1)
    )


def get_transform_plan(js):
    """Extracts the "transform plan", that is, the functions the original
    signature is passed through to decode the actual signature.

    Sample Output:
    ~~~~~~~~~~~~~~
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
    regex = re.compile(pattern)
    return (
        regex
        .search(js)
        .group(1)
        .split(';')
    )


def get_transform_object(js, var):
    """Extracts the "transform object" which contains the function definitions
    referenced in the "transform plan". The ``var`` argument is the obfuscated
    variable name which contains these functions, for example, given the
    function call ``DE.AJ(a,15)`` returned by the transform plan, "DE" would be
    the var.

    Sample Output:
    ~~~~~~~~~~~~~~
    ['AJ:function(a){a.reverse()}',
     'VR:function(a,b){a.splice(0,b)}',
     'kT:function(a,b){var c=a[0];a[0]=a[b%a.length];a[b]=c}']

    """
    pattern = r'var %s={(.*?)};' % re.escape(var)
    regex = re.compile(pattern, re.DOTALL)
    return (
        regex
        .search(js)
        .group(1)
        .replace('\n', ' ')
        .split(', ')
    )


def get_transform_map(js, var):
    transform_object = get_transform_object(js, var)
    mapper = {}
    for obj in transform_object:
        # AJ:function(a){a.reverse()} => AJ, function(a){a.reverse()}
        name, function = obj.split(':', 1)
        fn = map_functions(function)
        mapper[name] = fn
    return mapper


def reverse(arr, b):
    """Immutable equivalent to function(a){a.reverse()}.

    Example usage:
    ~~~~~~~~~~~~~~
    >>> reverse([1, 2, 3, 4])
    [4, 3, 2, 1]
    """
    return arr[::-1]


def splice(arr, b):
    """Immutable equivalent to function(a,b){a.splice(0,b)}.

    Example usage:
    ~~~~~~~~~~~~~~
    >>> splice([1, 2, 3, 4], 2)
    [1, 2]
    """
    return arr[:b] + arr[b * 2:]


def swap(arr, b):
    """Immutable equivalent to:
    function(a,b){var c=a[0];a[0]=a[b%a.length];a[b]=c}.

    Example usage:
    ~~~~~~~~~~~~~~
    >>> swap([1, 2, 3, 4], 2)
    [3, 2, 1, 4]
    """
    r = b % len(arr)
    return list(chain([arr[r]], arr[1:r], [arr[0]], arr[r + 1:]))


def map_functions(js_func):
    """Maps the javascript function to its Python equivalent.
    """
    mapper = (
        # function(a){a.reverse()}
        ('{\w\.reverse\(\)}', reverse),
        # function(a,b){a.splice(0,b)}
        ('{\w\.splice\(0,\w\)}', splice),
        # function(a,b){var c=a[0];a[0]=a[b%a.length];a[b]=c}
        ('{var\s\w=\w\[0\];\w\[0\]=\w\[\w\%\w.length\];\w\[\w\]=\w}', swap),
    )

    for pattern, fn in mapper:
        if re.search(pattern, js_func):
            return fn
    # TODO(nficano): raise error


def parse_function(js_func):
    pattern = r'\w+\.(\w+)\(\w,(\d+)\)'
    regex = re.compile(pattern)
    return (
        regex
        .search(js_func)
        .groups()
    )


@memoize
def get_signature(js, signature):
    tplan = get_transform_plan(js)
    # DE.AJ(a,15) => DE, AJ(a,15)
    var, _ = tplan[0].split('.')
    tmap = get_transform_map(js, var)
    signature = [s for s in signature]

    for js_func in tplan:
        name, argument = parse_function(js_func)
        signature = tmap[name](signature, int(argument))
    return ''.join(signature)
