#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pathlib

from prettyconf import config

PROJECT_ROOT = pathlib.Path(os.path.normpath(os.path.split(__file__)[0]))

LOG_PATH = PROJECT_ROOT / 'logs'
if not os.path.isdir(LOG_PATH):
    os.mkdir(LOG_PATH)

LOG_LEVEL = config('CHKWEB_LOG_LEVEL', default='DEBUG')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(name)s:%(levelname)s %(asctime)s %(message)s',
            'datefmt': '%Y-%m-%dT%H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        'logfile': {
            'level': LOG_LEVEL,
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_PATH, 'chkweb.log'),
            'maxBytes': 500000,
            'backupCount': 5,
            'formatter': 'standard',
        }
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'chkweb': {
            'handlers': ['logfile'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
    },
}
