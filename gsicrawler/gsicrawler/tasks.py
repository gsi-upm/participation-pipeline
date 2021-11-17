from celery import Celery
from celery.decorators import periodic_task
from celery.schedules import crontab

from functools import wraps

import json
import os
import math
import time
from itertools import islice
from functools import wraps
import requests
from datetime import timedelta
import datetime
from time import sleep, mktime
#from time import sleep
from celery.utils.log import get_task_logger
from gsicrawler.scrapers.cnn import retrieveCnnNews
from gsicrawler.scrapers.nytimes import retrieveNytimesNews
from gsicrawler.scrapers.twitter import retrieveTweets 
from gsicrawler.scrapers.facebook import getFBPageFeedData
from gsicrawler.scrapers.elmundo import retrieveElMundoNews
from gsicrawler.scrapers.elpais import retrieveElPaisNews
from gsicrawler.scrapers.tripadvisor import retrieveTripadvisorReviews
from gsicrawler.scrapers.aljazeera import retrieveAlJazeeraNews
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

logger = get_task_logger(__name__)

GSICRAWLER_BROKER = os.environ.get('GSICRAWLER_BROKER')
GSICRAWLER_RESULT_BACKEND = os.environ.get('GSICRAWLER_RESULT_BACKEND', GSICRAWLER_BROKER)
# CONFIGURACION PARA DOCKER
config = {}
config['SECRET_KEY'] = 'password'
config['CELERY_BROKER_URL'] = GSICRAWLER_BROKER
config['CELERY_RESULT_BACKEND'] = GSICRAWLER_RESULT_BACKEND
celery = Celery("gsicrawler", broker=GSICRAWLER_BROKER)
celery.conf.update(config)


@celery.task
def test_task():
    return 'Not implemented yet'


def crawler(func):
    @wraps(func)
    def func_wrapper(output, esendpoint, index, doctype, **kwargs):
        print(kwargs)
        filepath = "/tmp/"+str(time.time())+".json"
        print(filepath)


        print("Scraping...")
        result = func(**kwargs)
        print(len(result))

        if (output == "elasticsearch"): 
            es = Elasticsearch(hosts=[esendpoint])
            for doc in result:
                id = doc['@id']
                print('Storing {}'.format(id))
                res = es.index(index=index, doc_type=doctype, id=id, body=doc)
                if (res['result']!='created'):
                    print(res['result'])
            return "Check your results at: "+esendpoint+"/"+index+"/_search"
        else:
            return result
    return func_wrapper


@celery.task
@crawler
def twitter_scraper(query, querytype, number, keep, library, before, after):
    return retrieveTweets(querytype, query, number, keep, library, before, after)

@celery.task
@crawler
def tripadvisor_scraper(query, number):
    return retrieveTripadvisorReviews(query, number)

@celery.task
@crawler
def facebook_scraper(query, number):
    return getFBPageFeedData(query, number)

@celery.task
@crawler
def cnn_scraper(query,date):
    return retrieveCnnNews(query,date)

@celery.task
@crawler
def elpais_scraper(query, number):
    return retrieveElPaisNews(query, number)

@celery.task
@crawler
def elmundo_scraper(query, number):
    return retrieveElMundoNews(query, number)

@celery.task
@crawler
def nyt_scraper(query, date):
    return retrieveNytimesNews(query, date)

@celery.task
@crawler
def aljazeera_scraper(query, date):
    return retrieveAlJazeeraNews(query, date)
