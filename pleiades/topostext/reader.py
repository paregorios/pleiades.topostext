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
        self.namespaces = {}
        self.pleiades_places = {}
        self.triple_index = {
            'rdf': {
                'type': {}
            }
        }

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

    def match_places(self, pleiades_path='https://pleiades.stoa.org/'):
        """Match ToposText lawd:Places to corresponding Pleiades places."""
        pass

    def _count_triples(self, rdftype: str):
        """Query the graph for a triple count"""
        prefix, term = rdftype.split(':')
        ns = self._get_namespace(prefix)
        triples = self._get_by_type(rdftype)
        triples = self.g.triples((None, RDF.type, getattr(ns, term)))
        self.counts[rdftype] = len(list(triples))

    def _get_by_type(self, rdftype: str):
        prefix, term = rdftype.split(':')
        idx_type = self.triple_index['rdf']['type']
        try:
            idx_ns = idx_type[prefix]
        except KeyError:
            idx_type[prefix] = {}
            idx_ns = idx_type[prefix]
        try:
            uris = idx_ns[term]
        except KeyError:
            ns = self._get_namespace(prefix)
            uris = self.g.subjects(
                predicate=RDF.type, object=getattr(ns, term))
            idx_ns[term] = sorted(list(uris), key=lambda uri: str(uri))
            uris = idx_ns[term]
        return uris

    def _get_namespace(self, prefix: str):
        try:
            return self.namespaces[prefix]
        except KeyError:
            nsm = self.g.namespace_manager
            nsd = dict(list(nsm.namespaces()))
            self.namespaces[prefix] = Namespace(str(nsd[prefix]))
            return self.namespaces[prefix]


