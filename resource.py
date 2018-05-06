import codecs
import json

class Resource:
    resource = {}

    @staticmethod
    def load(filename):
        with codecs.open(filename, 'r', 'utf-8') as jsonfile:
            Resource.resource = json.load(jsonfile)

    @staticmethod
    def res(key):
        return Resource.resource[key] if key in Resource.resource else key
