"""
File:         diffbot_api.py
Package:      SFSU-Diffbot-API
Author:       Jose Ortiz Costa <jortizco@mail.sfsu.edu>
Date:         09-29-2017
Modified:     09-29-2017
Description:  This file contains all the types allowed by Diffbot api

USAGE:        search_type = DiffbotTypes.SEARCH
"""


class DiffbotApi():
    """
    Constants representing valids diffbot types apis
    """
    SEARCH = "search" # search api
    ARTICLE = "article" # article api
    IMAGE = "image"
    VIDEO = "video"
    ANALYZE = "analyze"
    PRODUCT = "product"
    DISCUSSION = "discussion"
    CRAWL      = "crawl"
