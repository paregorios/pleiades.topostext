#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python 3 script template (changeme)
"""

import better_exceptions
from airtight.cli import configure_commandline
import logging
from os.path import abspath, realpath
from pleiades.topostext.reader import ToposTextReader

logger = logging.getLogger(__name__)

DEFAULT_LOG_LEVEL = logging.WARNING
OPTIONAL_ARGUMENTS = [
    ['-l', '--loglevel', 'NOTSET',
        'desired logging level (' +
        'case-insensitive string: DEBUG, INFO, WARNING, or ERROR',
        False],
    ['-v', '--verbose', False, 'verbose output (logging level == INFO)',
        False],
    ['-w', '--veryverbose', False,
        'very verbose output (logging level == DEBUG)', False],
    ['-c', '--check', False, 'check against pleiades data', False],
    ['-j', '--json_dir', '', 'use Pleiades json for checks', False]
]
POSITIONAL_ARGUMENTS = [
    # each row is a list with 3 elements: name, type, help
    ['topostext_ttl', str, 'path to ToposText RDF/TTL file']
]


def main(**kwargs):
    """
    main function
    """
    path = abspath(realpath(kwargs['topostext_ttl']))
    reader = ToposTextReader()
    reader.load(path)
    if kwargs['json_dir'] == '':
        matches = reader.match_places(check_pleiades=kwargs['check'])
    else:
        json_path = abspath(realpath(kwargs['json_dir']))
        matches = reader.match_places(
            check_pleiades=kwargs['check'], pleiades_path=json_path)
    print(len(matches))

if __name__ == "__main__":
    main(**configure_commandline(
            OPTIONAL_ARGUMENTS, POSITIONAL_ARGUMENTS, DEFAULT_LOG_LEVEL))
