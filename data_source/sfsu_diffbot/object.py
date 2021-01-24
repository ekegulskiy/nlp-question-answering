"""
File:         object.py
Package:      SFSU-Diffbot-API
Author:       Jose Ortiz Costa <jortizco@mail.sfsu.edu>
Date:         09-29-2017
Modified:     09-29-2017
Description:  This file contains the class Object which represents an object/page from the Diffbot Knoledge
              Graph, including all its properties such as title, tags, images, videos....etc

IMPORTANT:    A content response may have several objects
              The Object class has also methods to analyze its own properties such us computing tf for a term
              in the document, and much more.....
              An Object can represent pages,images,videos depending on the api used to do the search. For example,
              a 'search' api will return objects representing pages ( which also has images, videos, tags...etc objects)
              a 'image' api will return objects representing images.

USAGE:        # assuming we already invoked the Diffbot client and already created its content response
              objects = content.objects() # all the objects from the response
              object = content.object(0) # first object in the response content ( the highest scored object)
              # some of its properties
              object.author()
              object.url()
              object.tags()
              object.images()
              object.videos()
              object.documentId()
"""
from data_source.sfsu_diffbot.diffbot_apis import DiffbotApi
from data_source.sfsu_diffbot.image import Image
from data_source.sfsu_diffbot.tag import Tag
from data_source.sfsu_diffbot.video import Video
from data_source.data_source_object import *


class Object(DataSourceObject):
    """
    Object class representing an object from the content response and all its properties
    """
    def __init__(self, object, encapsulate=False, client=None):
        """
        Constructor
        :param object: the object metadata
        """
        super(Object, self).__init__(object)
        self._nextPage = 0
        self._encapsulate = encapsulate
        self._client = client


    def init_object_by_type(self):
        if self.type() == DiffbotApi.IMAGE:
            return Image(self._object)
        return self._object

    def encapsulate(self):
        if self._encapsulate:
            tags = self.tags_sorted_by_score()
            response = self._client.article(tags[0].uri())
            return self.title() + " " + self.text() + " " + response.objects()[0].text()

    def title(self):
        """

        :return: the title of the object
        """
        if 'title' in self._object:
            return self.object_value('title')

    def text(self):
        """

        :return: the text of the object
        """
        if 'text' in self._object:
            return self.object_value('text')

    def url(self):
        """

        :return: the url of the object
        """
        if 'pageUrl' in self._object:
            return self.object_value('pageUrl')

    def html(self):
        """

        :return: the html text of the object
        """
        if 'html' in self._object:
            return self.object_value('html')

    def tags(self):
        """

        :return: the object's tags
        """
        tags = []
        if 'tags' in self._object:
            tags_dict = self.object_value('tags')
            if len(tags_dict) > 0:
                if '_keys' in tags_dict:
                    tags_dict.pop('_keys', None)
                if isinstance(tags_dict, dict):
                    for key, value in tags_dict.items():
                        tags.append(Tag(value))
                elif isinstance(tags_dict, list):
                    for value in tags_dict:
                        tags.append(Tag(value))
        return tags

    def tag(self, index):
        """

        :param index: the index of the tag object in the content
        :return: the object
        """
        return self.tags()[index]

    def tags_sorted_by_score(self, descending_order = True):
        """

        :param descending_order: If True, the tags will be returned in descending order sorted by score
        :return: the tags objects sorted by score
        """
        return sorted(self.tags(), key=lambda x: x.score(), reverse=descending_order)

    def tags_sorted_by_count(self, descending_order = True):
        """

        :param descending_order: If True, the tags will be returned in descending order sorted by count
        :return: the tags objects sorted by count
        """
        return sorted(self.tags(), key=lambda x: x.count(), reverse=descending_order)

    def date(self):
        """

        :return: the object date. Note that the object may have been cached
        """
        if 'date' in self._object:
            return self.object_value('date')

    def type(self):
        """

        :return: the object type
        """
        if 'type' in self._object:
            return self.object_value('type')

    def author(self):
        """

        :return: the author of the object ( if any ). Otherwise, returns None
        """
        if 'author' in self._object:
            return self.object_value('author')


    def videos(self):
        """

        :return: the videos extracted from the object
        """
        videos_content = []
        if 'videos' in self._object:
            videos = self.object_value('videos')
            for video in videos:
                videos_content.append(Video(video))
            return videos_content

    def video(self, index):
        """

        :param index: index of the video in the object response
        :return: the video object and all its properties
        """
        return self.videos()[index]

    def images(self):
        """

        :return: the images objects and all its properties
        """
        if 'images' in self._object:
            images_content = []
            images = self.object_value('images')
            for image in images:
                images_content.append(Image(image))
            return images_content

    def image(self, index):
        """

        :param index: the index of the image from the object response
        :return: the image object and all its properties
        """
        return self.images()[index]

    def diffbotUri(self):
        """

        :return: the diffbot uri of the object
        """
        if 'diffbotUri' in self._object:
            return self.object_value('diffbotUri')

    def links(self):
        """

        :return: A list of links from the object
        """
        if 'links' in self._object:
            return self.object_value('links')

    def meta(self):
        """

        :return: the object metadata
        """
        if 'meta' in self._object:
            return self.object_value('meta')

    def sentiment(self):
        """

        :return: the object sentiment score
        """
        if 'sentiment' in self._object:
            return self.object_value('sentiment')

    def siteName(self):
        """

        :return: the object/site name
        """
        if 'siteName' in self._object:
            return self.object_value('siteName')

    def lastCrawTimeUTC(self):
        """

        :return: Last time when the object was crawed
        """
        if 'lastCrawTimeUTC' in self._object:
            return self.object_value('lastCrawTimeUTC')

    def documentId(self):
        """

        :return: the document id
        """
        if 'docId' in self._object:
            return self.object_value('docId')

    def gburl(self):
        """

        :return: the gb url
        """
        if 'gburl' in self._object:
            return self.object_value('gburl')

    def humanLanguage(self):
        """

        :return: the language model of the object. e.g. English
        """
        if 'humanLanguage' in self._object:
            return self.object_value('humanLanguage')
        else:
            return 'en'

    def icon(self):
        """

        :return: the icon of the object
        """
        if 'icon' in self._object:
            return self.object_value('icon')



    def publisherCountry(self):
        if 'publisherCountry' in self._object:
            return self.object_value("publisherCountry")

    def to_string(self):
        """

        :return: the string representation of the object in JSON format
        """
        return self._object

    def timestamp(self):
        if 'timestamp' in self._object:
            return self.object_value('timestamp')

    def nextPages(self):
        if 'nextPages' in self._object:
            return self.object_value('nextPages')

    def nextPage(self):
        page = self.nextPages()[self._nextPage]
        self._nextPage+=1
        return page

    def estimatedDate(self):
        if 'estimatedDate' in self._object:
            return self.object_value('estimatedDate')

    def meta_data(self):
        return self._object













