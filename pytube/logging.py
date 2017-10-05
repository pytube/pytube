# -*- coding: utf-8 -*-
"""
pytube.logging
~~~~~~~~~~~~~~

This module implements a lightweight json log formatter and log factory.
"""
import datetime as dt
import json
import logging
from collections import OrderedDict

from pytube import __version__


KEPT_ATTRS = ('funcName', 'module',)
RESERVED_ATTRS = (
    'args',
    'created',
    'exc_info',
    'exc_text',
    'filename',
    'levelno',
    'lineno',
    'msecs',
    'msg',
    'name',
    'pathname',
    'process',
    'processName',
    'relativeCreated',
    'stack_info',
    'thread',
    'threadName',
)


class JsonFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        logging.Formatter.__init__(self, *args, **kwargs)
        self.json_encoder = kwargs.get('json_encoder', self.json_encode)
        self.kept_attrs = kwargs.get('kept_attrs', KEPT_ATTRS)
        self.permanent_metadata = kwargs.get('metadata', {})
        self.skipped_attrs = kwargs.get('skipped_attrs', RESERVED_ATTRS)

    def extra_metadata(self):
        return self.permanent_metadata

    def get_timestamp(self):
        return dt.datetime.utcnow().isoformat()

    def json_encode(self, obj):
        try:
            if isinstance(obj, (bool, str, int, float, None,)):
                return obj
        except TypeError:
            pass

        return str(obj)

    def jsonify(self, log):
        return json.dumps(log, default=self.json_encoder, indent=2)

    def format(self, record):
        new_record = OrderedDict()

        new_record['timestamp'] = self.get_timestamp()
        new_record['message'] = record.getMessage()
        new_record['levelname'] = record.__dict__.pop('levelname')
        new_record['version'] = __version__

        new_record.update(OrderedDict({'metadata': {'extra': {}}}))
        # new_record['metadata'].update(self.extra_metadata())

        for key, value in record.__dict__.items():
            if key in self.kept_attrs:
                new_record['metadata'][key] = value
            elif key not in self.skipped_attrs:
                new_record['metadata']['extra'][key] = value

        if record.exc_info:
            fmt_exception = self.formatException(record.exc_info)
            new_record['metadata']['exception'] = fmt_exception

        return '%s' % (self.jsonify(new_record))


def create_logger():
    logger = logging.getLogger()

    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger
