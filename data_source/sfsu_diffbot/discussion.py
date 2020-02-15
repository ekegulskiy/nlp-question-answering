"""
File:         discussion.py
Package:      SFSU-Diffbot-API
Author:       Jose Ortiz Costa <jortizco@mail.sfsu.edu>
Date:         09-29-2017
Modified:     09-29-2017
Description:  This file contains a object representation of a disccusion api extracted from the diffbot knoledge graph

USAGE:        # from object content
              url = "discussion url"
              discussion = client.discussion_content(url)
"""
from data_source.sfsu_diffbot.post import Post

from data_source.sfsu_diffbot.tag import Tag


class Discussion(object):
    """
    Discussion class
    """
    def __init__(self, discussion_metadata):
        """
        Constructor
        :param discussion_metadata:
        """
        self._discussion = discussion_metadata

    def _field(self, key):
        return self._discussion[key]

    # public properties
    def type(self):
        if 'type' in self._discussion:
            return self._field('type')

    def pageUrl(self):
        if 'pageUrl' in self._discussion:
            return self._field('pageUrl')

    def title(self):
        if 'title' in self._discussion:
            return self._field('title')

    def numPost(self):
        if 'numPost' in self._discussion:
            return self._field('numPost')

    def tags(self):
        """

        :return: the object's tags
        """
        if 'tags' in self._discussion:
            tags = []
            tags_dict = self._field('tags')
            tags_dict.pop('_keys', None)
            for key, value in tags_dict.items():
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
        if self.tags():
            return sorted(self.tags(), key=lambda x: x.score(), reverse=descending_order)

    def tags_sorted_by_count(self, descending_order = True):
        """

        :param descending_order: If True, the tags will be returned in descending order sorted by count
        :return: the tags objects sorted by count
        """
        if self.tags():
            return sorted(self.tags(), key=lambda x: x.count(), reverse=descending_order)

    def participants(self):
        if 'participants' in self._discussion:
            return self._field('participants')

    def nextPages(self):
        if 'nextPages' in self._discussion:
            return self._field('nextPages')

    def nextPage(self):
        if 'nextPage' in self._discussion:
            return self._field('nextPage')

    def humanLanguage(self):
        if 'humanLanguage' in self._discussion:
            return self._field('humanLanguage')

    def posts(self):
        if 'posts' in self._discussion:
            posts_list = []
            posts = self._field('posts')
            for post in posts:
                posts_list.append(Post(post))
            return posts_list

    def post(self, index):
        return self.posts()[index]

    def confidence(self):
        if 'confidence' in self._discussion:
            return self._field('confidence')

    def to_str(self):
        return self._discussion

    def meta_data(self):
        return self._discussion



