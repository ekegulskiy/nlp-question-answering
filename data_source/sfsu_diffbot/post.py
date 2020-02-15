"""
File:         post.py
Package:      SFSU-Diffbot-API
Author:       Jose Ortiz Costa <jortizco@mail.sfsu.edu>
Date:         09-29-2017
Modified:     09-29-2017
Description:  This file contains a object representation of post extracted from discussion api

IMPORTANT:    Posts objects comes from Discussion api

USAGE:        url = "discussion url"
              discussion = client.discussion_content(url)
              # extract multiple posts
              posts = discussion.posts()
              from post in posts:
                 post.author()
              # single post
              post = discussion.post(0) # the best scored post

"""
class Post(object):
    """
    Post class
    """
    def __init__(self, post_metadata):
        self._post = post_metadata
    def _field(self, key):
        if key in self._post:
            return self._post[key]

    def author(self):
        return self._field('author')

    def authorUrl(self):
        return self._field('authorUrl')

    def humanLanguage(self):
        return self._field('humanLanguage')

    def html(self):
        return self._field('html')

    def id(self):
        return self._field('id')

    def text(self):
        return self._field('text')

    def type(self):
        return self._field('type')

    def title(self):
        return self._field('title')

    def meta_data(self):
        return self._post

