#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Python 3 tests template (changeme)"""

import logging
from nose.tools import assert_equal, assert_false, assert_true, raises
from os.path import abspath, join, realpath
from unittest import TestCase

logger = logging.getLogger(__name__)
test_data_path = abspath(realpath(join('tests', 'data')))


def setup_module():
    """Change me"""
    pass


def teardown_module():
    """Change me"""
    pass


class Test_This(TestCase):

    def setUp(self):
        """Change me"""
        pass

    def tearDown(self):
        """Change me"""
        pass

    def test_a(self):
        """Change me"""
        pass
