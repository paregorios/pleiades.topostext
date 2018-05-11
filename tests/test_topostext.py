#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test ToposText reading"""

import logging
from nose.tools import assert_equal, assert_false, assert_true, raises
from os.path import abspath, join, realpath
from pleiades.topostext.reader import ToposTextReader
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
        count = reader.count()
        assert_equal(count, 9)

