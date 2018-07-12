#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test ToposText reading"""

import logging
from nose.tools import assert_equal, assert_false, assert_true, raises, assert_is_none
from os.path import abspath, join, realpath
from pleiades.topostext.reader import ToposTextPlace, ToposTextReader
from rdflib.term import URIRef
from unittest import TestCase


logger = logging.getLogger(__name__)
test_data_path = abspath(realpath(join('tests', 'data', 'pelagios.ttl')))
pleiades_path = abspath(realpath(join('tests', 'data', 'pleiades_json')))


def setup_module():
    """Load test data with a reader"""
    global reader
    reader = ToposTextReader()
    reader.load(test_data_path)


def teardown_module():
    """Change me"""
    pass


class Test_This(TestCase):
    global reader

    def setUp(self):
        """Change me"""
        pass

    def tearDown(self):
        """Change me"""
        pass

    def test_place_count(self):
        """Test place count"""
        count = reader.count(rdftype='lawd:Place')
        assert_equal(count, 11)

    def test_place_get(self):
        """Test getting places"""
        place_uris = reader._get_by_type('lawd:Place')
        assert_equal(len(place_uris), 11)
        assert_equal(
            str(place_uris[0]), 'https://topostext.org/place/000000IAtl')
        assert_true(isinstance(place_uris[0], URIRef))

    def test_get_pleiades(self):
        """Test getting Pleiades matches"""
        topostext_uris = reader._get_by_type('lawd:Place')
        pleiades_uris = reader._get_pleiades_from_place(topostext_uris[0])
        assert_equal(len(pleiades_uris), 0)
        pleiades_uris = reader._get_pleiades_from_place(topostext_uris[1])
        assert_equal(
            str(pleiades_uris[0]), 'https://pleiades.stoa.org/places/786017/')

    def test_topo_place(self):
        """Test creating topostext places"""
        place = reader.get_place('https://topostext.org/place/257326PThe')
        assert_equal(
            '257326PThe Thebes (Egypt): Bronze Age to Late Antique city near '
            'Luxor in Egypt', str(place))
        assert_equal('EG', place.country_code)
        assert_equal('32.641', place.locations[0]['longitude'])
        assert_equal(
            sorted(
                [a for a in dir(place) if not a.startswith('_')]),
            [
                'blurb',
                'country_code',
                'description',
                'label',
                'locations',
                'matches',
                'names',
                'precision',
                'subject',
                'temporal',
                'uri'
            ])

    def test_match_places(self):
        """Test getting all Pleiades matches."""
        matched, checked = reader.match_places()
        assert_is_none(checked)
        assert_true(isinstance(matched, dict))
        assert_equal(11, len(matched))

    def test_match_places_check(self):
        """Test getting all Pleiades matches, with verification."""
        reader.load_pleiades(pleiades_path)
        matched, checked = reader.match_places(check_pleiades=True)
        assert_equal(len(matched), 11)
        assert_equal(len(checked), 11)
        failures = {k: v for k, v in checked.items() if not(v['agree'])}
        assert_equal(len(failures), 3)

