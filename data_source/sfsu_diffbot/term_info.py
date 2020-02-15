"""
File:         term.py
Package:      SFSU-Diffbot-API
Author:       Jose Ortiz Costa <jortizco@mail.sfsu.edu>
Date:         09-29-2017
Modified:     09-29-2017
Description:  This file contains usefull info about a specific terms from the original query

IMPORTANT:    Terms are objects created from QueryInfo class

USAGE:        query = content.queryInfo()
              term = query.term()
              term.freq() # frequence of the term
"""

class Term(object):
    def __init__(self, term_metadata):
        """
        Constructor
        :param term_metadata:
        """
        self._term_info = term_metadata

    def _field(self, key):
        if key in self._term_info:
            return self._term_info[key]

    # Public properties of a term object

    def to_str(self):
        return self._term_info['termStr']

    def isIgnored(self):
        return self._term_info['isIgnored']

    def isRequired(self):
        return self._term_info['isRequired']

    def freq(self):
        return self._term_info['termFreq']

    def index(self):
        return self._term_info['termNum']

    def hash_48(self):
        return self._term_info['termHash48']

    def hash_64(self):
        return self._term_info['termHash64']

    def meta_data(self):
        return self._term_info