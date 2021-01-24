"""
This file implements the Question Preprocessing Module (QPM)

Package: fqakg

Author: Jose Ortiz
Author: Eduard Kegulskiy

"""

from nltk.corpus import stopwords
from nltk.tokenize import TweetTokenizer
import enum
from qa_utils import *
from colorama import init
init() # colorama needed for Windows
from colorama import Fore, Back, Style

class QuestionType(enum.Enum):
    Unclassified = 1
    SimpleFact = 2
    ComplexFact = 3

class QuestionEntity(enum.Enum):
    NONE = 1
    PERSON = 2
    LOCATION = 3
    ORGANIZATION = 4

class QPM(object):
    """
        QPM pre-processes the original question implementing a basic gramatical correction, and sanitizing the question to
        remove junk data.
    """

    # Constants
    Q_COLOR = Fore.CYAN
    def __init__(self, question, labeled_answer=""):
        """
        Class constructor.

            # Arguments
                question - user question
                labeled_answer[optional] - if provided, the class makes it available to other modules of the pipeline
                                           for collecting statistics and error analysis

            # Returns
                A QPM instance.
        """
        self.log("{}MODULE 1: QUESTION PRE-PROCESSING MODULE{}".format(Style.BRIGHT, Style.RESET_ALL))

        self.log("Question: {}{}{}{}".format(QPM.Q_COLOR, Style.BRIGHT, question, Style.RESET_ALL))
        self._stop_words = None
        self._tknzr = TweetTokenizer()
        self._free_text = self.first_q(question)

        self._labeled_answer = labeled_answer
        self._question_type = QuestionType.Unclassified
        self._pos_tagger = KGQAPOSTagger()
        self._collect_tags()

        self._query = self.get_sanitazed_sentence(self._free_text)
        self.log("Stop-words removed: {}{}{}{}".format(QPM.Q_COLOR, Style.BRIGHT, self._query, Style.RESET_ALL))

        self._entities = []
        self._important_query_terms = []
        self._verbs = []
        self._nouns = []
        self._is_numerical_answer_expected = False

        self._classify_question()
        self._check_numerical_answer_expected()

    def log(self, text):
        print("[{}] {}".format(QPM.__qualname__, text))

    def _collect_tags(self):
        # get parts-of-speech and NER tags
        self._pos_tags, self._ner_tags = self._pos_tagger.tag(self._free_text)

        if self._pos_tags:
            pos_str = ""
            for t in self._pos_tags:
                pos_str = pos_str + "{}{}{}{}({}) ".format(QPM.Q_COLOR, Style.BRIGHT, t[0], Style.RESET_ALL, t[1])
            self.log("Parts of speech: {}".format(pos_str))

    def pos_tags(self):
        return self._pos_tags

    def important_query_terms(self):
        return self._important_query_terms

    def query_verbs(self):
        return self._verbs

    def query_nouns(self):
        return self._nouns

    def _classify_question(self):
        """ collects information about the question and classifies it to be either simple fact (QuestionType.SimpleFact)
         or complex fact (QuestionType.ComplexFact)

        # Arguments
            None

        # Returns
            None
        """

        verbs = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
        important_pos = [
            'NN',# NN noun, singular ‘desk’
            'NNS',# NNS noun plural ‘desks’
            'NNP',# NNP proper noun, singular ‘Harrison’
            'NNPS',# NNPS proper noun, plural ‘Americans’
        ]

        nouns = [
            'NN',# NN noun, singular ‘desk’
            'NNS',# NNS noun plural ‘desks’
            'NNP',# NNP proper noun, singular ‘Harrison’
            'NNPS',# NNPS proper noun, plural ‘Americans’
        ]

        num_verbs = 0
        cur_important_term = ""
        for index, token in enumerate(self._pos_tags):
            # collect all verbs
            if token[1] in verbs:
                num_verbs += 1
                self._verbs.append(token[0].strip().lower())
            # collect all nouns
            if token[1] in nouns:
                self._nouns.append(token[0].strip().lower())

            if token[0] not in self._stop_words:
                if token[1] in important_pos:
                    cur_important_term += " " + token[0]
                else:
                    if cur_important_term != "":
                        # collect all important terms
                        self._important_query_terms.append(self.remove_non_alphanumeric(cur_important_term).strip().lower())
                        cur_important_term = ""
        # last important term
        if cur_important_term != "":
            self._important_query_terms.append(self.remove_non_alphanumeric(cur_important_term).strip().lower())
        #print("QPM.[important query terms]: {}".format(self._important_query_terms))

        self._entities = []
        cur_ner = ""
        cur_ner_type = ""
        for index, token in enumerate(self._ner_tags):
            if token[1] != 'O':
                if cur_ner != "" and cur_ner_type == token[1]:
                    # continuation of NER, let's combine it
                    cur_ner += " " + token[0]
                else:
                    if cur_ner != "":
                        self._entities.append((cur_ner, cur_ner_type))
                    cur_ner = token[0]
                    cur_ner_type = token[1]
            else:
                if cur_ner != "":
                    self._entities.append((cur_ner, cur_ner_type))
                cur_ner = ""
                cur_ner_type = ""

        # add last one
        if cur_ner != "":
            self._entities.append((cur_ner, cur_ner_type))

        if self._entities:
            ner_str = ""
            for t in self._entities:
                ner_str = ner_str + "{}{}{}{}({}) ".format(QPM.Q_COLOR, Style.BRIGHT, t[0], Style.RESET_ALL, t[1])
            self.log("Named entities: {}".format(ner_str))

        if num_verbs <= 1 and len(self._pos_tags) <= 6:
            self._question_type = QuestionType.SimpleFact
            self.log("Question type: Simple fact")
        else:
            self._question_type = QuestionType.ComplexFact
            self.log("Question type: Complex fact")

    @property
    def question_type(self):
        return self._question_type

    @property
    def question_named_entities(self):
        return self._entities

    def first_q(self, text):
        """
        :param text: the original text
        :return: the text without the ? character if any
        """
        return text.replace("?", "")

    def remove_non_alphanumeric(self, query):
        """
        :param query: the query
        :return: the query containing only alphanumeric characters
        """
        removelist = "'‘`’"
        pattern = re.compile(r'[^\w' + removelist + ']')

        #pattern = re.compile('\W')
        return re.sub(pattern, ' ', query)

    def get_sanitazed_sentence(self, text):
        """
        :param text:
        :return: sentence without stop words
        """
        word_tokens = self._tknzr.tokenize(text)
        filtered_sentence = [w for w in word_tokens if not w in self.stop_words()]
        sentence = " ".join(filtered_sentence)
        return sentence

    def query(self):
        """
        :return: search query that has been generated by sanitization of the original question (see get_sanitazed_sentence)
        """
        return self._query

    def free_text(self):
        return self._free_text

    def labeled_answer(self):
        return self._labeled_answer

    def stop_words(self):
        if self._stop_words is None:
            self._stop_words = set(stopwords.words('english'))
            self._stop_words.update(('Where', 'Who', 'Whose', 'What', 'Why', 'How', 'and', 'I', 'A', 'And', 'So', 'arnt', 'This',
                               'When', 'It', 'many', 'Many', 'so', 'cant',
                               'Yes', 'yes', 'No', 'no', 'These', 'these', 'is', 'are', 'Do', "Are", "About", "For", "Is", "\""))
            self._stop_words.remove('own')
            self._stop_words.remove('too')

        return self._stop_words

    def _check_numerical_answer_expected(self):
        """
        detects if provided question is expecting a numerical answer
        :return: none
        """
        self._is_numerical_answer_expected = self._free_text.lower().startswith('when') |\
                                             self._free_text.lower().startswith('how hot') | \
                                             self._free_text.lower().startswith('how big') | \
                                             self._free_text.lower().startswith('how many') | \
                                             self._free_text.lower().startswith('how much') | \
                                             self._free_text.lower().startswith('how often') | \
                                             self._free_text.lower().startswith('what date') | \
                                             self._free_text.lower().startswith('how old') | \
                                             self._free_text.lower().startswith('how close') | \
                                             self._free_text.lower().startswith('how tall') | \
                                             self._free_text.lower().startswith('how far') | \
                                             self._free_text.lower().startswith('what year') | \
                                             self._free_text.lower().startswith('how high') | \
                                             self._free_text.lower().startswith('which number') | \
                                             self._free_text.lower().startswith('how fast')
        if self._is_numerical_answer_expected:
            self.log("The question expects a numerical answer")
        else:
            self.log("The question does not expect a numerical answer")

    def is_numerical_answer_expected(self):
        """
        :return: true if a numerical question is expected for provided question, otherwise false
        """
        return self._is_numerical_answer_expected
