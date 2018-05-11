#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Read and index data from a ToposText TTL file
"""

import better_exceptions
import logging
from rdflib import Graph

logger = logging.getLogger(__name__)


class ToposTextReader:

    def __init__(self):
        pass

    def load(self, path):
        g = Graph()
        g.parse(path)
