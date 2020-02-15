"""
File:         image.py
Package:      SFSU-Diffbot-API
Author:       Jose Ortiz Costa <jortizco@mail.sfsu.edu>
Date:         09-29-2017
Modified:     09-29-2017
Description:  This file contains a object representation of an image extracted from the diffbot knoledge graph

IMPORTANT:    Images objects comes from Objects and Images api

USAGE:        # from object content
              object = content.object(0)
              images = object.images() # all the images from the object
              image = object.image.(0) # first image from the object
              image.caption() # caption
              image.title() # title
              image.url() # url

              # from Image api
              image = client,content(DiffbotType.IMAGE, query)
              image.title() # title
              image.date() # creation date
"""

class Image(object):
    """
    Image class with all the properties from a image object e.g. image.text, image.heigh...etc
    """
    def __init__(self, image_content):
        """
        Constructor
        :param image_content: the image metadata from the content
        """
        self._image_content = image_content

    def _field(self, key):
        """
        Retrieves a image value from a given key
        :param key: the field key
        :return: the value stored in the corresponding image field key
        """
        return self._image_content[key]

    def diffbotUri(self):
        """

        :return: the url where diffbot stores the id of the image
        """
        if 'diffbotUri' in self._image_content:
            return self._field('diffbotUri')

    def heigh(self):
        """

        :return: the image field
        """
        if 'naturalHeight' in self._image_content:
            return self._field('naturalHeight')

    def width(self):
        """

        :return: the image width
        """
        if 'naturalWidth' in self._image_content:
            return self._field('naturalWidth')

    def is_primary(self):
        """

        :return: true if the image is primary. Otherwise returns false
        """
        if 'primary' in self._image_content:
            return self._field('primary')

    def title(self):
        """

        :return: the image title
        """
        if 'title' in self._image_content:
            return self._field('title')

    def url(self):
        """

        :return: the image url
        """
        if 'url' in self._image_content:
            return self._field('url')

    def date(self):
        """

        :return:
        """
        if 'date' in self._image_content:
            return self._field('date')

    def xpath(self):
        """

        :return:
        """
        if 'xpath' in self._image_content:
            return self._field('xpath')

    def type(self):
        if 'type' in self._image_content:
            return self._field('type')

    def resolvedPageUrl(self):
        if 'resolvedPageUrl' in self._image_content:
            return self._field('resolvedPageUrl')

    def meta_data(self):
        return self._image_content
