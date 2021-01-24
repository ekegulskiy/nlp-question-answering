"""
This file implements the Factoid Multiquery Formulation Module (FMQFM)

Package: fqakg

Author: Eduard Kegulskiy

"""

from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords
from qa_utils import *
from pattern.en import conjugate, lemma, lexeme,PAST,SG
from colorama import init
init() # colorama needed for Windows
from colorama import Fore, Back, Style

class FactoidQueryParser:
    """
        Factoid Query parser which transforms a single user query into multiple search queries aimed to retrieve an
        answer from a search engine such as DiffBot or Google
    """
    QUOTED_TOKEN = "UNIQUEQUOTESTOKENxxExwr"
    HYPHEN_TOKEN = " xxxHYPHENTOKENxxx "
    DOT_TOKEN = "xxxDOTTOKENxxx"
    FULL_PLUS_QUERY = "Full+"
    FULL_PLUS_QUERY_RANK = 0
    MAX_GRAM_SIZE = 5
    POS_QUERY = "POS-based"
    POS_QUERY_RANK = 1
    ONE_GRAM_QUERY = "1-Gram"
    ONE_GRAM_QUERY_RANK = 2
    QUOTED_TEXT_QUERY = "Quoted Text"
    QUOTED_TEXT_QUERY_RANK = 3
    Q_COLOR = Fore.CYAN

    def __init__(self):
        """
        Class constructor

        :returns instance of FactoidQueryParser
        """
        self._user_query = ""
        self._parsed_query = ""
        self._search_queries = []
        self._tweet_tokenizer = TweetTokenizer()
        self._quotes = []
        self._parsed_query_tokens = []
        self._pos_tags = []
        self._full_query = ""
        self._pos_query = ""
        self._quoted_query = ""
        self._1_grams_query = ""
        self._qpm = None
        self._POSTagger = KGQAPOSTagger()

        self._stop_words = set(stopwords.words('english'))
        self._stop_words.update(('Where', 'Who', 'Whose', 'What', 'Why', 'How', 'and', 'I', 'A', 'And', 'So', 'arnt', 'This',
                           'When', 'It', 'many', 'Many', 'so', 'cant', 'whom'
                           'Yes', 'yes', 'No', 'no', 'These', 'these', 'is', 'are', 'Do', "Are", "About", "For", "Is", "\""))
        self._stop_words.remove('own')
        self._stop_words.remove('too')
        self._stop_words.remove('won')
        self._stop_words.remove('in')
        self._stop_words.remove('of')
        self._stop_words.remove('have')
        self._stop_words.remove('has')
        self._stop_words.remove('had')

    def log(self, text):
        print("[{}] {}".format(FMQFM.__qualname__, text))

    # Public methods
    @property
    def query(self):
        return self._user_query

    @query.setter
    def query(self, user_query):
        self._user_query = user_query

    @property
    def qpm(self):
        return self._qpm

    @qpm.setter
    def qpm(self, qpm):
        self._qpm = qpm

    def _replace_factoid_question_words(self):
        """
            Transforms query terms that usually start factoid questions into a terms that represent what an answer
            be like for such a question. For example, if somebody is asking "when was WWII?", the expected answer
            may contain "the date of WWII is..." - so in this case we transformed term "when" into "date".
        :return: None
        """
        if self._parsed_query.lower().startswith("when was"):
            self._parsed_query = self._parsed_query.replace("when was", "")
            self._parsed_query = self._parsed_query.replace("When was", "")

            verbs = self._qpm.query_verbs()
            new_tokens = []
            if len(verbs) == 2: # 'was' and whatever second verb is
                for t in self._parsed_query.split():
                    if t in verbs:
                        new_tokens.append("was "+t)
                    else:
                        new_tokens.append(t)

                self._parsed_query = " ".join(new_tokens)
            self._parsed_query += " in"

        if self._parsed_query.lower().startswith("what year was"):
            self._parsed_query = self._parsed_query.replace("what year was", "")
            self._parsed_query = self._parsed_query.replace("What year was", "")
            self._parsed_query += " in"

        self._parsed_query = self._parsed_query.replace("when were", "date")
        self._parsed_query = self._parsed_query.replace("When were", "date")

        self._parsed_query = self._parsed_query.replace("when is", "date")
        self._parsed_query = self._parsed_query.replace("When is", "date")

        self._parsed_query = self._parsed_query.replace("when are", "date")
        self._parsed_query = self._parsed_query.replace("When are", "date")

        self._parsed_query = self._parsed_query.replace("how long is", "length")
        self._parsed_query = self._parsed_query.replace("How long is", "length")

        self._parsed_query = self._parsed_query.replace("how long are", "length")
        self._parsed_query = self._parsed_query.replace("How long are", "length")

        self._parsed_query = self._parsed_query.replace("how long was", "length")
        self._parsed_query = self._parsed_query.replace("How long was", "length")

        self._parsed_query = self._parsed_query.replace("how long were", "length")
        self._parsed_query = self._parsed_query.replace("How long were", "length")

        self._parsed_query = self._parsed_query.replace("how long does", "duration")
        self._parsed_query = self._parsed_query.replace("How long does", "duration")

        self._parsed_query = self._parsed_query.replace("how long", "estimation")
        self._parsed_query = self._parsed_query.replace("How long", "estimation")

        self._parsed_query = self._parsed_query.replace("How fast", "speed")
        self._parsed_query = self._parsed_query.replace("how fast", "speed")

        self._parsed_query = self._parsed_query.replace("How tall", "height")
        self._parsed_query = self._parsed_query.replace("how tall", "height")

        if self._parsed_query.lower().startswith('how many'):
            simple_set = ['is', 'was', 'are', 'were', 'does', 'do', 'have']
            simple_q = True
            do = False
            verbs = self._qpm.query_verbs()
            for v in verbs:
                if v.lower() in simple_set:
                    if v == 'do':
                        do = True
                    continue
                else:
                    simple_q = False
                    break

            if simple_q:
                self._parsed_query = self._parsed_query.replace("How many", "number of ")
                self._parsed_query = self._parsed_query.replace("how many", "number of ")
                for w in verbs:
                    if w == 'have':
                        if do is True:
                            self._parsed_query = self._parsed_query.replace(w, 'have')
                        else:
                            self._parsed_query = self._parsed_query.replace(w, 'has')
                    else:
                        self._parsed_query = self._parsed_query.replace(w, '')
            else:
                self._parsed_query = self._parsed_query.replace("How many", "number")
                self._parsed_query = self._parsed_query.replace("how many", "number")

        self._parsed_query = self._parsed_query.replace("How much", "amount")
        self._parsed_query = self._parsed_query.replace("how much", "amount")

        self._parsed_query = self._parsed_query.replace("How often does", "frequency")
        self._parsed_query = self._parsed_query.replace("How often is", "frequency")
        self._parsed_query = self._parsed_query.replace("How often was", "frequency")

        self._parsed_query = self._parsed_query.replace("how high is", "height")
        self._parsed_query = self._parsed_query.replace("How high is", "height")
        self._parsed_query = self._parsed_query.replace("how high are", "height")
        self._parsed_query = self._parsed_query.replace("How high are", "height")
        self._parsed_query = self._parsed_query.replace("how high was", "height")
        self._parsed_query = self._parsed_query.replace("How high was", "height")
        self._parsed_query = self._parsed_query.replace("how high were", "height")
        self._parsed_query = self._parsed_query.replace("How high were", "height")

        self._parsed_query = self._parsed_query.replace("how big is", "size")
        self._parsed_query = self._parsed_query.replace("How big is", "size")
        self._parsed_query = self._parsed_query.replace("how big are", "size")
        self._parsed_query = self._parsed_query.replace("How big are", "size")
        self._parsed_query = self._parsed_query.replace("how big was", "size")
        self._parsed_query = self._parsed_query.replace("How big was", "size")
        self._parsed_query = self._parsed_query.replace("how big were", "size")
        self._parsed_query = self._parsed_query.replace("How big were", "size")

    def _process_comas(self):
        """
            Replaces commas with spaces
        :return: None
        """
        self._parsed_query = self._parsed_query.replace(",", " ")

    def generate_search_queries(self):
        """
            generates multiple search queries, aimed to find most relevant answers. The queries are sorted by their ability
            to find the answers, i.e. rank as following:
            Full Query+ reserves as much context as possible so it’s almost identical to original (full) question
            POS-based  The original question is broken into multiple pieces, each being a multi-gram query of variable size.
                        The algorithm for deciding on how to break is based on parts-of-speech (POS)
            1-Gram simple boolean query with 1-gram terms
        :return: list of all generated queries as tuple: (query, query_type, query_rank)
        """
        self._cleanup_previous()
        self._parsed_query = self._user_query

        self._replace_factoid_question_words()
        self._process_comas()
        self._process_quoted_text()
        self._process_dots()
        self._tokenize()

        # Build all queries
        self._full_query = self._build_full_query()
        self._pos_query = self._build_pos_based_query()
        self._build_quotes_query()
        self._build_1_grams_query()

        self._search_queries = self._post_process_queries()
        return self._search_queries

    def _build_pos_tags(self):
        """
            Build parts-of-speech and NER tags
        :return: None
        """
        self._pos_tags, ner_tags = self._POSTagger.tag(self._parsed_query_tokens, ner=False)

    def _post_process_queries(self):
        """
            finalizies all queries, checks for various error conditions and adjusts the results as needed.
            assigns ranks and types to each query and returns them as a list
        :return: list of all generated queries as tuple: (query, query_type, query_rank)
        """
        search_queries = []
        search_queries_staging = []

        # check pos query
        def is_single_gram_query(query):
            for token in query:
                if len(token.split()) > 1:
                    return False

            return True

        def above_gram_limit(query):
            for token in query:
                if len(token.split()) > self.MAX_GRAM_SIZE:
                    return True

            return False

        pos_strategies = [
            (['DT', 'IN'], ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'], [], []),
            (['DT', 'IN'], [], [], ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']),
            (['DT', 'IN'], [], ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'], []),
            (['DT', 'IN'], ['NN'], ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'], [])
        ]

        if self._full_query is None:
            # Since full Query wasn't generated, we use the POS-based query in its place with the rank equal to Full Query
            self._full_query = self._build_pos_based_query()
            index = 0
            num_strategies = len(pos_strategies)
            while (is_single_gram_query(self._full_query) or above_gram_limit(self._full_query)) \
                    and num_strategies > 0:
                self._full_query = self._build_pos_based_query(break_and_remove=pos_strategies[index][0],
                                                              break_and_isolate=pos_strategies[index][1],
                                                              break_on_right=pos_strategies[index][2],
                                                              break_on_left=pos_strategies[index][3])
                num_strategies -= 1
                index += 1

            search_queries_staging.append(self._full_query)
            search_queries.append((self._full_query, FactoidQueryParser.POS_QUERY, FactoidQueryParser.FULL_PLUS_QUERY_RANK))
        else:
            search_queries_staging.append(self._full_query)
            search_queries.append((self._full_query, FactoidQueryParser.FULL_PLUS_QUERY, FactoidQueryParser.FULL_PLUS_QUERY_RANK))

        index = 0
        num_strategies = len(pos_strategies)
        while (is_single_gram_query(self._pos_query) or self._pos_query == self._full_query or above_gram_limit(self._pos_query))\
                and num_strategies > 0:
            self._pos_query = self._build_pos_based_query(break_and_remove=pos_strategies[index][0],
                                        break_and_isolate=pos_strategies[index][1],
                                        break_on_right=pos_strategies[index][2],
                                        break_on_left=pos_strategies[index][3])
            num_strategies -= 1
            index += 1

        if self._pos_query not in search_queries_staging:
            search_queries_staging.append(self._pos_query)
            search_queries.append((self._pos_query, FactoidQueryParser.POS_QUERY, FactoidQueryParser.POS_QUERY_RANK))

        if self._1_grams_query != "" and self._1_grams_query not in search_queries_staging:
            search_queries_staging.append(self._1_grams_query)
            search_queries.append((self._1_grams_query,
                                   FactoidQueryParser.ONE_GRAM_QUERY,
                                   FactoidQueryParser.ONE_GRAM_QUERY_RANK))

        if self._quoted_query != "" and self._quoted_query not in search_queries_staging:
            search_queries_staging.append(self._quoted_query)
            search_queries.append((self._quoted_query,
                                   FactoidQueryParser.QUOTED_TEXT_QUERY,
                                   FactoidQueryParser.QUOTED_TEXT_QUERY_RANK))

        return search_queries

    def _process_dots(self):
        """
            Finds all dots in the user query and replaces them with special token.
            This is done for better tokenization handling since standard tokenizers do not handle dots well. This is
            especially useful for acronyms (e.g. U.S.A. or U.N.)
        :return: None
        """
        prev_char = ""
        dot_indexes = []

        for index, char in enumerate(self._parsed_query):
            if char == '.' and prev_char != " ":
                dot_indexes.append(index)

            prev_char = char

        dot_token_size_adjustment = 0
        for h in dot_indexes:
            dot_pos = h + dot_token_size_adjustment
            first_part = self._parsed_query[:dot_pos]
            second_part = self._parsed_query[dot_pos+1:]
            self._parsed_query = first_part + self.DOT_TOKEN + second_part
            dot_token_size_adjustment += len(self.DOT_TOKEN) - 1

    def _cleanup_previous(self):
        self._search_queries = []
        self._parsed_query_tokens = []
        self._pos_tags = []
        self._full_query = ""
        self._pos_query = ""
        self._quoted_query = ""
        self._1_grams_query = ""

    def _build_quotes_query(self):
        """
            If original query contained quotes, they will all be used to generate separate search queries
        :return: None
        """
        if len(self._quotes) > 0:

            quotes = []
            for q in self._quotes:
                quotes.append(q)

            self._quoted_query = quotes

    def _build_1_grams_query(self):
        """
            Builds boolean query where each item contains exactly 1 term. This contains most of original question terms
            minus question beginning words
        :return: None
        """
        queries = []
        next_quote = 0
        for token in self._parsed_query_tokens:
            if token in self._stop_words:
                continue
            elif token == FactoidQueryParser.QUOTED_TOKEN:
                quoted_token = self._quotes[next_quote].split()
                for t in quoted_token:
                    processed_token = t.replace(self.DOT_TOKEN, ".")
                    queries.append(processed_token)
                next_quote += 1
            else:
                processed_token = token.replace(self.DOT_TOKEN, ".")
                queries.append(processed_token)

        self._1_grams_query = queries

    def _build_full_query(self):
        """
            Builds a search query which contains most of the original question terms (minus question beginning terms)
        :return: full query
        """
        queries = []
        full_query = None
        sentence = " ".join(self._parsed_query_tokens).replace(".", "")
        for q in self._quotes:
            sentence = sentence.replace(FactoidQueryParser.QUOTED_TOKEN, q, 1)

        sentence = sentence.replace(self.DOT_TOKEN, ".")
        if len(sentence.split()) > self.MAX_GRAM_SIZE:
            full_query = None
        else:
            queries.append(sentence)
            full_query = queries

        return full_query

    def _build_pos_based_query(self, break_and_remove=['WDT'],
                               break_and_isolate=['NNP', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'],
                               break_on_right=[],
                               break_on_left=[]):
        """
            Build boolean search query consisting of multiple N-gram queries, based on part-of-speech
        :param break_and_remove: list of POS tags which will be used as term boundary for next N-gram query. The term itself will be removed from the query.
        :param break_and_isolate: list of POS tags which will be used as term boundary for next N-gram query. The term itself will be put into isolated N-gram query.
        :param break_on_right: list of POS tags which will be used as term boundary for next N-gram query. The term itself will be kept in the current N-gram query
        :param break_on_left: list of POS tags which will be used as term boundary for next N-gram query. The term itself will be moved into the next N-gram query
        :return: POS search query
        """
        cur_token = ""
        pos_tokens = []
        adjectives = ['JJ', 'JJR', 'JJS']
        prev_POS = ''
        pos_tags_length = len(self._pos_tags)

        for index, tag in enumerate(self._pos_tags):
            if tag[0] == FactoidQueryParser.QUOTED_TOKEN:
                continue # skip quoted tokens since they will be added later
            if tag[1] in break_and_remove:
                if cur_token != "":
                    pos_tokens.append(cur_token.strip().replace(".", ""))
                cur_token = ""
            elif tag[1] in break_and_isolate and \
                    not (tag[1] == 'NN' and prev_POS in adjectives):
                if cur_token != "":
                    pos_tokens.append(cur_token.strip().replace(".", ""))
                if index == pos_tags_length-2 and self._pos_tags[pos_tags_length-1][1] == 'IN':
                    cur_token = tag[0]
                else:
                    pos_tokens.append(tag[0].strip().replace(".", ""))
                    cur_token = ""
            elif tag[1] in break_on_right:
                if tag[1] != "POS":
                    cur_token += " "  # only add a space if it's not the possessive ending parent’s
                cur_token += tag[0]
                if cur_token != "":
                    pos_tokens.append(cur_token.strip().replace(".", ""))
                cur_token = ""
            elif tag[1] in break_on_left:
                if cur_token != "":
                    pos_tokens.append(cur_token.strip().replace(".", ""))
                cur_token = tag[0]
            else:
                if tag[1] != "POS":
                    cur_token += " "  # only add a space if it's not the possessive ending parent’s
                cur_token += tag[0]

            prev_POS = tag[1]

        # add last token
        if cur_token != "":
            pos_tokens.append(cur_token.strip().replace(".", ""))

        for q in self._quotes:
            pos_tokens.append(q)

        #process DOTS if any
        for i, token in enumerate(pos_tokens):
            pos_tokens[i] = pos_tokens[i].replace(self.DOT_TOKEN, '.')

        pos_tokens_copy = pos_tokens
        pos_tokens = []

        def is_all_stop_words(sentence):
            for t in sentence.split():
                if t not in self._stop_words:
                    return False

            return True
        # remove carefully any 'the and 'a' if the query gram ends with it
        for t in pos_tokens_copy:
            if is_all_stop_words(t):
                continue
            else:
                if t.endswith(" the"):
                    t = t[0:t.rfind(" the")]
                elif t.endswith(" a"):
                    t = t[0:t.rfind(" a")]
                pos_tokens.append(t)

        return pos_tokens

    def _process_quoted_text(self):
        """
            Finds all double and single - quotes in the user query and replaces them with special token.
            This is done for better tokenization handling since standard tokenizers do not handle quoted text well.
        :return: None
        """

        if True:
            self._quotes = []
            processed_query = ''
            potential_quote = ''
            potential_quote_started = False
            prev_c = ''
            SPACE = ' '
            QUOTE_CHARS = ['\'', '\"', '`']
            for index, c in enumerate(self._parsed_query):
                next_char = ''
                if index < len(self._parsed_query)-1:
                    next_char = self._parsed_query[index+1]

                if c in QUOTE_CHARS:
                    if potential_quote_started:
                        if next_char == SPACE or next_char == '':
                            # complete it
                            potential_quote_started = False
                            self._quotes.append(potential_quote)
                            potential_quote = ''
                            processed_query += FactoidQueryParser.QUOTED_TOKEN
                        else:
                            potential_quote += c
                    elif prev_c == SPACE or prev_c == '' or prev_c == '.':
                        potential_quote_started = True
                    else:
                        processed_query += c
                elif potential_quote_started:
                    potential_quote += c
                else:
                    processed_query += c

                prev_c = c
            # left over
            if potential_quote != '':
                processed_query += potential_quote

            if processed_query != '':
                self._parsed_query = processed_query


    def _remove_name_tokens(self):
        """
            Removes terms from user query that are asking about the name. This is a special case since expected answer
            won't usually contain any of these terms.
        :return: None
        """
        self._parsed_query = self._parsed_query.replace("What was the name of", '')
        self._parsed_query = self._parsed_query.replace("What was the name of the", '')
        self._parsed_query = self._parsed_query.replace("What was the name of a", '')
        self._parsed_query = self._parsed_query.replace("What is the name of", '')
        self._parsed_query = self._parsed_query.replace("What is the name of the", '')
        self._parsed_query = self._parsed_query.replace("What is the name of a", '')

    def _remove_begin_pairs_tokens(self):
        """
            Remove terms that start with a special pair "for whom". The reasoning being that answers to such questions
            usually won't contain these terms.
        :return: None
        """
        if self._parsed_query.startswith('For whom') or \
                self._parsed_query.startswith('for whom'):
            self._parsed_query = self._parsed_query.replace("For whom was", '')
            self._parsed_query = self._parsed_query.replace("for whom was", '')
            self._parsed_query = self._parsed_query.replace("For whom is", '')
            self._parsed_query = self._parsed_query.replace("for whom is", '')
            self._parsed_query = self._parsed_query.replace("For whom are", '')
            self._parsed_query = self._parsed_query.replace("for whom are", '')

    def _remove_stop_words(self):
        """
            Remove a very small set of stop words from the beginning of the query. The reason we keep all other stop
            words since they help preserve the context of the question better.
        :return: None
        """
        if self._parsed_query_tokens[0] == 'the':
            self._parsed_query_tokens.pop(0)


    def _tokenize(self):
        """
            transform the query into search query for finding expected answer and tokenize it
        :return:
        """
        self._remove_name_tokens()
        self._remove_begin_pairs_tokens()
        self._remove_begin_question_tokens()
        self._remove_stop_words()
        self._process_does_verb()

        self.log("Transforming question terms into likely answer form: {}{}{}{}".format(self.Q_COLOR,
                                                                                        Style.BRIGHT,
                                                                                        " ".join(self._parsed_query_tokens),
                                                                                        Style.RESET_ALL))

        self._build_pos_tags()
        self._process_past_tense()

        self.log("Tokenizing the query: {}{}{}{}".format(self.Q_COLOR,
                                                         Style.BRIGHT,
                                                         self._parsed_query_tokens,
                                                         Style.RESET_ALL))

    def _process_does_verb(self):
        """
            When user question contains 'does' verb, we transform verbs of the question into proper tense by adding 's'
            to them - this helps to find better answers
        :return:
        """
        verbs = self._qpm.query_verbs()
        if len(verbs) == 2 and verbs[0].lower() == "does":  # 'does' and whatever second verb is
            new_tokens = []
            for t in self._parsed_query_tokens:
                if t == "does":
                    continue
                elif t in verbs:
                    new_tokens.append(t + "s")
                else:
                    new_tokens.append(t)

            self._parsed_query_tokens = new_tokens

    def _process_past_tense(self):
        """
            Detects if the question being asked is in the PAST tense and transforms the verbs of the question into PAST
            tense - helps to find more relevant answers
        :return: None
        """
        verbs = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
        force_verbs = ['open']

        def past_tence(v):
            if v == 'bite':
                return 'bitten'
            elif v == 'found':
                return 'founded'
            return conjugate(verb=v, tense=PAST, number=SG) # he / she / it

        is_past_tense = False
        past_tense_determiner_index = 0
        for index, token in enumerate(self._parsed_query_tokens):
            if token == "did":
                is_past_tense = True
                past_tense_determiner_index = index
                break

        if is_past_tense:
            del self._pos_tags[past_tense_determiner_index]
            for index, tag in enumerate(self._pos_tags):
               if self._pos_tags[index][1] in verbs or self._pos_tags[index][0] in force_verbs:
                   self._pos_tags[index] = (past_tence(self._pos_tags[index][0]), self._pos_tags[index][1])

            self._parsed_query_tokens = list(map(lambda x: x[0], self._pos_tags))

    def _remove_begin_question_tokens(self):
        """
            Remove general question words that usually start factoid questions. The reasoning is that answers to such
            questions usually won't contain these words.
        :return: None
        """
        tokens = self._tweet_tokenizer.tokenize(self._parsed_query)

        factoid_start_tokens = ['What', 'How', 'When', 'Who', 'Where', 'Why', 'Which',
                                'what', 'how', 'when', 'who', 'where', 'why', 'which']
        factoid_start_found = False
        for index, token in enumerate(tokens):
            if index == 0:
                if token in factoid_start_tokens:
                    factoid_start_found = True
                    continue
            if factoid_start_found:
                if index == 1:
                    if token.casefold() == "is".casefold() or token.casefold() == "was".casefold() or \
                            token.casefold() == "are".casefold() or token.casefold() == "were".casefold():
                        continue

            self._parsed_query_tokens.append(token.strip())


class FMQFM(object):
    """
        FMQFM module generates search queries that are optimized to retrieve the best objects with Diffbot Search API
    """
    fquery_parser = FactoidQueryParser()

    def __init__(self, qpm):
        """
        Class constructor.
        :param qpm QPM Module of FQAKG pipeline containing user question for which an answer needs to be retrieved
        """

        print("")
        self.log("{}MODULE 2: FACTOID MULTI-QUERY FORMULATION MODULE{}".format(Style.BRIGHT, Style.RESET_ALL))

        self._original_q = qpm.free_text()
        self._multiquery_list = []
        self._qpm = qpm
        self.Q_COLOR = Fore.CYAN

        FMQFM.fquery_parser.query = self.original_question()
        FMQFM.fquery_parser.qpm = self._qpm
        self._multiquery_list = FMQFM.fquery_parser.generate_search_queries()

        self.log("Building ranked search queries:")
        for q in self._multiquery_list:
            self.log("  [{}, rank={}]: {}{}{}{}".format(q[1], q[2], self.Q_COLOR,
                                                                    Style.BRIGHT,
                                                                    q[0],
                                                                    Style.RESET_ALL))

    def log(self, text):
        print("[{}] {}".format(FMQFM.__qualname__, text))

    def original_question(self):
        return self._original_q

    def multiquery(self):
        """

        :return: list of search queries that are optimized to retreive an answer to the user question passed via QPM module
        """
        return self._multiquery_list
