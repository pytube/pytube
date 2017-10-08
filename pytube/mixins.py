# -*- coding: utf-8 -*-
"""
pytube.mixins
~~~~~~~~~~~~~

Applies in-place data mutations.
"""
from __future__ import absolute_import

import json
import logging

from pytube import cipher
from pytube.compat import parse_qsl
from pytube.compat import unquote


logger = logging.getLogger(__name__)


def apply_signature(config_args, fmt, js):
    """Applies the decrypted signature to the stream manifest.

    :param dict config_args:
        Details of the media streams available.
    :param str fmt:
        Key in stream manifests ("player_config") containing progressive
        download or adaptive streams (e.g.: "url_encoded_fmt_stream_map" or
        "adaptive_fmts").
    :param str js:
        The contents of the base.js asset file.
    """
    stream_manifest = config_args[fmt]
    for i, stream in enumerate(stream_manifest):
        url = stream['url']

        if 'signature=' in url:
            continue

        signature = cipher.get_signature(js, stream['s'])

        logger.debug(
            'finished descrambling signature for itag=%s\n%s',
            stream['itag'], json.dumps(
                {
                    's': stream['s'],
                    'signature': signature,
                }, indent=2,
            ),
        )
        stream_manifest[i]['url'] = url + '&signature=' + signature


def apply_parse_qs(dct, key):
    """Parses query string key/values into dictionary, and then applies it
    in-place.

    :param dict dct:
        Dictionary containing query string encoded values.
    :param str key:
        Name of the key in dictionary.
    """
    dct[key] = [
        {k: unquote(v) for k, v in parse_qsl(i)} for i in dct[key].split(',')
    ]
