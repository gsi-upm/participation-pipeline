import luigi
from luigi.contrib.esindex import CopyToIndex
from soneti_tasks.SenpyAnalysis import SenpyAnalysis
from soneti_tasks.GSICrawlerScraper import GSICrawlerScraper
from soneti_tasks.CopyToFuseki import CopyToFuseki
from gsitk.preprocess import pprocess_twitter
from utils import annotate_ideology, geolocate, liwc_annotations, mft_annotations
import requests
import json
import time
from elasticsearch.helpers import bulk
import os


###############
# SCRAPY TASK #
###############

class ScrapyTask(GSICrawlerScraper):

    id = luigi.Parameter()
    query = luigi.Parameter()
    number = luigi.Parameter()
    source = luigi.Parameter()
    library = luigi.Parameter()
    before = luigi.Parameter()
    after = luigi.Parameter()
    keep = luigi.Parameter(default=False)
    host = os.environ['GSICRAWLER_URL']

    def run(self):
        """
        Run analysis task 
        """
        with self.output().open('w') as outfile:

            url = '{host}/scrapers/{source}'.format(host=self.host, source=self.source)
            params = {
                "query": self.query,
                "number": self.number,
                "output": self.taskoutput,
                "esendpoint": self.esendpoint,
                "index": self.index,
                "doctype": self.doctype,
                "querytype": self.querytype,
                "keep": self.keep,
                "library": self.library,
                "before": self.before,
                "after": self.after
            }

            # Request sent to GSICrawler
            r = requests.get(url, params=params)

            if 'results' not in r.json():
                url = self.host+'/tasks/'+r.json()['task_id']
                while(r.json()["status"] != "SUCCESS"):
                    if r.json()["status"] == 500:
                        break

                    time.sleep(5)
                    r = requests.get(url)
            
            results = r.json()["results"]

            # Filter languages
            languages = ['en', 'de', 'es']
            results = list(filter(lambda tweet: tweet['schema:inLanguage'] in languages, results))

            # Annotate ideology and narrative
            results = annotate_ideology(results)

            outfile.write(json.dumps(results))

    def output(self):
        return luigi.LocalTarget(path='/tmp/_scrapy-%s.json' % self.id)


######################
# PREPROCESSING TASK #
######################

class PreprocessingTask(luigi.Task):
    id = luigi.Parameter()
    query = luigi.Parameter()
    number = luigi.Parameter()
    source = luigi.Parameter()
    library = luigi.Parameter()
    before = luigi.Parameter()
    after = luigi.Parameter()

    def output(self):
        return luigi.LocalTarget(path='/tmp/preprocess-%s.json'%self.id)

    def requires(self):
        return ScrapyTask(self.id,self.query,self.number,self.source,self.library,self.before,self.after)

    def run(self):
        with self.input().open('r') as fobj:
            with self.output().open('w') as outfile:
                fobj = json.load(fobj)
                results = []
                for tweet in fobj:
                    tweet['schema:articleBody'] = pprocess_twitter.preprocess(tweet['schema:articleBody'])
                    results.append(tweet)
                json.dump(results, outfile)



########################
# GEO ANNOTATIONS TASK #
########################

class GeoTask(luigi.Task):

    id = luigi.Parameter()
    query = luigi.Parameter()
    number =luigi.Parameter()
    source = luigi.Parameter()
    lang = luigi.Parameter()
    library = luigi.Parameter()
    before = luigi.Parameter()
    after = luigi.Parameter()

    def requires(self):
        return PreprocessingTask(self.id,self.query,self.number,self.source,self.library,self.before,self.after)
        
    def run(self):
        """
        Run analysis task 
        """
        with self.input().open('r') as fobj:
            with self.output().open('w') as outfile:
                fobj = json.load(fobj)
                results = []
                for i in fobj:

                    if 'schema:locationCreated' in i:
                        location, country = geolocate(i['schema:locationCreated'])
                        if location:
                            i['location'] = { 
                                'lat': location[0],
                                'lon': location[1]
                            }
                        if country:
                            i['schema:locationCreated'] = country

                    results.append(i)

                outfile.write(json.dumps(results))
     
    def output(self):
        return luigi.LocalTarget(path='/tmp/geo-%s.json'%self.id)


######################
# LIWC ANALYSIS TASK #
######################

class LIWCTask(SenpyAnalysis):

    id = luigi.Parameter()
    query = luigi.Parameter()
    number =luigi.Parameter()
    source = luigi.Parameter()
    algorithm = luigi.Parameter()
    lang = luigi.Parameter()
    library = luigi.Parameter()
    before = luigi.Parameter()
    after = luigi.Parameter()
    host = os.environ['SENPY_URL']

    def requires(self):
        return GeoTask(self.id,self.query,self.number,self.source,self.lang,self.library,self.before,self.after)

    def run(self):
        """
        Run analysis task 
        """
        with self.input().open('r') as fobj:
            with self.output().open('w') as outfile:
                fobj = json.load(fobj)
                results = []
                for i in fobj:
                    b = {}
                    b['@id'] = i['@id']
                    b['@type'] = i['@type']
                    b['_id'] = i['@id']
                    b['marl:hasOpinion'] = i['marl:hasOpinion']
                    
                    r = requests.post(self.host, data={'i':i[self.fieldName], 'apiKey': self.apiKey, 'algo': self.algorithm, 'lang': i["schema:inLanguage"]})
                    time.sleep(self.timeout)
                    i.update(r.json()["entries"][0])
                    i.update(b)

                    i = liwc_annotations(i, r.json()["entries"][0])
                    results.append(i)
                    # outfile.write(json.dumps(i, ensure_ascii=False))
                    # outfile.write('\n')
                outfile.write(json.dumps(results))

    def output(self):
        return luigi.LocalTarget(path='/tmp/liwc-%s.json'%self.id)


######################
# MFT ANALYSIS TASK #
######################

class MFTTask(SenpyAnalysis):

    id = luigi.Parameter()
    query = luigi.Parameter()
    number =luigi.Parameter()
    source = luigi.Parameter()
    algorithm = luigi.Parameter()
    lang = luigi.Parameter()
    library = luigi.Parameter()
    before = luigi.Parameter()
    after = luigi.Parameter()
    host = os.environ['SENPY_URL']

    def requires(self):
        return LIWCTask(self.id,self.query,self.number,self.source,'liwc',self.lang,self.library,self.before,self.after)

    def run(self):
        """
        Run analysis task 
        """
        with self.input().open('r') as fobj:
            with self.output().open('w') as outfile:
                fobj = json.load(fobj)
                for i in fobj:
                    b = {}
                    b['@id'] = i['@id']
                    b['@type'] = i['@type']
                    b['_id'] = i['@id']
                    b['marl:hasOpinion'] = i['marl:hasOpinion']
                    
                    r = requests.post(self.host, data={'i':i[self.fieldName], 'apiKey': self.apiKey, 'algo': self.algorithm})
                    time.sleep(self.timeout)
                    i.update(r.json()["entries"][0])
                    i.update(b)

                    i = mft_annotations(i, r.json()["entries"][0])
                    print(i)

                    outfile.write(json.dumps(i, ensure_ascii=False))
                    outfile.write('\n')

    def output(self):
        return luigi.LocalTarget(path='/tmp/mft-%s.json'%self.id)


###############
# FUSEKI TASK #
###############

class FusekiTask(CopyToFuseki):
    
    id = luigi.Parameter()
    query = luigi.Parameter()
    number = luigi.Parameter()
    source = luigi.Parameter()
    algorithm = luigi.Parameter()
    lang = luigi.Parameter()
    library = luigi.Parameter()
    before = luigi.Parameter()
    after = luigi.Parameter()
    host = os.environ['FUSEKI_URL']
    port = os.environ['FUSEKI_PORT']

    def requires(self):
        return MFTTask(self.id,self.query,self.number,self.source,'mft',self.lang,self.library,self.before,self.after)
        
    def output(self):
        return luigi.LocalTarget(path='/tmp/_n3-%s.json' % self.id)

    def run(self):
        """
        Run indexing to Fuseki task 
        """
        f = []

        with self.input().open('r') as infile:
            with self.output().open('w') as outfile:
                for i, line in enumerate(infile):
                    self.set_status_message("Lines read: %d" % i)
                    w = json.loads(line)
                    #print(w)
                    f.append(w)
                
                for i in f:
                    i.pop('_id')
                    i.pop('radar_social')
                    i.pop('radar_drives')
                    i.pop('radar_affective')
                    i.pop('radar_concerns')
                    i.pop('radar')
                    i.pop('word_count')
                    i.pop('liwc:result')
                    i.pop('ideology')
                    i.pop('narrative')
                    i.pop('counter-narrative')
                    i.pop('alternative-narrative')

                    if 'location' in i: i.pop('location')

                    if 'Religious' in i: i.pop('Religious')
                    if 'Far right' in i: i.pop('Far right')
                    if 'Far left' in i: i.pop('Far left')
                    if 'Separatism' in i: i.pop('Separatism')

                f = json.dumps(f, indent=3)
                self.set_status_message("JSON created")
                print(f)
                #g = Graph().parse(data=f, format='json-ld')
                r = requests.put('http://{fuseki}:{port}/{dataset}/data'.format(fuseki=self.host,
                                                                                port=self.port, dataset = self.dataset),
                    headers={'Content-Type':'application/ld+json'},
                    data=f)
                self.set_status_message("Data sent to fuseki")
                outfile.write(f)


######################
# ELASTICSEARCH TASK #
######################

class ElasticsearchTask(CopyToIndex):
    
    id = luigi.Parameter()
    query = luigi.Parameter()
    number = luigi.Parameter()
    source = luigi.Parameter()
    algorithm = luigi.Parameter()
    lang = luigi.Parameter()
    index = 'participation'
    doc_type = luigi.Parameter()
    library = luigi.Parameter()
    before = luigi.Parameter()
    after = luigi.Parameter()
    host = os.environ['ES_URL']
    port = os.environ['ES_PORT']
    http_auth = (os.environ['ES_USER'],os.environ['ES_PASSWORD'])
    timeout = 100

    def requires(self):
        return MFTTask(self.id,self.query,self.number,self.source,'mft',self.lang,self.library,self.before,self.after)



class StoreTask(luigi.Task):

    id = luigi.Parameter()
    query = luigi.Parameter()
    number = luigi.Parameter()
    source = luigi.Parameter()
    algorithm = luigi.Parameter()
    lang = luigi.Parameter()
    library = luigi.Parameter()
    before = luigi.Parameter(None)
    after = luigi.Parameter(None)
    doc_type = luigi.Parameter(default='_doc')


    def requires(self):
        yield FusekiTask(self.id, self.query, self.number, self.source, self.algorithm,self.lang,self.library,self.before,self.after)
        yield ElasticsearchTask(self.id, self.query, self.number, self.source, self.algorithm,self.lang,self.doc_type,self.library,self.before,self.after)
