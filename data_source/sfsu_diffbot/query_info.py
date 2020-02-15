from data_source.sfsu_diffbot.term_info import Term
class QueryInfo(object):
    def __init__(self, info_metadata):
        self._query_info = info_metadata


    def _field(self, key):
        if self._query_info and key in self._query_info:
            return self._query_info[key]

    def fullQuery(self):
        return self._field('fullQuery')

    def language(self):
        return self._field('queryLanguage')

    def num_terms_used(self):
        return self._field('queryNumTermsUsed')

    def num_terms_truncated(self):
        return self._field('queryWasTruncated')

    def terms(self):
        terms = []
        if self._field('terms'):
            for term in self._field('terms'):
                terms.append(Term(term))
            return terms

    def term(self, term):
        terms = self.terms()
        for tmp_term in terms:
            if tmp_term.to_str() == term:
                return tmp_term

    def meta_data(self):
        return self._query_info




