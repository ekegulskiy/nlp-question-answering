"""
File:         diffbot_api.py
Package:      SFSU-Diffbot-API
Author:       Jose Ortiz Costa <jortizco@mail.sfsu.edu>
Date:         09-29-2017
Modified:     09-29-2017
Description:  This file contains all the types allowed by Diffbot api

USAGE:        search_type = DiffbotTypes.SEARCH
"""


class CrawlbotActions():
    """
    Constants representing valids diffbot types apis
    """
    PAUSE = "pause"
    ROUND_START = "roundStart"
    RESTART = 'restart'
    DELETE = 'delete'