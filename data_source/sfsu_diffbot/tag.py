"""
File:         tag.py
Package:      SFSU-Diffbot-API
Author:       Jose Ortiz Costa <jortizco@mail.sfsu.edu>
Date:         09-29-2017
Modified:     09-29-2017
Description:  This file contains the object Tag which represents a tag from a object/page response and it has methods
              to access to all its tag properties.

IMPORTANT:    A Tag object may act recursively. That's it, a tag is extracted from a object, and new content,
              their objects and their sub-tags may be built from that tag.

USAGE:        # assuming that the response content and an object of this content has been already created
              tag = object.tags() # all tags objects from a specific object
              tag = object.tag(0) # the first tag object
              tag = object.sort_tags_by_score() # all tags objects sorted by score
              # some tag's properties
              tag.score() # the tag score
              tag.uri() # the tag url
              # new content from a tag
              content = client.content(DiffbotType.Article, tag.uri())
"""
class Tag(object):
    """
    Represents a tag object and all its properties
    """
    def __init__(self, tag):
        """
        Constructor
        :param tag: the tag metadata
        """
        self._tag = tag

    def _value(self, key):
        """

        :param key:
        :return: the tag field value
        """
        if key in self._tag:
            return self._tag[key]

    def score(self):
        """

        :return: the tag score
        """
        return self._value('score')

    def rdfTypes(self):
        """

        :return: the rdfTypes from the tag
        """
        return self._value('rdfTypes')

    def uri(self):
        """

        :return: the tag uri
        """
        return self._value('uri')

    def label(self):
        """

        :return: the tag label
        """
        return self._value('label')

    def count(self):
        """
        the tag count
        :return:
        """
        return self._value('count')

    def toString(self):
        """

        :return: the string representation of the tag
        """
        return self._tag

    def meta_data(self):
        return self._tag



