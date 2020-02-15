"""
File:         dkg.py
Package:      SFSU-Diffbot-API
Author:       Jose Ortiz Costa <jortizco@mail.sfsu.edu>
Date:         09-29-2017
Modified:     09-29-2017
Description:  Entry point to the sfsu-diffot-API. It builds the diffbot client and checks out token authorization

IMPORTANT:    A valid diffbot token is necessary to access to all the API features.

USAGE:        token = "your token"
              sfsu_diffbot_api = dkg(token) # invokes the sfsu diffbot API
              client = sfsu_diffbot_api.client() # creates the client.

"""
from data_source.sfsu_diffbot.client import Client
class Diffbot(object):
    """
    SFSU Diffbot API entry point
    """
    def __init__(self, token):
        """
        Constructor
        :param token: a valid diffbot token
        """
        self._token = token

    def client(self):
        """
        Creates a new SFSU diffbot API client
        :return: the SFSU diffbot API client
        """
        return Client(self._token)


