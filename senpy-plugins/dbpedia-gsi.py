from senpy.plugins import AnalysisPlugin
from senpy.models import Response, Entry
import urllib.parse
import requests
import json

class DBpedia(AnalysisPlugin):
    '''
    A plugin to easily use the DBpedia SPARQL endpoint.
    '''
    name = "dbpedia"
    author = "@ggarcia"
    version = "0.1"

    def analyse_entry(self, entry, params):
        self.log.debug('Analysing with the dbpedia plugin.')

        text = urllib.parse.quote(entry.text)
        confidence = 0.3
        print(text)

        params = {
            "text": text,
            "confidence": confidence
        }

        r = requests.get("https://api.dbpedia-spotlight.org/en/annotate", params=params, headers={"Accept":"application/json"}).json()

        entry['entities'] = []
        if 'Resources' in r:
            for resource in r['Resources']:
                resource_id = resource["@URI"]
                resource_name = resource["@URI"].split("/")[-1].replace("_", " ")

                entry['entities'].append(resource_name)

        print(json.dumps(r, indent=3))
        yield entry