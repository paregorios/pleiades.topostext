#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Match topostext places to pleiades places
"""

import better_exceptions
from airtight.cli import configure_commandline
import json
import logging
from os.path import abspath, join, realpath
from pleiades.topostext.reader import ToposTextReader
from pprint import pprint

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
    ['-j', '--pleiades_json', '', 'use Pleiades json for checks', False],
    ['-o', '--output', '', 'existing directory to which to dump all output',
        False]
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
    if kwargs['pleiades_json']:
        json_path = abspath(realpath(kwargs['pleiades_json']))
        reader.load_pleiades(json_path)
        matched, checked = reader.match_places(check_pleiades=True)
    else:
        matched, checked = reader.match_places(check_pleiades=False)
    citations = {}
    if checked is None:
        raise NotImplementedError('foo')
    for topo_uri, pleiades_uri in matched.items():
        if checked[topo_uri]['agree'] and pleiades_uri is not None:
            try:
                citations[pleiades_uri]
            except KeyError:
                citations[pleiades_uri] = []
            finally:
                topos_place = reader.get_place(topo_uri)
                citations[pleiades_uri].append(
                    {
                        'access_uri': topo_uri,
                        'bibliographic_uri': 'https://www.zotero.org/groups/'
                                             '2533/items/MC9RGDVB',
                        'citation_detail': topos_place.label,
                        'formatted_citation': (
                            'Kiesling, Brady. ToposText – a Reference Tool '
                            'for Greek Civilization. Version 2.0. Aikaterini '
                            'Laskaridis Foundation, 2016-.'),
                        'short_title': 'ToposText',
                    }
                )
    references = {}
    errors = {}
    for pleiades_uri, cc in citations.items():
        if len(cc) != 1:
            for c in cc:
                try:
                    errors[c['access_uri']]
                except KeyError:
                    errors[c['access_uri']] = {
                        'msg': [],
                        'error_codes': []
                    }
                finally:
                    errors[
                        c['access_uri']]['error_codes'].append(
                            'oversubscribed')
                    errors[c['access_uri']]['msg'].append(
                        'This is not the only ToposText place to claim '
                        'association with {}. See also: {}.'
                        ''.format(
                            pleiades_uri,
                            [d['access_uri'] for d in cc if
                                d['access_uri'] != c['access_uri']]))
        else:
            references[pleiades_uri] = cc

    if kwargs['output'] != '':
        out_dir = abspath(realpath(kwargs['output']))
        ref_path = join(out_dir, 'references.json')
        with open(ref_path, 'w') as f:
            json.dump(
                references, f, indent=4, ensure_ascii=False, sort_keys=True)
        del f
        for topo_uri, results in checked.items():
            if not results['agree']:
                pleiades_uri = matched[topo_uri]
                error_code = ''
                msg = ['Pleiades checking did not agree with ToposText.']
                alternates = results['alternates']
                alt_len = len(alternates)
                if pleiades_uri is None and alt_len > 0:
                    error_code = 'topos_no_pleiades_yes'
                    msg.append(
                        'ToposText asserts that there is no Pleiades match, '
                        'but there are {} possible Pleiades alternates.'
                        ''.format(alt_len))
                elif pleiades_uri is not None:
                    msg.append(
                        'ToposText asserts that the Pleiades match is {},'
                        'but Pleiades checking disagrees.'
                        ''.format(pleiades_uri))
                    if alt_len == 0:
                        error_code = 'topos_yes_pleiades_no'
                        msg.append(
                            'Pleiades checking did not find any alternative '
                            'matches.')
                    else:
                        error_code = 'topos_yes_pleiades_multiple'
                        msg.append(
                            'Pleiades checking found {} possible Pleiades '
                            'matches.'.format(alt_len))
                else:
                    error_code = 'undefined'
                    msg.append(
                        'Pleiades checking is grumpy about something, but I '
                        'have no idea what.')
                try:
                    errors[topo_uri]
                except KeyError:
                    errors[topo_uri] = {
                        'msg': [],
                        'error_codes': []
                    }
                finally:
                    errors[topo_uri]['error_codes'].append(error_code)
                    errors[topo_uri]['msg'].append(' '.join(msg))
                    errors[topo_uri]['alternates'] = results['alternates'],
                    errors[topo_uri]['topos_match'] = pleiades_uri
        err_path = join(out_dir, 'errors.json')
        with open(err_path, 'w') as f:
            json.dump(
                errors, f, indent=4, ensure_ascii=False, sort_keys=True)
        del f
        print('{} ToposText places checked'.format(reader.count()))
        print(
            'ToposText claimed {} matches with Pleiades'
            ''.format(len([k for k, m in matched.items() if m is not None])))
        print(
            'The Pleiades match tool verified {} of those matches and wrote '
            'them to {}.'
            ''.format(len(references), ref_path))
        print(
            '{} errors were detected and written to {}.'
            ''.format(len(errors), err_path))
        print('error breakdown as follows:')
        print(
            '\tUnverified ToposText match assertion:'
            ' {}'.format(
                len(
                    [e for uri, e in errors.items()
                        if 'topos_yes_pleiades_no' in e['error_codes']])))
        print(
            '\tPossible match not asserted by ToposText:'
            ' {}'.format(
                len(
                    [e for uri, e in errors.items()
                        if 'topos_no_pleiades_yes' in e['error_codes']])))
        print(
            '\tToposText asserts Pleiades match, but there are multiple '
            'candidates in Pleiades:'
            ' {}'.format(
                len(
                    [e for uri, e in errors.items()
                        if 'topos_yes_pleiades_multiple' in e['error_codes']]
                )))
        print(
            '\tToposText asserts same Pleiades match for multiple entries:'
            ' {}'.format(
                len(
                    [e for uri, e in errors.items()
                        if 'oversubscribed' in e['error_codes']])))
        print(
            '\tUndefined errors:'
            ' {}'.format(
                len(
                    [e for uri, e in errors.items()
                        if 'undefined' in e['error_codes']])))
    else:
        print(json.dumps(
            references, indent=4, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main(**configure_commandline(
        OPTIONAL_ARGUMENTS, POSITIONAL_ARGUMENTS, DEFAULT_LOG_LEVEL))
