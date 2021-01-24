from data_source.data_source_object import *


class GoogleKGObject(DataSourceObject):
    def __init__(self, object_with_fields):
        super(GoogleKGObject, self).__init__(object_with_fields)

    def humanLanguage(self):
        return 'en'

    def text(self):
        return self.object_value('text')

    def url(self):
        return self.object_value('url')

class GoogleKGContent:
    def __init__(self, json_response):
        self._response = json_response

    def hits(self):
        # TODO investigate using Google's resultScore field to represent the hits
        return 0

    def objects(self):
        objs = []
        for index, element in enumerate(self._response['itemListElement']):
            if "detailedDescription" in element['result'] and element['result']['detailedDescription']['articleBody']:
                objs.append(GoogleKGObject({"text": element['result']['detailedDescription']['articleBody'],
                                            "url": element['result']['detailedDescription']['url'],
                             "score": element['resultScore'], "name": element['result']['name']}))
                self.log("   candidate {}: {}".format(index, element['result']['detailedDescription']['articleBody']))
        return objs

    def log(self, text):
        print("[{}] {}".format("DSOEM", text))