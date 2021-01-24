"""
This file implements the Factoid Answer Extraction Selection Module (FAESM)

Package: fqakg

Author: Jose Ortiz
        Eduard Kegulskiy

"""
# -*- coding: utf-8 -*-
from __future__ import division

import datetime
import enum
import json
import statistics
import string

import numpy as np
#from config import Config
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from websocket import create_connection
from colorama import init
init() # colorama needed for Windows
from colorama import Fore, Back, Style

from qa_utils import *
#from metrics.measure import *
#from utils.pos_tagger import *


class FAESM:
    """
    FAESM takes as input the instance of DSOEM class which provides high quality data objects with potentially large corpus.
    It processes the objects using Deep Learning and returns best short answers.
    """
    #####################################################################################################
    # CONFIGURABLE PARAMETERS
    # maximum size in word tokens of answer paragraphs (optimized for BERT processing)
    ANSWER_PARAGRAPH_MAX_SIZE = 200
    # maximum number of answer paragraphs to be passed to BERT for processing (experimentally optimized
    # for processing time and minimum noise)
    ANSWER_PARAGRAPHS_MAX_AMOUNT = 20
    # regular expression to tokenize string into words (much faster than standard tokenizers, while producing
    # almost the same accuracy)
    WORD = re.compile(r'\w+')
    # regular expression to tokenize text into sentences (much faster than standard tokenizers, while producing
    # almost the same accuracy)
    SENTENCE = re.compile(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s')
    #####################################################################################################

    # global object for number detection
    _number_detector = KGQANumberDetector()

    def __init__(self, dsoem):
        """
        Constructor
        :param dsoem - instance of DSOEM class
        """
        self.log("{}MODULE 4: FACTOID ANSWER EXTRACTION SELECTION MODULE{}".format(Style.BRIGHT, Style.RESET_ALL))

        self._best_query = None
        self._top_objects = None
        self._oem = dsoem
        self._instance = dsoem.instance()
        self._original_q = dsoem.original_question()
        self._labeled_answer = dsoem.labeled_answer()

        self._bert_prediction_result = []
        self._bert_candidates = []
        self._ws = None
        self._candidate_answers = []
        self._answer_paragraphs = []
        self._kg_fields_results = []
        self._all_significant_queries_terms = []

        # initialize
        # self._vectorizer = TfidfVectorizer(tokenizer=self.normalize, stop_words='english')
        self._vectorizer = TfidfVectorizer(use_idf=True, stop_words='english')
        self._tfidf_reverse_lookup = None
        self._stemmer = nltk.stem.porter.PorterStemmer()
        self._remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)

        # update stats
        self._answer_paragraphs_contain_answer = False
        self._positive_score_has_answer = False
        self._zero_score_has_answer = False

        self._generate_all_answer_paragraphs()
        self._process_with_bert()

    def log(self, text):
        print("[{}] {}".format(FAESM.__qualname__, text))

    def _process_with_bert(self):
        before = datetime.datetime.now()
        for bert_candidate in self._bert_candidates:
            self.get_bert_prediction(bert_candidate, self._original_q)
        after = datetime.datetime.now()
        timespan = after - before
        duration = int(timespan.total_seconds() * 1000)
        #self.log("BERT inference time: {} ms".format(duration))

    def _generate_all_answer_paragraphs(self):
        data = self._oem.get_data_objects()
        kg_data = self._oem.get_kg_data_objects()
        if data:
            self._best_query = data[0]
            self._top_objects = data[1]

        self._prepare_significant_query_terms()

        if kg_data:
            print("FAESM.[BERT Candidates List] Adding KG API Answer Paragraphs")
            self._select_answer_paragraphs_from_kg(kg_data)

        if self._top_objects:
            self.log("[BERT Candidates List] Adding Search API Answer Paragraphs")
            self._select_answer_paragraphs_from_global_search()

        self.log("BERT Candidates List: {}".format(len(self._bert_candidates)))

    def _prepare_significant_query_terms(self):
        self._all_significant_queries_terms = set()
        for index, obj in enumerate(self._top_objects):
            diff_bot_obj = obj[0]
            query_rank = obj[1]
            query_grams = obj[2]
            for gram in query_grams:
                for t in gram.split():
                    if t not in self._oem._qpm.stop_words():
                        self._all_significant_queries_terms.add(t.lower())

    def _select_answer_paragraphs_from_kg(self, kg_data):
        for obj in kg_data:
            inner_object = obj[0].meta_data()
            if 'allDescriptions' in inner_object:
                if isinstance(inner_object['allDescriptions'], list):
                    for each_desc in inner_object['allDescriptions']:
                        self._bert_candidates.append(each_desc)
                else:
                    self._bert_candidates.append(inner_object['allDescriptions'])
            if 'description' in inner_object:
                self._bert_candidates.append(inner_object['description'])

    def _collect_candidate_stats(self, score, candidate):
        if self._labeled_answer:
            if score > 0:
                if self.contains_answer(candidate, self._labeled_answer):
                    self._positive_score_has_answer = True
            else:
                if self.contains_answer(candidate, self._labeled_answer):
                    self._zero_score_has_answer = True

    def contains_answer(self, s, answer):
        matched_strings = 0
        if isinstance(s, list):
            for item in s:
                matched_strings += len(re.findall(answer, item, re.IGNORECASE))
        else:
            matched_strings = len(re.findall(answer, s, re.IGNORECASE))
        return matched_strings

    def collect_answer_paragraphs_precision_at(self, answer_paragraph, index, cos_sim_score):
        if self._labeled_answer:
            if not self._answer_paragraphs_contain_answer and self.contains_answer(answer_paragraph,
                                                                                   self._labeled_answer):
                self._answer_paragraphs_contain_answer = True

                if index in FAESM.top_candidates_threasholds:
                    FAESM.top_candidates_threasholds[index] += 1
                else:
                    FAESM.top_candidates_threasholds[index] = 1

                if FAESM.answer_paragraphs_index_threashold_for_answer < index:
                    FAESM.answer_paragraphs_index_threashold_for_answer.set(index)

                FAESM.top_score_with_answer_f.add_value(cos_sim_score)

    def _collect_all_bert_error_analysis(self):
        FAESM.total_all_bert_errors += 1
        error_name = "bert_all_answers_error_{}".format(FAESM.total_top_bert_errors)
        error_analysis = ValuesCollector("FAESM",
                                         error_name,
                                         enabled=FAESM.COLLECT_STATS,
                                         file_path=error_name,
                                         value_entry_separator="\n")

        error_analysis.add_value("[ORIGINAL QUERY]: " + self._original_q)
        error_analysis.add_value("[LABELED ANSWER]: " + self._labeled_answer)

        for index, candidate in enumerate(self._bert_candidates):
            paragraph = candidate
            has_answer = self.contains_answer(paragraph, self._labeled_answer)
            if has_answer:
                error_analysis.add_value(
                    "[CANDIDATE {} with answer]: {}".format(index, paragraph))
            else:
                error_analysis.add_value(
                    "[CANDIDATE {} without answer]: {}".format(index, paragraph))

            error_analysis.add_value("\n")

        bert_predictions = self.bert_answer_prediction()

        error_analysis.add_value("BERT ANSWERS:")
        for item in bert_predictions:
            is_correct_answer = self.contains_answer(item['text'], self._labeled_answer)
            error_analysis.add_value("    {}: {}, [{}]".format("CORRECT" if is_correct_answer else "WRONG  ",
                                                               item['probability'],
                                                               item['text']))

    def _collect_top_error_analysis(self):
        FAESM.total_top_bert_errors += 1
        error_name = "top_answer_error_{}".format(FAESM.total_top_bert_errors)
        error_analysis = ValuesCollector("FAESM",
                                         error_name,
                                         enabled=FAESM.COLLECT_STATS,
                                         file_path=error_name,
                                         value_entry_separator="\n")

        error_analysis.add_value("[ORIGINAL QUERY]: " + self._original_q)
        error_analysis.add_value("[LABELED ANSWER]: " + self._labeled_answer)

        for index, candidate in enumerate(self._bert_candidates):
            paragraph = candidate
            has_answer = self.contains_answer(paragraph, self._labeled_answer)
            if has_answer:
                error_analysis.add_value(
                    "[CANDIDATE {} with answer]: {}".format(index, paragraph))
            else:
                error_analysis.add_value(
                    "[CANDIDATE {} without answer]: {}".format(index, paragraph))

            error_analysis.add_value("\n")

        bert_predictions = self.bert_answer_prediction()

        error_analysis.add_value("BERT ANSWERS sorted by probability:")
        all_answers = {}
        all_answer_tokens = {}
        for item in bert_predictions:
            answer = item['text']
            probability = item['probability']
            is_correct_answer = self.contains_answer(answer, self._labeled_answer)
            error_analysis.add_value("    {}: {}, [{}]".format("CORRECT" if is_correct_answer else "WRONG  ",
                                                               probability,
                                                               answer))

            if answer in all_answers:
                all_answers[answer] += probability
            else:
                all_answers[answer] = probability

            word_tokens = nltk.word_tokenize(answer)
            stop_words = set(stopwords.words('english'))
            stop_words.update(
                ('where', 'who', 'whose', 'what', 'why', 'how', 'and', 'i', 'a', 'and', 'so', 'arnt', 'this',
                 'when', 'it', 'many', 'many', 'so', 'cant',
                 'yes', 'no', 'these', 'is', 'are', 'do', "about", "for", "is", "\"",
                 ',', '.', '(', ')', '`', '\"', '\'', '-',))

            tokens = [w for w in word_tokens if not w.lower() in stop_words]

            for t in tokens:
                if t in all_answer_tokens:
                    all_answer_tokens[t] += probability
                else:
                    all_answer_tokens[t] = probability

        all_answers = sorted(all_answers.items(), key=lambda i: i[1], reverse=True)
        error_analysis.add_value("BERT ANSWERS sorted by combined probability:")
        for item in all_answers:
            answer = item[0]
            combined_prob = item[1]
            is_correct_answer = self.contains_answer(answer, self._labeled_answer)
            error_analysis.add_value("    {}: {}, [{}]".format("CORRECT" if is_correct_answer else "WRONG  ",
                                                               combined_prob,
                                                               answer))

        all_answer_tokens = sorted(all_answer_tokens.items(), key=lambda i: i[1], reverse=True)
        error_analysis.add_value("")
        error_analysis.add_value("")

        error_analysis.add_value("BERT TOKENS sorted by combined probability:")
        for item in all_answer_tokens:
            answer = item[0]
            combined_prob = item[1]
            is_correct_answer = self.contains_answer(answer, self._labeled_answer)
            error_analysis.add_value("    {}: {}, [{}]".format("CORRECT" if is_correct_answer else "WRONG  ",
                                                               combined_prob,
                                                               answer))

    def _collect_error_analysis(self):
        # only possible when we have a labeled answer
        if self._labeled_answer:
            candidate_answers_have_answer = self._zero_score_has_answer | self._positive_score_has_answer

            if candidate_answers_have_answer and not self._answer_paragraphs_contain_answer:
                FAESM.total_errors += 1
                error_name = "answer_paragraphs_error_{}".format(FAESM.total_errors)
                error_analysis = ValuesCollector("FAESM",
                                                 error_name,
                                                 enabled=FAESM.COLLECT_STATS,
                                                 file_path=error_name,
                                                 value_entry_separator="\n")

                error_analysis.add_value("[ORIGINAL QUERY]: " + self._original_q)
                error_analysis.add_value("[Significant Queries Terms]: ", std_out=False, separator=" ")
                for t in self._all_significant_queries_terms:
                    error_analysis.add_value(t, std_out=False, separator=" ")

                error_analysis.add_value("")
                error_analysis.add_value("[STEMMED QUERY]: " + " ".join(self.normalize(self._oem.query())))
                error_analysis.add_value("[LABELED ANSWER]: " + self._labeled_answer)
                error_analysis.add_value("[ANSWER PARAGRAPHS CUT_OFF]: " + str(len(self._bert_candidates) - 1))

                for index, candidate in enumerate(self._candidate_answers):
                    cos_sim_score = candidate[0]
                    paragraph = candidate[1]
                    has_answer = self.contains_answer(paragraph, self._labeled_answer)
                    if has_answer:
                        error_analysis.add_value(
                            "[CANDIDATE {} (score={}) with answer]: {}".format(index, cos_sim_score, paragraph))
                        error_analysis.add_value(
                            "[CANDIDATE {} STEMMED]: {}".format(index, " ".join(self.normalize(paragraph))))
                        break
                    else:
                        error_analysis.add_value(
                            "[CANDIDATE {} (score={}) without answer]: {}".format(index, cos_sim_score, paragraph))
                        error_analysis.add_value(
                            "[CANDIDATE {} STEMMED]: {}".format(index, " ".join(self.normalize(paragraph))))

                    error_analysis.add_value("\n")

    def is_valid_text(self, text):
        return True

    def _term_distance_score(self, paragraph_tokens, query_grams):
        num_spawns = 0
        cumulative_distance = 0
        spawn_start_index = 0
        term_distance_score = 0
        first_token_found = False
        smallest_distance = -1

        prev_token = ""
        for index, token in enumerate(paragraph_tokens):
            if token not in self._oem._qpm.stop_words():
                if token in query_grams:
                    if first_token_found:
                        # previous spawn has completed since we found next matching gram
                        if token != prev_token:
                            spawn_distance = index - spawn_start_index
                            cumulative_distance = cumulative_distance + spawn_distance
                            num_spawns += 1

                            if smallest_distance == -1:
                                smallest_distance = spawn_distance
                            elif spawn_distance < smallest_distance:
                                smallest_distance = spawn_distance

                        prev_token = token

                    first_token_found = True
                    spawn_start_index = index
                    # print(token)

        # if cumulative_distance > 0:
        #    term_distance_score = num_spawns/cumulative_distance
        # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! term_distance_score={}".format(term_distance_score))
        if smallest_distance > 0:
            term_distance_score = num_spawns / smallest_distance / len(paragraph_tokens)
        return term_distance_score

    def _contains_number(self, text):
        numbers = re.findall(r'\d+', text)
        if len(numbers) == 0:
            try:
                numbers = w2n.word_to_num(text)
            except:
                return False  # no numbers found
        return True

    def regex_word_tokenize(self, text):
        words = FAESM.WORD.findall(text)
        return words

    def _candidate_answer_paragraph_score(self, candidate, query_rank, query_grams):
        if self._oem._qpm.is_numerical_answer_expected() and not FAESM._number_detector.has_number(candidate):
            return 0  # no numbers found, the score is 0

        all_query_tokens = set(query_grams)
        candidate_tokens = self.regex_word_tokenize(candidate.lower())
        # candidate_tokens = nltk.word_tokenize(candidate.lower())
        candidate_tokens_set = set(candidate_tokens)

        term_coverage_set = all_query_tokens & candidate_tokens_set
        term_coverage_score = len(term_coverage_set) / len(all_query_tokens)

        tfidf_vectorizer_vectors = self.vectorizer().transform([candidate])

        tfidf_score = 0
        tfidf_token_matches = 0
        for t in all_query_tokens:
            if t in self._tfidf_reverse_lookup:
                index = self._tfidf_reverse_lookup[t]
                temp = tfidf_vectorizer_vectors.A[0][index]
                if temp > 0:
                    tfidf_score += temp
                    tfidf_token_matches += 1

        if tfidf_token_matches > 0:
            tfidf_score = tfidf_score / tfidf_token_matches

        term_distance_score = self._term_distance_score(candidate_tokens, query_grams)

        score = tfidf_score + term_coverage_score + term_distance_score

        if False:
            answer_str = "with answer" if self.contains_answer(candidate, self._labeled_answer) else "no answer"
            print("    term_coverage_score: {}".format(term_coverage_score))
            print("    tfidf_score: {}".format(tfidf_score))
            print("    term_distance_score: {}".format(term_distance_score))
            print("    important_terms_score: {}".format(important_terms_score))
            print("    total score: {} {}".format(score, answer_str))

        return score

    def _generate_candidate_answer_paragraphs(self, sentences, query_rank, query_grams):
        docs = []

        def add_candidate(candidate):
            if candidate != "":
                candidate_score = self._candidate_answer_paragraph_score(candidate, query_rank, query_grams)

                if candidate_score > 0:
                    candidates.append((candidate_score, candidate))
                else:
                    zero_score_candidates.append((candidate_score, candidate))

                self._collect_candidate_stats(candidate_score, candidate)

        def chunkstring(string, length):
            return (string[0 + i:length + i] for i in range(0, len(string), length))

        # Build candidate answer paragraphs using sliding window method
        candidates = []
        zero_score_candidates = []
        self._index_of_max_cos_sim_score = 0
        candidate = ""

        for index, sentence in enumerate(sentences):
            sentences_chunked = chunkstring(sentence, FAESM.ANSWER_PARAGRAPH_MAX_SIZE)
            for chunked_sentence in sentences_chunked:
                if candidate is not "" and len(candidate.split()) + len(
                        chunked_sentence.split()) > FAESM.ANSWER_PARAGRAPH_MAX_SIZE:
                    docs.append(candidate)
                    candidate = ""

                # append next candidate
                candidate = candidate + chunked_sentence

        # add last one
        docs.append(candidate)
        self.vectorizer().fit_transform(docs)
        tfidf_features = np.array(self.vectorizer().get_feature_names())
        self._tfidf_reverse_lookup = {
            word: idx for idx, word in enumerate(tfidf_features)}

        for d in docs:
            add_candidate(d)

        # if there was no candidate with positive cos similarity, let's give it one entry
        # from zero cos similarity list, to give BERT a chance to find an answer
        if len(candidates) == 0 and len(zero_score_candidates) > 0:
            candidates.append(zero_score_candidates[0])

        return candidates

    def _new_selection_strategy(self, candidates):
        for index, candidate in enumerate(candidates):
            candidate_score = candidate[0]
            paragraph = candidate[1]
            self._bert_candidates.append(paragraph)
            self.collect_answer_paragraphs_precision_at(paragraph, index, candidate_score)

    def _select_answer_paragraphs_from_global_search(self):
        candidates = []
        for index, obj in enumerate(self._top_objects):
            diff_bot_obj = obj[0]
            query_rank = obj[1]
            query_grams = obj[2]

            obj_sentences = self._extract_sentences([obj])
            cur_candidates = self._generate_candidate_answer_paragraphs(obj_sentences, query_rank,
                                                                        self._all_significant_queries_terms)
            self._candidate_answers += cur_candidates

        # sort by score
        self._candidate_answers = sorted(self._candidate_answers, reverse=True)

        for index, c in enumerate(self._candidate_answers):
            candidates.append(c)
            if index == FAESM.ANSWER_PARAGRAPHS_MAX_AMOUNT - 1:
                break

        self._answer_paragraphs = sorted(candidates, reverse=True)
        self._new_selection_strategy(self._answer_paragraphs)

    def get_bert_prediction(self, context, query):
        data = {}
        data['data'] = [None]
        data['data'][0] = {}
        data['data'][0]['title'] = "Title"
        data['data'][0]['paragraphs'] = [None]
        data['data'][0]['paragraphs'][0] = {}
        data['data'][0]['paragraphs'][0]['context'] = context
        data['data'][0]['paragraphs'][0]['qas'] = [None]
        data['data'][0]['paragraphs'][0]['qas'][0] = {}
        data['data'][0]['paragraphs'][0]['qas'][0]['question'] = query
        data['data'][0]['paragraphs'][0]['qas'][0]['id'] = "1"
        json_data = json.dumps(data)

        if self._ws is None:
            try:
                self._ws = create_connection("ws://localhost:13254")
            except:
                self.log("bert-qa_srv connection not available")
                return

        self.log("Sending candidate to BERT: {}".format(context))
        self._ws.send(json_data)
        # print("Sent")
        # print("Receiving...")
        result = self._ws.recv()
        # print("Received '%s'" % result)
        self._bert_prediction_result.append(result)
        # self._ws.close()

    def stem_tokens(self, tokens):
        return [self._stemmer.stem(item) for item in tokens]

    def normalize(self, text):
        return self.stem_tokens(nltk.word_tokenize(text.lower().translate(self._remove_punctuation_map)))

    def vectorizer(self):
        return self._vectorizer

    def cosine_sim(self, text1, text2):
        tfidf = self.vectorizer().transform([text1, text2])

        return ((tfidf * tfidf.T).A)[0, 1]

    def split_into_sentences(self, text):
        # return list(set(self.split_into_sentences_add(text.strip())))  # list(set(nltk.sent_tokenize(text.strip())))
        # return nltk.sent_tokenize(text)

        # nltk_sent = nltk.sent_tokenize(text)
        sent = re.split(FAESM.SENTENCE, text)
        return sent

    def remove_non_alphanumeric(self, sentence):
        pattern = re.compile('\W')
        return re.sub(pattern, ' ', sentence)

    def remove_duplicates(self, queries):
        seen = set()
        seen_add = seen.add
        return [x for x in queries if not (x in seen or seen_add(x))]

    def _extract_sentences(self, encapsulated_objects):
        sentences = []
        for object_tuple in encapsulated_objects:
            object = object_tuple[0]
            try:
                text = ""
                if hasattr(object, 'text') and object is not None:
                    text = object.text()
                else:
                    text = object

                sents = self.split_into_sentences(text)
                for sent in sents:
                    # if self.is_valid_sentence(sent):
                    sentences.append(sent.strip())
            except:
                continue
        # return self.remove_duplicates(sentences)
        return sentences

    def is_valid_sentence(self, sentence):
        if "?" in sentence:
            return False
        elif len(sentence.split()) <= 3:
            return False
        return True

    def bert_answer_prediction(self):
        if True:
            final_bert_list = []
            # json_str = json.dumps(self._bert_prediction_result)
            for result in self._bert_prediction_result:
                bert_objs = json.loads(result)
                final_bert_list += bert_objs

            final_bert_list = sorted(final_bert_list, key=lambda i: i['probability'], reverse=True)
            return final_bert_list
        else:
            return []

    def _bert_top_by_combined_prob(self, bert_predictions):
        all_answers = {}
        for item in bert_predictions:
            answer = item['text']
            probability = item['probability']

            if self._oem._qpm.is_numerical_answer_expected() and not FAESM._number_detector.has_number(answer):
                continue  # no numbers found, skip this candidate

            if answer in all_answers:
                all_answers[answer] += probability
            else:
                all_answers[answer] = probability

        all_answers = sorted(all_answers.items(), key=lambda i: i[1], reverse=True)
        return all_answers

    def top_answers(self):
        answers = []

        matched_kg_results = False
        for kg_result in self._kg_fields_results:
            answers.append(kg_result)
            if fqakg_test_contains_answer(kg_result, self._labeled_answer):
                matched_kg_results = True

        final_bert_list = self.bert_answer_prediction()
        all_bert_contains_answer = False
        top_contains_answer = False
        num_top_answers_to_analyze_errors = 3

        if False:
            for item in final_bert_list:
                if self._oem._qpm.is_numerical_answer_expected() and not self._contains_number(item['text']):
                    continue  # no numbers found, skip this candidate
                if num_items > 0:
                    answers.append(item['text'])
                    num_items -= 1
                    if self.contains_answer(item['text'], self._labeled_answer):
                        top_contains_answer = True

                if self.contains_answer(item['text'], self._labeled_answer):
                    all_bert_contains_answer = True
        else:
            bert_combined_prob_list = self._bert_top_by_combined_prob(final_bert_list)
            for index, item in enumerate(bert_combined_prob_list):
                answer = item[0]
                combined_prob = item[1]

                # append all items
                answers.append(answer)

                # only analalyze errors for num_top_answers_to_analyze_errors
                if self._labeled_answer:
                    if num_top_answers_to_analyze_errors > 0:
                        num_top_answers_to_analyze_errors -= 1
                        if self.contains_answer(answer, self._labeled_answer):
                            top_contains_answer = True

                    if self.contains_answer(answer, self._labeled_answer):
                        all_bert_contains_answer = True

        if all_bert_contains_answer:
            FAESM.all_bert_answers_contain_answer += 1

        if matched_kg_results:
            FAESM.matched_kg_fields_contain_answer += 1

        bert_candidates_have_answer = self._zero_score_has_answer | self._positive_score_has_answer
        if self._zero_score_has_answer:
            FAESM.candidate_answers_zero_score_contain_answer += 1
        if self._positive_score_has_answer:
            FAESM.candidate_answers_pos_score_contain_answer += 1
        if bert_candidates_have_answer:
            FAESM.paragraphs_contain_answer += 1
        if self._answer_paragraphs_contain_answer:
            FAESM.answer_paragraphs_contain_answer += 1

        if self._labeled_answer:
            self.print_stats()
            self._collect_error_analysis()

            if all_bert_contains_answer and not top_contains_answer:
                self._collect_top_error_analysis()
            elif not all_bert_contains_answer:
                self._collect_all_bert_error_analysis()

        self.log("Top answers:")

        max_answers = 3
        for answer in answers:
            self.log("{}   {}{}".format(Style.BRIGHT, answer, Style.RESET_ALL))
            max_answers -= 1
            if max_answers == 0:
                break
        return answers

    def split_into_sentences_add(self, text):
        caps = "([A-Z])"
        prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
        suffixes = "(Inc|Ltd|Jr|Sr|Co)"
        starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
        acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
        websites = "[.](com|net|org|io|gov)"
        text = " " + text + "  "
        text = text.replace("\n", " ")
        text = re.sub(prefixes, "\\1<prd>", text)
        text = re.sub(websites, "<prd>\\1", text)
        if "Ph.D" in text: text = text.replace("Ph.D.", "Ph<prd>D<prd>")
        text = re.sub("\s" + caps + "[.] ", " \\1<prd> ", text)
        text = re.sub(acronyms + " " + starters, "\\1<stop> \\2", text)
        text = re.sub(caps + "[.]" + caps + "[.]" + caps + "[.]", "\\1<prd>\\2<prd>\\3<prd>", text)
        text = re.sub(caps + "[.]" + caps + "[.]", "\\1<prd>\\2<prd>", text)
        text = re.sub(" " + suffixes + "[.] " + starters, " \\1<stop> \\2", text)
        text = re.sub(" " + suffixes + "[.]", " \\1<prd>", text)
        text = re.sub(" " + caps + "[.]", " \\1<prd>", text)
        if "”" in text: text = text.replace(".”", "”.")
        if "\"" in text: text = text.replace(".\"", "\".")
        if "!" in text: text = text.replace("!\"", "\"!")
        if "?" in text: text = text.replace("?\"", "\"?")
        text = text.replace(".", ".<stop>")
        text = text.replace("?", "?<stop>")
        text = text.replace("!", "!<stop>")
        text = text.replace("<prd>", ".")
        sentences = text.split("<stop>")
        sentences = sentences[:-1]
        sentences = [s.strip() for s in sentences]
        return sentences
