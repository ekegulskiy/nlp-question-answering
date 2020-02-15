"""
File:         video.py
Package:      SFSU-Diffbot-API
Author:       Jose Ortiz Costa <jortizco@mail.sfsu.edu>
Date:         09-29-2017
Modified:     09-29-2017
Description:  This file contains the object Video which represents a video from a object/page response and it has methods
              to access to all its properties.

IMPORTANT:    Videos objects comes from Objects and Videos api

USAGE:        # from object content
              object = content.object(0)
              videos = object.videos() # all the videos from the object
              video = object.video(0) # first video object from the object Object
              video.url() # url pointing to the videp

              # from Video api (will be implemented in future versions)

"""
class Video(object):
    """
    Video class and all its properties
    """
    def __init__(self, video_content):
        """
        Constructor
        :param video_content: the video metadata content
        """
        self._video_content = video_content

    def _field(self, key):
        """

        :param key: the field key
        :return: the value stored on the field
        """
        if key in self._video_content:
            return self._video_content[key]

    def diffbotUri(self):
        """

        :return: the diffbot uri
        """
        return self._field('diffbotUri')

    def is_primary(self):
        """

        :return: True if the video is primary. Otherwise, false.
        """
        return self._field('primary')

    def url(self):
        """

        :return: The url pointing to the video
        """
        return self._field('url')

    def duration(self):
        return self._field('duration')


    def pageUrl(self):
        """

        :return: The page url pointing to the video
        """
        return self._field('pageUrl')

    def html(self):
        """

        :return: The html pointing to the video
        """
        return self._field('html')

    def title(self):
        """

        :return: The title pointing to the video
        """
        return self._field('title')


    def date(self):
        """

        :return: The date pointing to the video
        """
        return self._field('date')

    def viewCount(self):
        return self._field('viewCount')

    def mime(self):
        """

        :return: The mime pointing to the video
        """
        return self._field('mime')

    def naturalHeight(self):
        """

        :return: The height pointing to the video
        """
        return self._field('naturalHeight')

    def naturalWidth(self):
        """

        :return: The width pointing to the video
        """
        return self._field('naturalWidth')

    def type(self):
        """

        :return: The type pointing to the video
        """
        return self._field('type')

    def meta_data(self):
        return self._video_content

