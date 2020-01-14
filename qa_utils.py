"""
utility classes for QA text processing

Package: fqakg

Author: Eduard Kegulskiy

"""

from nltk.tag import StanfordPOSTagger
from nltk.tag import StanfordNERTagger
import nltk
from word2number import w2n
import re

class KGQAPOSTagger:
    """
    Parts-of-Speech and Named Entity Recognition taggers, based on Stanford Taggers (https://www.nltk.org/_modules/nltk/tag/stanford.html)
    """
    _POSTagger = StanfordPOSTagger(
        #model_filename='stanford-postagger-2018-10-16/models/english-bidirectional-distsim.tagger',
        model_filename='stanford-postagger-2018-10-16/models/english-left3words-distsim.tagger',
        path_to_jar="stanford-postagger-2018-10-16/stanford-postagger.jar")

    _NERTagger = StanfordNERTagger(
        model_filename='stanford-ner-2018-10-16/classifiers/english.all.3class.distsim.crf.ser.gz',
        path_to_jar='stanford-ner-2018-10-16/stanford-ner.jar',
        encoding='utf-8')

    def __init__(self):
        _empty = 0

    def tag(self, sentence, ner=True):
        """
            POS and optional NER tagging
        :param sentence: sentence to tag
        :param ner: if True, also perform NER tagging
        :return: list of POS-word tuples and list of NER-word tuples (if ner was set to True)
        """
        if isinstance(sentence, list):
            pos_tags = KGQAPOSTagger._POSTagger.tag(sentence)
        else:
            pos_tags = KGQAPOSTagger._POSTagger.tag(sentence.split())
        if ner:
            tokens = nltk.tokenize.word_tokenize(sentence)
            ner_tags = KGQAPOSTagger._NERTagger.tag(tokens)
        else:
            ner_tags = None
        return pos_tags, ner_tags

class KGQANumberDetector:
    """
        Detects whether a given text contains a number in either digit form or textual form
    """
    def __init__(self):
        _empty = 0

    numeric_answers = ['never', 'none']

    def has_number(self, text):
        """
        :param text: text to search for a number
        :return: True if contains a number (digit or textual), False otherwise
        """

        # these words are also considered as having "numeric" meaning
        for n in KGQANumberDetector.numeric_answers:
            if text.find(n) != -1:
                return True

        numbers = re.findall(r'\d+', text)
        if len(numbers) == 0:
            try:
                numbers = w2n.word_to_num(text)
            except:
                return False  # no numbers found
        return True