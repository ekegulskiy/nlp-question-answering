"""
File:         content.py
Package:      SFSU-Diffbot-API
Author:       Jose Ortiz Costa <jortizco@mail.sfsu.edu>
Date:         09-29-2017
Modified:     09-29-2017
Description:  After a request is done to Diffbot server and a response is retrieved by the client class,
              the content class stores all the raw response in JSON format. The content class has methods
              to serialize all the data and create the Object, Image, Videos, Tags...etc objects with
              all its fields properties

IMPORTANT:    Content data is stored in JSON format by default. The way the data is stored in the content
              class can be modified in its contructor or setters. For example data from JSON to HTML

USAGE:        # assuming we already invoked the Diffbot client
              # this will create a content object
              content = client.content(DiffbotType.Search, "our query")
              # now we can use the main proprierties or create new objects from it
              content.hits() # hits from our query
              content.api() # this will return in this case 'search api'
              content.date() # the content date
              objects = content.objects() # all the objects/pages from content
              object = content.object(0) #the page object with highest score.
"""
from pprint import pprint

from data_source.sfsu_diffbot.diffbot_apis import DiffbotApi
from data_source.sfsu_diffbot.discussion import Discussion
from data_source.sfsu_diffbot.image import Image
from data_source.sfsu_diffbot.object import Object
from data_source.sfsu_diffbot.product import Product
from data_source.sfsu_diffbot.query_info import QueryInfo
from data_source.sfsu_diffbot.video import Video


class Content(object):
    """
    Stores and creates objects from the response retrieved from a request to the Diffbot server
    """
    def __init__(self, content):
        """
        Constructor
        :param content: the response
        """
        self._content = content
        self._nextPage = 0

    def print_content(self):
        """
        print content in JSON format
        :return: VOID
        """
        pprint(self._content)

    def field(self, tag):
        """
        Retrieves a field from the content
        :param tag: the field key or tag
        :return: the field from the content
        """
        if tag in self._content:
            return self._content[tag]

    def objects(self, type = None):
        """
        Loads all the objects from the response content
        :return: the objects loaded
        """
        objects = []
        meta_objects = None
        index = 0

        if 'data' in self._content:
            meta_objects = self._content['data']
        elif 'objects' in self._content:
            meta_objects = self._content['objects']

        if meta_objects:
            for obj in meta_objects:
                objects.append(self.object_api(obj))
                index += 1
        return objects

    def object_api(self, object):
        if 'type' in object:
            if object['type'] == DiffbotApi.IMAGE:
                return Image(object)
            elif object['type'] == DiffbotApi.VIDEO:
                return Video(object)
            elif object['type'] == DiffbotApi.PRODUCT:
                return Product(object)
            elif object['type'] == DiffbotApi.DISCUSSION:
                return Discussion(object)
        return Object(object)


    def object(self, object_index):
        """
        Sets an object by index
        :param object_index:
        :return: the object
        """
        return self.objects()[object_index]

    def hits(self):
        """

        :return: the hits from the response
        """
        return self.field('hits')

    def num(self):
        """

        :return: the num of objects
        """
        return self.field('num')

    def token(self):
        """

        :return: the diffbot token
        """
        return self.field('token')

    def start(self):
        """

        :return: the index where the response started to retrieve content
        """
        return self.field('start')

    def query(self):
        """

        :return: the query
        """
        return self.field('query')

    def query_info(self):
        """

        :return: some additional info about the query
        """
        return QueryInfo(self.field('queryInfo'))

    def request(self):
        """

        :return: request info attached to the response
        """
        return self.field('request')

    def responseTime(self):
        """

        :return: the response time
        """
        return self.field('responseTimeMS')

    def totalShards(self):
        """

        :return: the total shards
        """

        return self.field('totalShards')

    def docsInCollection(self):
        """

        :return: the number of docs in the collection
        """
        return self.field('docsInCollection')

    def nextPages(self):
        """
        :return: The next pages
        """
        return self.field('nextPages')

    def nextPage(self):
        """

        :return: the next page
        """
        next_page =  self.nextPages()[self._nextPage]
        if len(self.nextPages()) < self._nextPage:
            self._nextPage+=1
        return next_page

    def docs_in_collection(self):
        """

        :return: the number of docs on the collection retrived
        """
        return self.field("docsInCollection")

    def to_string(self):
        """

        :return: the string representation of this content
        """
        return self._content










