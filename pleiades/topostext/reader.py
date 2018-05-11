#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Read and index data from a ToposText TTL file
"""

import better_exceptions
import logging
from rdflib import Graph, Namespace
from rdflib.namespace import RDF

logger = logging.getLogger(__name__)


class ToposTextReader:

    def __init__(self):
        self.counts = {}

    def load(self, path):
        self.g = Graph()
        self.g.parse(path, format='turtle')

    def count(self, rdftype='lawd:Place'):
        """Get count of triples parsed"""
        try:
            n = self.counts[rdftype]
        except KeyError:
            self._count_triples(rdftype)
            n = self.counts[rdftype]
        return n

    def _count_triples(self, rdftype: str):
        """Query the graph for a triple count"""
        prefix, term = rdftype.split(':')
        ns = self._get_namespace(prefix)
        triples = self.g.triples((None, RDF.type, getattr(ns, term)))
        self.counts[rdftype] = len(list(triples))

    def _get_namespace(self, prefix: str):
        nsm = self.g.namespace_manager
        nsd = dict(list(nsm.namespaces()))
        return Namespace(str(nsd['lawd']))

