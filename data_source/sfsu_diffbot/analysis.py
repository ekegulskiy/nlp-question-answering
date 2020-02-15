"""
File:         analysis.py
Package:      sfsu_diffbot
Author:       Jose Ortiz Costa <jortizco@mail.sfsu.edu>
Date:         09-29-2017
Modified:     09-29-2017
Description:  This file contains some usefull methods to analyze the data returned from the sfsu_diffbot_client

IMPORTANT:    spacy module needs to be installed. 'pip install spacy'

USAGE:        # assuming that an object is already extracted from the sfsu diffbot client response
              from sfsu_diffbot.analysis import Analyze
              analyzer = Analyze(object, 'title', type='article', model='en') # type and model are optionals
              # term semantics info from the field title of the object passed on the constructor
              analyzer.term_semantics() # prints term, tag, pos, lemma, dep and head of every term
              # for individual terms
              tag = analyzer.term_sematic(term) # term can be string or spacy object
              # similarity between 2 terms
              similarity = analyzer.similarity(term1, term2) # similarity score -- term1 and term2 are strings or spacy objects
              # most similar terms or synomims
              most_similar_terms = analyzer.most_similar(term) # optional # of results, default is 10
              for similar_term in most_similar_terms:
                print(similar_term.text) # you can also apply all the tag, dep....etc to the results

"""

import spacy
import math
import sys
class Analyze(object):
    """
    Tools to analyze
    """
    def __init__(self, client, object = None, field = None, type = None, model='en'):
        """
        Constructor
        :param object: a object extracted from a response from sfsu diffbot client
        :param field: e.g 'text', 'title', 'author'..... -- field must be a string
        :param type:  optional --- default is 'article'
        :param model: optional -- default is English model 'en'
        """
        if object:
            self._object = object
            self._field = field
            self._type = type
            self._model = self.model(model)
            self._doc = self.doc(field)
        self._client = client
        self._model = spacy.load("en")


    def model(self, model = "en"):
        """
        Sets the model -- default is English language 'en'
        :param model:
        :return: the model
        """
        return spacy.load(model)

    def doc(self, field, is_meta_data = True):
        """
        Builts the doc
        :param field: 'text', 'title'....etc
        :param is_meta_data: optional -- default is True
        :return:
        """
        doc = None
        meta = self._object.meta_data()
        if is_meta_data == True and field in meta:
           item = meta[field]
           doc = self._model(item)
        return doc

    def terms_semantics(self):
        """

        :return: the semantics of the terms in the field e.g tag, dep, lemma...etc
        """
        for term in self._doc:
            self.term_semantic(term)

    def term_semantic(self, term):
        print("Term: ", term)
        print("Term tag", self.term_tag(term))
        print("Term pos", self.term_pos(term))
        print("Term lemma", self.term_lemma(term))
        print("Term dep", self.term_dep(term))
        print("Term head", term.head)

    def term_encode_utf8(self, strTerm):
        """
        Transforms a string to unicode
        :param strTerm:
        :return: the unicode of the string
        """
        if sys.hexversion >= 0x3000000:
            return strTerm
        return strTerm.decode("UTF-8")

    def term_tag(self, term):
        """

        :param term:
        :return: the tag of the term
        """
        if isinstance(term, str):
            term = self.term_encode_utf8(term)
            docs = self._model(term)
            for tmp_term in docs:
                return tmp_term.tag_
        return term.tag_

    def term_pos(self, term):
        """

        :param term:
        :return: the pos of the term
        """
        if isinstance(term, str):
            if isinstance(term, str):
                term = self.term_encode_utf8(term)
                docs = self._model(term)
                for tmp_term in docs:
                    return tmp_term.pos_
        return term.pos_

    def term_lemma(self, term):
        """

        :param term:
        :return: the lemma of the term
        """
        if isinstance(term, str):
            if isinstance(term, str):
                term = self.term_encode_utf8(term)
                docs = self._model(term)
                for tmp_term in docs:
                    return tmp_term.lemma_
        return term.lemma_

    def term_dep(self, term):
        """

        :param term:
        :return: the dep of the term
        """
        if isinstance(term, str):
            if isinstance(term, str):
                term = self.term_encode_utf8(term)
                docs = self._model(term)
                for tmp_term in docs:
                    return tmp_term.dep_
        return term.dep_

    def similarity(self, term1, term2):
        """
        Compute similarity score between term1 and term2 -- term1 and term2 may be strings or spacy objects
        :param term1:
        :param term2:
        :return: the similarity score
        """
        if isinstance(term1, str) and isinstance(term2, str):
            docStr = term1 + " " + term2
            doc = self.term_encode_utf8(docStr)
            term1, term2 = self._model(doc)
        return term1.similarity(term2)


    def most_similar(self, term, max_num=10, min_prob = -15):
        """
        Determines which words are most similar to term
        :param term: the term to compare
        :param max_num: optional -- the max number of similar words returned. Default is 10
        :param min_prob: optional -- the threshold probability. Must be negative number. Default is -15
        :return:
        """
        if isinstance(term, str):
            term = self.term_encode_utf8(term)
        docs = self._model(term)
        for word in docs:
            queries = [w for w in word.vocab if w.is_lower == word.is_lower and w.prob >= min_prob]
            by_similarity = sorted(queries, key=lambda w: word.similarity(w), reverse=True)
            return by_similarity[:max_num]
        return 0.0

    def tf(self, term):
        """

        :param term:
        :return: the term frequency in this object
        """
        count = 0.00
        num_terms = len(self._doc)
        for doc_term in self._doc:
            if term == doc_term.text:
                count = count + 1
        if self._field == 'text':
            self.field = "title"
        else:
            self.field = "text"
        self._doc = self.doc(self._field)
        num_terms = num_terms + len(self._doc)
        for doc_term in self._doc:
            if term == doc_term.text:
                count = count + 1
        return float(count/num_terms)


    def tf_tag(self, term):
        """

        :param term:
        :return: the term frequence in all the tags of this object
        """
        count = 0
        tags = self._object.tags_sorted_by_score()
        for tag in tags:
            tag_text = self._client.tag_data(tag)
            if isinstance(tag_text, str):
                self._object = tag_text
                self._field = 'text'
                self._doc = self.doc(self._field)
            for doc_term in self._doc:
                if term == doc_term:
                    count = count + 1
        return count

    def tf_idf(self, response, term):
        """
        Computes tf-idf of a term
        :param response: the whole response
        :param term: the term to be computed
        :return:
        """
        tf = self.tf(term)
        query_info = response.query_info()
        term = query_info.term(term)
        term_freq_in_docs = float(term.freq()) # times term is found in a doc
        num_docs_in_collection = float(response.docsInCollection()) #
        return tf * (1 + math.log((num_docs_in_collection/term_freq_in_docs), 2))

    def query_weight(self, response):
        weight = 0.00
        query_info = response.query_info()
        terms = query_info.terms()
        for term in terms:
             if term.isRequired():
                 tf_idf = self.tf_idf(response, term.to_str())
                 weight = weight + tf_idf
        return weight







