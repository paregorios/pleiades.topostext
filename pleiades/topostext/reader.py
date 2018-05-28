#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Read and index data from a ToposText TTL file
"""

import better_exceptions
import logging
from pleiades.matcher.tools import MatchTool
from pleiades.walker.walker import PleiadesWalker
from pprint import pprint
from rdflib import Graph, Namespace
from rdflib.namespace import RDF
from rdflib.term import BNode, Literal, URIRef
import re
import sys
from datetime import timedelta
import sys

logger = logging.getLogger(__name__)


THRESHOLD = 0.1
MAX_MSG = 255
TERMS = {
    'temporal': ('temporal', list),
    'description': ('description', str),
    'countryCode': ('country_code', str),
    'subject': ('subject', list),
    'exactMatch': ('matches', list),
    'label': ('label', str),
    'location': ('locations', None),
    'hasName': ('names', None),
    'precision': ('precision', str),
    'primaryForm': ('attested_name', str),
    'long': ('longitude', str),
    'lat': ('latitude', str)
}
RX_DESC_INIT = re.compile(r'^View \d+ ancient references to .+:\s+(.+)\(.+$')
RX_DESC_NAMES = re.compile(r'^.+\((.+)\)$')


class ToposTextPlace:

    def __init__(self, **kwargs):
        self.label = ""
        self.description = ""
        self.subject = ""
        self.country_code = ""
        self.matches = []
        self.names = []
        self.uri = ""
        self.locations = []
        self.precision = -1
        self.temporal = []
        self.blurb = ''
        for kw, arg in kwargs.items():
            try:
                getattr(self, kw)
            except AttributeError:
                if kw in ['latitude', 'longitude']:
                    try:
                        loc = self.locations[-1]
                    except IndexError:
                        loc = {}
                        self.locations.append(loc)
                    try:
                        loc[kw]
                    except KeyError:
                        loc[kw] = arg
                    else:
                        raise RuntimeError('horrors!')
                    self.locations[-1] = loc
                elif kw == 'attested_name':
                    self.names.append(arg)
                    self.names = list(set(self.names))
            else:
                setattr(self, kw, arg)
            if kw == 'description':
                m = RX_DESC_NAMES.match(arg)
                if m is not None:
                    self.names.extend(
                        [n.strip() for n in m.group(1).split(',')])
                    self.names = list(set(self.names))

    def __str__(self):
        if self.blurb == '':
            parts = [p.strip() for p in self.uri.split('/')]
            parts = [p for p in parts if p != '']
            msg = ' '.join((parts[-1], self.label))
            if len(msg) < MAX_MSG:
                m = RX_DESC_INIT.match(self.description)
                if m is not None:
                    words = m.groups()[0].split()
                else:
                    words = self.description.split()
                i = 0
                while len(msg) < MAX_MSG - 4:
                    i += 1
                    if i == len(words):
                        break
                msg = '{}: {}'.format(msg, ' '.join(words[0:i]))
                if i < len(words):
                    msg += ' ...'
            self.blurb = msg
        return self.blurb


class ToposTextReader:

    def __init__(self):
        self.counts = {}
        self.namespaces = {}
        self.pleiades_match_tool = None
        self.triple_index = {
            'rdf': {
                'type': {}
            }
        }
        self.place_index = {}

    def load(self, path):
        self.g = Graph()
        self.g.parse(path, format='turtle')

    def load_pleiades(self, path):
        walker = PleiadesWalker(path=path)
        place_count, place_collection = walker.walk()
        self.pleiades_match_tool = MatchTool(place_collection)

    def count(self, rdftype='lawd:Place'):
        """Get count of triples parsed"""
        try:
            n = self.counts[rdftype]
        except KeyError:
            self._count_triples(rdftype)
            n = self.counts[rdftype]
        return n

    def match_places(
            self,
            check_pleiades=False):
        """Match ToposText lawd:Places to corresponding Pleiades places."""
        if self.count() > len(self.place_index):
            for uri in self._get_by_type('lawd:Place'):
                self.get_place(uri)  # will be automatically indexed
        matched = {}
        for uri, topos_place in self.place_index.items():
            pleiades_uris = [
                m for m in topos_place.matches if 'pleiades.stoa.org' in m]
            if len(pleiades_uris) != 1:
                matched[str(uri)] = None
            elif len(pleiades_uris) == 1:
                matched[str(uri)] = pleiades_uris[0]
            else:
                raise RuntimeError('weird')
        if check_pleiades:
            if self.pleiades_match_tool is None:
                raise RuntimeError(
                    'pleiades match tool has not been initialized')
            checked = {}
            for topo_uri, pleiades_uri in matched.items():
                topo_place = self.get_place(topo_uri)
                if len(topo_place.locations) != 1:
                    raise RuntimeError(
                        'wrong number of topos locations: {}'
                        ''.format(len(topo_place.locations)))
                tpl = topo_place.locations[0]
                points = [(float(tpl['longitude']), float(tpl['latitude']))]
                results = self.pleiades_match_tool.match(
                    points=points,
                    names=topo_place.names
                )
                checked[topo_uri] = {
                    'agree': False,
                    'alternates': []
                }
                if len(results) == 0 and pleiades_uri is None:
                    checked[topo_uri]['agree'] = True
                else:
                    for result in results:
                        result_uri = result.data['uri']
                        while result_uri.endswith('/'):
                            result_uri = result_uri[:-1]
                        while pleiades_uri.endswith('/'):
                            pleiades_uri = pleiades_uri[:-1]
                        if result_uri == pleiades_uri:
                            checked[topo_uri]['agree'] = True
                        else:
                            checked[topo_uri]['alternates'].append(result_uri)
            return (matched, checked)
        else:
            return (matched, None)

    def _count_triples(self, rdftype: str):
        """Query the graph for a triple count"""
        prefix, term = rdftype.split(':')
        triples = self._get_by_type(rdftype)
        # triples = self.g.triples((None, RDF.type, getattr(ns, term)))
        self.counts[rdftype] = len(list(triples))

    def _get_pleiades_from_place(self, topostext_uri: URIRef):
        ns = self._get_namespace('skos')
        matches = self.g.objects(
            subject=topostext_uri, predicate=ns.exactMatch)
        matches = [
            s for s in matches if str(s).startswith(
                'https://pleiades.stoa.org/places/')]
        return matches

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

    def get_place(self, uri: str):
        uri_ref = URIRef(uri)
        try:
            place = self.place_index[uri]
        except KeyError:
            attribs = self._extract_from_graph(uri_ref)
            place = ToposTextPlace(**attribs)
            self.place_index[uri] = place
        return place

    def _extract_from_triple(self, triple):
        s, p, o = triple
        term = str(p).split('/')[-1].split('#')[-1]
        try:
            k, k_type = TERMS[term]
        except KeyError:
            return ()  # ignore this term
        else:
            if k is not None:
                if isinstance(o, Literal) or isinstance(o, URIRef):
                    return [(k, k_type, str(o))]
                elif isinstance(o, BNode):
                    if k_type is None:
                        values = list(self.g.triples((o, None, None)))
                        results = []
                        for v in values:
                            results.extend(self._extract_from_triple(v))
                        return results
                    else:
                        raise RuntimeError(
                            'unexpected ')
                else:
                    raise RuntimeError(
                        'extract failure on {}: {}'.format(k, type(o)))

    def _extract_from_graph(self, uri):
        triples = list(self.g.triples((uri, None, None)))
        if len(triples) == 0:
            raise ValueError(
                'The URI "{}" is not a subject in this graph.'
                ''.format(str(uri)))
        attribs = {
            'uri': str(uri)
        }
        for triple in triples:
            results = self._extract_from_triple(triple)
            for result in results:
                k, k_type, val = result
                if k_type == list:
                    try:
                        attribs[k]
                    except KeyError:
                        attribs[k] = []
                    attribs[k].append(val)
                else:
                    attribs[k] = val
        return attribs
