"""
File:         product.py
Package:      SFSU-Diffbot-API
Author:       Jose Ortiz Costa <jortizco@mail.sfsu.edu>
Date:         09-29-2017
Modified:     09-29-2017
Description:  This file contains a object representation of a product extracted from the diffbot knoledge graph

IMPORTANT:    Images objects comes from Objects and Images api

USAGE:        # from object content
              url = "your url to the target product"
              product = client.content_product(url)
              product.regularPrice()
"""
from data_source.sfsu_diffbot.image import Image
class Product(object):
    """
    Product class
    """
    def __init__(self, product_metadata):
        """
        Contstructor
        :param product_metadata:
        """
        self._product = product_metadata

    def _field(self, key):
        if key in self._product:
            return self._product[key]

    # public product properties

    def pageUrl(self):
        return self._field('pageUrl')

    def type(self):
        return self._field('type')

    def resolvedPageUrl(self):
        return self._field('resolvedPageUrl')

    def title(self):
        return self._field('title')

    def text(self):
        return self._field('text')

    def brand(self):
        return self._field('brand')

    def offerPrice(self):
        return self._field('offerPrice')

    def regularPrice(self):
        return self._field('regularPrice')

    def shippingAmount(self):
        return self._field('shippingAmount')

    def saveAmount(self):
        return self._field('saveAmount')

    def offerPriceDetails(self):
        return self._field('offerPriceDetails')

    def regularPriceDetails(self):
        return self._field('type')

    def saveAmountDetails(self):
        return self._field('saveAmountDetails')

    def humanLanguage(self):
        if 'humanLanguage' in self._product:
            return self._field('humanLanguage')

    def url(self):
        """

        :return: the image url
        """
        if 'url' in self._product:
            return self._field('url')
        else:
            return self.pageUrl()

    def productId(self):
        return self._field('productId')

    def upc(self):
        return self._field('upc')

    def sku(self):
        return self._field('sku')

    def mpn(self):
        return self._field('mpn')

    def isbn(self):
        return self._field('isbn')

    def specs(self):
        return self._field('specs')

    def images(self):
        images_list = []
        images = self._field('images')
        for image in images:
            images_list = Image(image)
        return images_list

    def image(self, index):
        return self.images()[index]

    def to_string(self):
        return self._product

    def availability(self):
        return self._field('availability')

    def meta_data(self):
        return self._product





