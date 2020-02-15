import json
import urllib
import urllib.parse
import urllib.request
from googleapiclient.discovery import build
from colorama import init
init() # colorama needed for Windows
from colorama import Fore, Back, Style

class GKGAPI(object):
    # API: AIzaSyCbMTpFVwvAzdUXSl8R5qqdRk26JozGu_o

    def __init__(self, api_key, queries= None):
        self._key = api_key
        self._queries = queries
        self.Q_COLOR = Fore.CYAN

    def client(self):
        return self.getService()

    def set_queries(self, queries):
        self._queries = queries

    def remove_duplicates(self, queries):
        seen = set()
        seen_add = seen.add
        return [x for x in queries if not (x in seen or seen_add(x))]

    def parsed_query(self, query):
        query_tokens = []
        parts = query.split()
        seq_started = False
        for part in parts:
            if '"' in part:
                part = part.replace('"', "")
                if seq_started == False:

                    seq_started = True
                else:
                    seq_started = False
                query_tokens.append(part)
            if seq_started:
                query_tokens.append(part)
        q_parsed = " ".join(list(self.remove_duplicates(query_tokens)))
        return q_parsed

    def getService(self):
        service = build("customsearch", "v1",
                        developerKey="AIzaSyCbMTpFVwvAzdUXSl8R5qqdRk26JozGu_o")
        return service



    def object(self, query, limit=10, entitiy_type=None):
        tags = []
        self._service_url = 'https://kgsearch.googleapis.com/v1/entities:search'
        self._params = {'query': query, 'limit': limit, 'indent': True, 'key': self._key}

        # named entity search
        if entitiy_type != None:
            self._params['types'] = entitiy_type

        # noinspection PyUnresolvedReferences
        self._url = self._service_url + '?' + urllib.parse.urlencode(self._params)
        try:
            response = json.loads(urllib.request.urlopen(self._url).read())
            for index, element in enumerate(response['itemListElement']):
                if "detailedDescription" in element['result'] and element['result']['detailedDescription']['articleBody'] not in tags:
                    tags.append({"description": element['result']['detailedDescription']['articleBody'],
                                 "score": element['resultScore'], "name": element['result']['name']})
                    self.log("   candidate {}: {}".format(index, element['result']['detailedDescription']['articleBody']))
                elif "description" in element['result'] and element['result']["description"] not in tags:
                    tags.append({"description": element['result']['description'], "score": element['resultScore'],
                                 "name": element['result']['name']})
                    self.log("   candidate {}: {}".format(index, element['result']['description']))
        except:
            return tags
        return tags

    def log(self, text):
        print("[{}] {}".format("DSOEM", text))

    def objects(self):
        objs = []
        for query in self._queries:
            self.log("Using Google KG Search API (https://kgsearch.googleapis.com/v1/entities:search) for boolean query {}{}{}{}".format(self.Q_COLOR,
                                                             Style.BRIGHT,
                                                             query,
                                                             Style.RESET_ALL))

            object = self.object(query)
            objs.append((object, self.get_object_score(object), self.get_object_tags_count(object)))
        return objs

    def kg_search(self, named_entity):
        objs = []

        self.log(
            "Using Google KG Search API (https://kgsearch.googleapis.com/v1/entities:search) for named entity {}{}{}{} of type {}".format(
                self.Q_COLOR,
                Style.BRIGHT,
                named_entity[0],
                Style.RESET_ALL,
                named_entity[1]))

        object = self.object(named_entity[0], limit=10, entitiy_type=named_entity[1])
        objs.append((object, self.get_object_score(object), self.get_object_tags_count(object)))
        return objs

    def get_tag_score(self, tag):
        return tag["score"]

    def get_tag_name(self, tag):
        return tag["name"]

    def get_tag_description(self, tag):
        return tag["description"]

    def get_object_score(self, object):
        scores = 0.00
        n_tags = len(object)
        for tag in object:
            score = self.get_tag_score(tag)
            scores += score
        if n_tags == 0:
            return 0.00
        return scores / n_tags

    def get_num_tags(self, object):
        return len(object)

    def get_tag_count(self, entities, tag):
        count = 0
        text = self.get_tag_description(tag)
        tokens = text.split()
        for entity in entities:
            if entity in tokens:
                count += 1
        return count

    def get_object_tags_count(self, object):
        count = 0.00
        num_tags = len(object)
        for tag in object:
            entities = self.get_tag_name(tag).split()
            count += self.get_tag_count(entities, tag)
        if num_tags == 0:
            return 0.00
        return count / num_tags

    def client_instance(self):
        return "gkg"

    def contents(self, query):
        return urllib.request.urlopen(
            "https://www.googleapis.com/customsearch/v1?key=AIzaSyCbMTpFVwvAzdUXSl8R5qqdRk26JozGu_o&cx=017576662512468239146:omuauf_lfve&q=Mount+McKinley").read()




