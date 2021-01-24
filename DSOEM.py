"""
This file implements the Data Source Object Extraction Module (DSOEM)

Package: fqakg

Author: Jose Ortiz
        Eduard Kegulskiy
"""
import math
from data_source.google_kg_client.GKGAPI import GKGAPI
from data_source.sfsu_diffbot.sfsu_diffbot_client import *
import logging
from urllib.parse import urlparse
from os.path import splitext
from QPM import QuestionType
from colorama import init
init() # colorama needed for Windows
from colorama import Fore, Back, Style

class DSOEM(object):
    """
    DSOEM will take as input the set of multiple queries gerenated by FMQFM module, and return high quality objects
    from the selected Data Source
    """

    def __init__(self, mqfm, kg_instance="dkg", api_key = None, qpm=None):
        """
            DSOEM constructor
        :param mqfm: FMQFM object
        :param kg_instance: data source kg object (supported values are 'dkg' and 'gkg' - representing Diffbot and Google KG)
        :param api_key: api token to be used when calling data source APIs
        :param qpm: QPM object
        """
        print("")
        self.log("{}MODULE 3: DATA SOURCE OBJECT EXTRACTION MODULE{}".format(Style.BRIGHT, Style.RESET_ALL))

        self._mqfm = mqfm
        self._qpm = qpm
        self._server = kg_instance
        self._api_key = api_key
        self._client = self.get_client()
        self._response = None
        self._query = self._qpm.query()
        self._uris = []
        self._hits = 0
        self._best_query = self._query
        self._objects_added = []
        self._max_num_objects = 30
        self._client.num_results = self._max_num_objects
        self._data = None
        self._kg_data = None

        if self._mqfm is not None:
            self._multiqueries = self._mqfm.multiquery()
        else:
            self._multiqueries = None

        self._best_basiline_object = None
        self._num_objects = []
        self._original_q = self._qpm.free_text()
        self._labeled_answer = self._qpm.labeled_answer()

        self._data = self.encapsulate_objects(with_tags=False)

        if self._qpm.question_type.value is QuestionType.SimpleFact.value and self._qpm.question_named_entities:
            self._kg_data = self.encapsulate_objects_from_kg()

    def log(self, text):
        print("[{}] {}".format(DSOEM.__qualname__, text))

    def get_data_objects(self):
        return self._data

    def get_kg_data_objects(self):
        return self._kg_data

    def original_question(self):
        return self._original_q

    def labeled_answer(self):
        return self._labeled_answer

    def get_client(self):
        """
        
        :return: The Data Source instance client
        """
        client = None
        if self._server == "dkg":
            client = Diffbot(self._api_key).client()
        elif self._server == "gkg":
            client = GKGAPI(self._api_key)
            client.set_queries(["world wide web"])
        return client

    def objects(self, response):
        """

        :param response: response from data source
        :return: objects containing the results
        """
        return response.objects()

    def is_valid_text(self, object):
        """
            validates single object with search results from the data source using the following logic:
            1. Checks if the source document is code (such as JavaScript). If yes, invalidates this object
            2. Checks if the source document is long list of short words. If yes, invalidates this object
            3. If above 2 are false, object is considered valid

        :param object: object received from the data source
        :return: whether a give object has valid/useful text for finding an answer to user question
        """
        url = object.url()
        path = urlparse(url).path
        ext = splitext(path)[1]
        if ext == ".js":
            return False

        text = object.text()
        if text is not None and text != "":
            num_new_lines = text.count("\n")
            if num_new_lines == 0:
                num_new_lines = 1

            num_tokens = len(text.split())
            average_token_len = len(text)/num_tokens
            if average_token_len < 30 and num_tokens/num_new_lines > 3:
                return True
            else:
                return False
        else:
            return False

    def encapsulate_objects_from_kg(self):
        """
            Uses KG APIs to query Data Source about all entities detected in user question
        :return: list of retreived objects
        """
        encapsulated_objects = []
        if self._qpm.question_type.value is QuestionType.SimpleFact.value and self._qpm.question_named_entities:
            for named_entity in self._qpm.question_named_entities:
                obj_data = self._encapsulate_objects_kg_helper(named_entity)

                for object in obj_data:
                    if len(encapsulated_objects) < self._max_num_objects:
                        encapsulated_objects.append((object, named_entity))

        return encapsulated_objects

    def _contains_query_grams(self, object, query_grams):
        object_text = object.text().lower()

        for gram in query_grams:
            if object_text.find(gram.lower()) == -1:
                DSOEM.kg_diffbot_match_error += 1
                return False

        return True


    def encapsulate_objects_mq(self, with_tags=True):
        """
        Encapulates objects 
        :param with_tags: 
        :return: 
        """

        def not_duplicate(object):
            for o in encapsulated_objects:
                if object.url().replace('https://', '').replace('http://', '') ==\
                   o[0].url().replace('https://', '').replace('http://', ''):
                    return False

            return True

        encapsulated_objects = []
        multiqueries = self._multiqueries

        for index, query in enumerate(multiqueries):
            if len(encapsulated_objects) >= self._max_num_objects:
                break  # limit to self._max_num_objects
            obj_data = self._encapsulate_objects_mq_helper(query[0], with_tags)

            for object in obj_data:
                if len(encapsulated_objects) < self._max_num_objects and self.is_valid_text(object) and\
                        not_duplicate(object): # and self._contains_query_grams(object, query[0]):
                    encapsulated_objects.append((object, query[2], query[0]))

        return self._best_query, encapsulated_objects

    def encapsulate_objects(self, with_tags=True):
        """
        Encapulates objects
        :param with_tags:
        :return:
        """
        encapsulated_objects = []
        multiqueries = self._multiqueries
        if multiqueries is not None:
            return self.encapsulate_objects_mq(with_tags)

        if self._server == "dkg":
            obj_data = self._encapsulate_objects_helper(self._query, with_tags)
            for object in obj_data:
                encapsulated_objects.append(object)
        elif self._server == "gkg":
           encapsulated_objects = self.gkg_objects(self.multiquery())
        return self._best_query, encapsulated_objects

    def gkg_objects(self, queries):
        """
        
        :param queries: 
        :return: google knowledge graphs objects
        """
        raw_queries = []
        for q in queries:
            raw_queries.append(" ".join(q[0]))

        # remove duplicates
        raw_queries = list(set(raw_queries))

        self._client.set_queries(raw_queries)
        objects = self._client.objects()
        return objects

    def _encapsulate_objects_helper(self, query, include_tags):
        """
        Encapsulates objects from a single query
        :param query:
        :param include_tags:
        :return: A list of encapsulated objects
        """

        def non_empty_string(s):
            return isinstance(s, str) and not s.isspace() and s != ''

        objects_list = []
        main_response = self._client.simple_search(query.split())
        hits = main_response.hits()
        objects = main_response.objects()
        last_score = 0
        num_objects = 0
        objs = []
        if len(objects) > 0:
            if hits > self._hits and query != self._query:
                self._best_query = query
                self._hits = hits
            for object in objects:
                if hasattr(object, 'text') and non_empty_string(object.text()) and object.humanLanguage() == 'en':
                    num_objects += 1
                    objects_list.append(object)
                    if include_tags:
                        tags = object.tags_sorted_by_score()
                        if len(tags) > 0:
                            for tag in tags:
                                logging.debug(tag.label())
                                logging.debug(tag.score())
                                for token in self.query().split():
                                    uri = tag.uri()
                                    if token in tag.uri() and uri not in self._uris:
                                        response = self._client.article(uri)
                                        if response is not None:
                                            objs = response.objects()
                                        if len(objs) > 0:
                                            tag_obj = objs[0]
                                            if hasattr(tag_obj, 'text'):
                                                self._uris.append(uri)
                                                objects_list.append(tag_obj)
            self._num_objects.append(num_objects)
        return objects_list

    def _encapsulate_objects_kg_helper(self, named_entity):
        objects_list = []
        num_objects = 0
        main_response = self._client.kg_search(named_entity)
        if self._server == "gkg":
            objects = main_response
        else:
            objects = main_response.objects()

        for object in objects:
            objects_list.append(object)
            num_objects += 1

        self._num_objects.append(num_objects)
        return objects_list

    def _encapsulate_objects_mq_helper(self, query, include_tags):
        """
        Encapsulates objects from a single query
        :param query: 
        :param include_tags: 
        :return: A list of encapsulated objects 
        """
        objects_list = []
        main_response = self._client.simple_search(query)
        if main_response is None:
            return []
        hits = main_response.hits()
        objects = main_response.objects()
        last_score = 0
        num_objects = 0
        objs = []
        if len(objects) > 0:
            if hits > self._hits and query != self._query:
                self._best_query = query
                self._hits = hits
            for object in objects:
                if hasattr(object, 'text') and hasattr(object,
                                                       'url') and object.url() not in self._objects_added and object.humanLanguage() == 'en':
                    self._objects_added.append(object.url())
                    num_objects += 1
                    objects_list.append(object)
                    if include_tags:
                        tags = object.tags_sorted_by_score()
                        if len(tags) > 0:
                            for tag in tags:
                                logging.debug(tag.label())
                                logging.debug(tag.score())
                                for token in self.query().split():
                                    uri = tag.uri()
                                    if token in tag.uri() and uri not in self._uris:
                                        response = self._client.article(uri)
                                        if response is not None:
                                            objs = response.objects()
                                        if len(objs) > 0:
                                            tag_obj = objs[0]
                                            if hasattr(tag_obj, 'text'):
                                                self._uris.append(uri)
                                                objects_list.append(tag_obj)
            self._num_objects.append(num_objects)
        return objects_list

    def confidence(self, object):
        """
        Computes the confidence score
        :param object: 
        :return: the confidence score
        """
        confidence_count = 0
        if hasattr(object, "text"):
            text = object.text()
            grams = self._mqfm.grams()
            for gram in grams:
                if gram in text:
                    confidence_count += 1
            return confidence_count / len(grams)
        else:
            return 0.00

    def number_objects_list(self):
        return self._num_objects

    def query(self):
        return self._query

    def multiquery(self):
        return self._mqfm.multiquery()

    def best_query(self):
        return self._best_query

    def tf(sekf, word, blob):
        """
        
        :param word: 
        :param blob: a blob object 
        :return: the term frequency of the word 
        """
        return blob.count(word) / len(blob.split())

    def n_containing(self, word, bloblist):
        return sum(1 for blob in bloblist if word in blob.split())

    def idf(self, word, bloblist):
        return math.log(len(bloblist) / (1 + self.n_containing(word, bloblist)))

    def tfidf(self, word, blob, bloblist):
        return self.tf(word, blob) * self.idf(word, bloblist)

    def instance(self):
        return self._server
