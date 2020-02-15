"""
File:         client.py
Package:      SFSU-Diffbot-API
Author:       Jose Ortiz Costa <jortizco@mail.sfsu.edu>
Date:         09-29-2017
Modified:     09-29-2017
Description:  This file contains a Client class which performs the resquests to the Diffbot API and Diffbot
              Knoledge Graph. The content method will return all the raw data from the
              request in JSON format.

IMPORTANT:    Although an object of this class can be created directly by calling its constructor,
              It is highly recomended to invoke it from the DKG class by calling its client method. This
              method will create a valid Diffbot client.

USAGE:        diffbot = Diffbot("YOUR TOKEN") # sfsu-diffbot-api
              client = diffbot.client() # initializes a new diffbot client ready to sent request.
              # Optional: if you need to modify defaul data parameters
              param = client.get_default_param()
              param.update({'query':'your query'}}
              # Sends a request with type 'SEARCH' and retrieve the server response
              query = "(Michele Obama) AND (married to) # queries parameter supports be wildcards, text...etc
              client.update_data({images.caption:flower}) # filter query images by caption flower
              content = client.content(type=DiffbotTypes.SEARCH, query=query,print_in_console=True) # response
              # Sends a request with type 'ARTICLE' and retrieve the server response
              url = "http://wikipedia.com"
              content = client.content(type=DiffbotTypes.ARTICLE, query=url ,print_in_console=True) # response
"""
import json
import logging

import requests
from data_source.sfsu_diffbot.content import Content
from data_source.sfsu_diffbot.diffbot_apis import DiffbotApi
from data_source.sfsu_diffbot.crawlbot import CrawlBot
from data_source.sfsu_diffbot.crawlbot_actions import CrawlbotActions
import requests_cache
import time

class Client(object):
    """
    This client sends requests and proccess responses from Difbbot server
    """
    GLOBAL_INDEX = "GLOBAL-INDEX"
    EXACT_MATCH = "EXACT MATCH"
    FUZZY_MATCH = "FUZZY MATCH"
    KG_API = "Knowledge Graph"
    DIFFBOT_END_POINT = "https://api.diffbot.com"
    DIFFBOT_KG_API_END_POINT = "http://kg.diffbot.com/kg/dql_endpoint"
    DEBUG_HTTPGET_COUNT = 0
    requests_cache.install_cache('diffbot_cache')
    #requests_cache.install_cache('diffbot_cache_freebaseqa_eval')
    #requests_cache.install_cache('diffbot_cache_comqa')

    _https_session = requests.Session()

    def __init__(self, token, version = "v3", output_format="json"):
        """
        Constructor
        :param token: Diffbot token
        :param output_format: e.g json
        """
        self._data = {}
        self._custom_api = None
        self._num_results = 20
        self._start_index = 0
        self._print = False
        self._token = token
        self._output_format = output_format
        self._params = self.get_default_param()
        self._version = version
        self._doc = None
        self._query = None
        self._type = "search"
        self._api_types = [DiffbotApi.ARTICLE, DiffbotApi.SEARCH, DiffbotApi.IMAGE,
                           DiffbotApi.ANALYZE, DiffbotApi.VIDEO, DiffbotApi.PRODUCT, DiffbotApi.DISCUSSION]
        self._error_code = None
        self._error = None
        self._docsInCollection = 0
        self._query_info = None

        # Logging config
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(levelname)s %(message)s')

    def data(self):
        """

        :return: the data parameters
        """
        return self._data

    @property
    def custom_api(self):
        """

        :return: The custom api
        """
        return self._custom_api

    @custom_api.setter
    def custom_api(self, api):
        """
        sets the custom api
        :param api: the name of the custom api
        :return: VOID
        """
        if api:
            self._custom_api = api

    @property
    def endpoint(self):
        """

        :return: the end point of the api
        """
        return self._endpoint

    @endpoint.setter
    def endpoint(self, url):
        """
        Sets the endpoint of this api
        :param url:
        :return: VOID
        """
        if url:
            self._endpoint = url

    @property
    def num_results(self):
        """

        :return: the number of results taken from the response
        """
        return self._num_results

    @num_results.setter
    def num_results(self, num_results):
        """
        Sets the number of results extracted from the response
        :param num_results:
        :return: VOID
        """
        if num_results:
            self._params.update({'num': num_results})
            self._num_results = num_results

    @property
    def start_index(self):
        """

        :return: the start index. Default is 0
        """
        return self._start_index

    @start_index.setter
    def start_index(self, start_index):
        """
        Sets the start_index
        :param start_index:
        :return: VOID
        """
        if start_index:
            self._start_index = start_index

    @property
    def print_json_content(self):
        """

        :return: true if the self._print field is set to true
        """
        return self._print

    @print_json_content.setter
    def print_json_content(self, is_active):
        """
        If is_active = True, then the json responde will be printed in the console
        :param is_active:
        :return: VOID
        """
        self._print = is_active

    def get_default_param(self):
        """

        :return: the default parameters
        """
        params = {
            'token': self._token,
            'format': self._output_format,
            'num': self._num_results,
            'col': self.GLOBAL_INDEX,
            'start': self.start_index,
        }
        return params

    def article(self, url, param=None, data = None):
        """
        Api to send a request type ARTICLE
        :param url: the page url
        :param param: the extra parameters attached to the request
        :return: a response from the server in json format
        """
        return self._api(DiffbotApi.ARTICLE, url, param, data)

    def image(self, url, param=None):
        """
        Api to send a request type Image
        :param url: the page url
        :param param: the extra parameters attached to the request
        :return: a response from the server in json format
        """
        return self._api(DiffbotApi.IMAGE, url, param)

    def product(self, url, param = None):
        """
        Api to send a request type Product
        :param url: the page url
        :param data: the extra parameters attached to the request
        :return: a response from the server in json format
        """
        return self._api(DiffbotApi.PRODUCT, url, param)

    def video(self, url, param = None):
        """
        Api to send a request type Video
        :param url: the page url
        :param data: the extra parameters attached to the request
        :return: a response from the server in json format
        """
        return self._api(DiffbotApi.VIDEO, url, param)

    def discussion(self, url, param = None):
        """
        Api to send a request type Discussion
        :param url: the page url
        :param data: the extra parameters attached to the request
        :return: a response from the server in json format
        """
        return self._api(DiffbotApi.DISCUSSION, url, param)

    def custom(self, url, param = None):
        """
        Api to send a request type Product
        :param url: the page url
        :param data: the extra parameters attached to the request
        :return: a response from the server in json format
        """
        return self._api(self.custom_api, url, param)

    def crawlbot_create(self, jobName, seeds, api, param=None):
        api = Client.DIFFBOT_END_POINT+ "/" + self._version + "/" + api
        endpoint = Client.DIFFBOT_END_POINT + "/v3/crawl"
        self._params.update({'name': jobName})
        params_seed = None
        for seed in seeds:
            if params_seed:
               params_seed = params_seed + " " + seed
            else:
               params_seed = seed
        self._params.update({'seeds': params_seed})
        self._params.update({'apiUrl': api})
        request = requests.get(endpoint, params=self._params)
        content = json.loads(request.content.decode('utf-8'))
        if 'error' in content:
            self._error = content['error'];
            self._error_code = content['errorCode']
        response = CrawlBot(content)
        return response



    def _crawlbot_action(self, name, action, value):
        endpoint = Client.DIFFBOT_END_POINT + "/" + self._version + "/crawl"
        self._params.update({action:value})
        request = requests.get(endpoint, params=self._params)
        content = json.loads(request.content.decode('utf-8'))
        if 'error' in content:
            self._error = content['error'];
            self._error_code = content['errorCode']
        response = CrawlBot(content)
        return response

    def crawlbot_roundStar(self, name):
        return self._crawlbot_action(name, CrawlbotActions.ROUND_START, 1)

    def crawlbot_restart(self, name):
        return self._crawlbot_action(name, CrawlbotActions.RESTART, 1)

    def crawlbot_pause(self, name, action=1):
        return self._crawlbot_action(name, CrawlbotActions.PAUSE, action)

    def crawlbot_delete(self, name, action=1):
        return self._crawlbot_action(name, CrawlbotActions.DELETE, 1)

    def crawlbot_get_data(self, name, format='json', parameters=None):
        endpoint = Client.DIFFBOT_END_POINT + "/" + self._version + "/crawl/data"
        data = {'name': name, 'format':format}
        for key, value in parameters.items():
            data.update({key:value})
        return self.search(endpoint, None, data)

    def analyze_api(self, url, parameters=None):
        return self._api('analyze', url, parameters)

    def print_parameters(self):
        """
        Prints the parameters attached to the request
        :return: VOID
        """
        print(self._params)

    def prepare_kg_request(self, query, param = None, data={'orderBy':'timestamp'}):
        """
                Api that sends a request to the server of type SEARCH
                :param query: the query
                :param data: the request attached parameters
                :return: the response from the server in json format
                """
        endpoint = Client.DIFFBOT_KG_API_END_POINT
        query_builder = ""

        if query:
            subject_type = query[1].lower().capitalize()
            if subject_type == 'Location':
                subject_type = 'Place'
            query_builder = "type:{} ".format(subject_type)
            query_builder += "allNames:\"{}\"".format(query[0])

        if param:
            for key, value in param.items():
                query_builder += (" " + key + ":" + str(value))

        self._params.update({'query': query_builder})
        #print("Diffbot Query: {}".format(query_builder))
        if data:
            for key, value in data.items():
                self._params.update({key: value})

        self._params.update({"num": "3"})
        self._params.update({"type": "query"})

        return endpoint

    def prepare_gi_request(self, query, param = None, data={'orderBy':'timestamp'}, search_type=EXACT_MATCH):
        """
                Api that sends a request to the server of type SEARCH
                :param query: the query
                :param data: the request attached parameters
                :return: the response from the server in json format
                """
        endpoint = Client.DIFFBOT_END_POINT + "/" + self._version + "/search"
        #endpoint = "http://kg.diffbot.com/kg/dql_endpoint"
        query_builder = ""
        if search_type == Client.EXACT_MATCH:
            STRING_DELIMITER = "\""
            if query:
                for i, token in enumerate(query):
                    query_builder += 'text:'
                    query_builder += STRING_DELIMITER + token + STRING_DELIMITER
                    if i < len(query) - 1:
                        query_builder += " AND "
        else:
            STRING_DELIMITER = "'"
            if query:
                query_builder += 'text:'
                query_builder += STRING_DELIMITER
                query_builder += " ".join(query)
                query_builder += STRING_DELIMITER

        if param:
            for key, value in param.items():
                query_builder += (" " + key + ":" + str(value))
        self._params.update({'query': query_builder})
        #print("Diffbot Query: {}".format(query_builder))
        if data:
            for key, value in data.items():
                self._params.update({key: value})

        self._params.update({"num": str(self._num_results)})
        #self._params.update({"type": "query"})

        return endpoint

    def kg_search(self, named_entity):
        return self.simple_search(named_entity, search_api=self.KG_API)

    def simple_search(self, query, search_api=GLOBAL_INDEX, search_type=EXACT_MATCH, param = None, data={'orderBy':'timestamp'}):
        if search_api is self.GLOBAL_INDEX:
            endpoint = self.prepare_gi_request(query, param, data, search_type)
        elif search_api is self.KG_API:
            endpoint = self.prepare_kg_request(query, param, data)
        else:
            Exception("invalide seach api: {}".format(search_api))
            exit(1)

        Client.DEBUG_HTTPGET_COUNT = Client.DEBUG_HTTPGET_COUNT + 1
        logging.debug("HTTP GET Count={}".format(Client.DEBUG_HTTPGET_COUNT))

        try:
            request = Client._https_session.get(endpoint, params=self._params)
            content = json.loads(request.content.decode('utf-8'))
        except Exception as inst:
            if type(inst) == json.decoder.JSONDecodeError:
                print("JSONDecodeError occurred: {}".format(inst.msg))
                return None
            else:
                print("Diffbot connection was reset, trying again in 10 seconds...")
                time.sleep(10)
                # try again
                request = Client._https_session.get(endpoint, params=self._params)
                content = json.loads(request.content.decode('utf-8'))

        if 'error' in content:
            self._error = content['error']
            self._error_code = content['errorCode']
        response = Content(content)

        # TODO: need to figure out a way to limit the number of returned results similar to GLOBAL_INDEX API.
        # for now, harcoding to using max of 3 objects from returned results
        if search_api is self.KG_API:
            if len(response._content['data']) > 3:
                response._content['data'] = response._content['data'][0:3]

        self._docsInCollection = response.docsInCollection()
        self._query_info = response.query_info()
        return response

    def search(self, query, param = None, data={'orderBy':'timestamp'}):
        """
        Api that sends a request to the server of type SEARCH
        :param query: the query
        :param data: the request attached parameters
        :return: the response from the server in json format
        """
        endpoint = Client.DIFFBOT_END_POINT + "/" + self._version + "/search"
        query_builder = ""
        if query:
            if "\"" in query: # takes care of queries with the AND equivalent for example: president AND "Barank Obama"
                for token in query.split("\""):
                    t = token.strip().split()
                    if len(t)  > 1:
                       for i in t:
                           query_builder += 'title:' + i + " "
                    else:
                        query_builder += token + " "
            else:
                query_builder = query
            self._query = query_builder.lower()
        if param:
            for key, value in param.items():
                query_builder += (" " + key + ":" + str(value))
        self._params.update({'query':"sortby:timestamp " + query_builder})
        if data:
            for key, value in data.items():
                self._params.update({key:value})

        Client.DEBUG_HTTPGET_COUNT = Client.DEBUG_HTTPGET_COUNT + 1
        logging.debug("HTTP GET Count={}".format(Client.DEBUG_HTTPGET_COUNT))

        try:
            request = Client._https_session.get(endpoint, params=self._params)
            content = json.loads(request.content.decode('utf-8'))
        except:
            print("Diffbot connection was reset, trying again in 10 seconds...")
            time.sleep(10)
            # try again
            request = Client._https_session.get(endpoint, params=self._params)
            content = json.loads(request.content.decode('utf-8'))

        if 'error' in content:
            self._error = content['error']
            self._error_code = content['errorCode']
        response = Content(content)
        self._docsInCollection = response.docsInCollection()
        self._query_info = response.query_info()
        return response

    def _api(self, type, url, param, data):
        """
        :param url: the image url
        :param optional_fields: optional fields. see the complete list here https://www.diffbot.com/dev/docs/image/
        :return: the image object content
        """
        try:
            endpoint = Client.DIFFBOT_END_POINT + "/" + self._version + "/"
            if type in self._api_types:
                if type == DiffbotApi.CRAWL:
                    endpoint+=type+"/data"
                endpoint+=type
            if param:
                for key, value in param:
                    self._params.update({key : value})
            if data:
                for key, value in data.items():
                    self._params.update({key: value})
            self._params.update({'url': url})

            Client.DEBUG_HTTPGET_COUNT = Client.DEBUG_HTTPGET_COUNT + 1
            logging.debug("HTTP GET Count={}".format(Client.DEBUG_HTTPGET_COUNT))

            request = Client._https_session.get(endpoint, params=self._params)
            content = json.loads(request.content)
            if 'error' in content:
                self._error = content['error'];
                self._error_code = content['errorCode']
            response =  Content(content)
            self._docsInCollection = response.docsInCollection()
            self._query_info = response.query_info()
            return response
        except:
            logging.warning("Response failed. For more info about this error, check the logs")

    def main_tag(self, content, field_key):
        """

        :param content: the server response
        :param tag: the main field key to retrieve the valu e.g: hits
        :return: the value of the field_key specified from the response
        """
        return content[field_key]

    def objects(self, content):
        """

        :param content: the response from the server
        :return: the objects in the response
        """
        if 'data' in content:
            return content['data']
        elif 'objecdts' in content:
            return content['objects']
        else:
            return None

    def object_tag(self, content, object_index, field_key):
        """

        :param content: the response from the server
        :param object_index: the index of the object in the response
        :param field_key: the key from the response fields
        :return: the value from the response stored on its field key
        """
        return self.objects(content)[object_index][field_key]

    def test_connection(self):
        """
        Performs a dummy request to Diffbot server to test if the connection with this client is alive.
        Its prints the connection test results on terminal.
        :return: VOID
        """
        self.search("")
        if self._error and self._error_code:
            logging.error("Connection Failed with error code: ", self._error_code)
            logging.error("Error description: ", self._error)
        else:
            logging.info("Connected successfully to Diffbot server. Conection code: ", 200)

    def tag_data(self, tag):
        """
        Executes the article extraction API to retrieve data from a tag object
        :param tag: the tag object
        :return: the data about the tag, then you can call all its properties to retrieve specific data e,g tag.text()
        """
        res_tags = self.article(tag.uri())
        tag = res_tags.objects()[0]
        return tag

    def query_comparasion(self, query1, query2):
        res1 = self.search(query1)
        res2 = self.search(query2)
        return res1.hits(), res2.hits()

    def query_info(self):
        if self._query_info:
            return self._query_info


    def numDocsInCollection(self):
        if self._docsInCollection:
            return self._docsInCollection

    def client_instance(self):
        return "dkg"






