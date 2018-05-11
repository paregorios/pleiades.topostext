#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test ToposText reading"""

import logging
from nose.tools import assert_equal, assert_false, assert_true, raises
from os.path import abspath, join, realpath
from pleiades.topostext.reader import ToposTextReader
from rdflib.term import URIRef
from unittest import TestCase


logger = logging.getLogger(__name__)
test_data_path = abspath(realpath(join('tests', 'data', 'pelagios.ttl')))


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
        assert_equal(count, 9)

    def test_place_get(self):
        """Test getting places"""
        place_uris = reader._get_by_type('lawd:Place')
        assert_equal(len(place_uris), 9)
        assert_equal(
            str(place_uris[0]), 'https://topostext.org/place/257326PThe')
        assert_true(isinstance(place_uris[0], URIRef))

    def test_get_pleiades(self):
        """Test getting Pleiades matches"""
        topostext_uris = reader._get_by_type('lawd:Place')
        pleiades_uris = reader._get_pleiades_from_place(topostext_uris[0])
        assert_equal(len(pleiades_uris), 1)
        assert_equal(
            str(pleiades_uris[0]), 'https://pleiades.stoa.org/places/786017/')

