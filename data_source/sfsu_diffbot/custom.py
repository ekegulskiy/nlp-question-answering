"""
File:         custom.py
Package:      SFSU-Diffbot-API
Author:       Jose Ortiz Costa <jortizco@mail.sfsu.edu>
Date:         09-29-2017
Modified:     09-29-2017
Description:  This file contains a object representation of a custom api extracted from the diffbot knoledge graph

IMPORTANT:    Custom api needs to be pre-configured first at Diffbot.com by using the Diffbot Custom Api Toolkit

USAGE:        # from object content
              url = "example url"
              custom = client.custom_content(url)
"""
class Custom(object):
    def __init__(self, custom_metadata):
        self._custom = custom_metadata

    def fields(self, key):
        if key in self._custom:
            return self._custom[key]

    def all(self):
        return self._custom

    def toString(self):
        return str(self._custom)

    def meta_data(self):
        return self._custom