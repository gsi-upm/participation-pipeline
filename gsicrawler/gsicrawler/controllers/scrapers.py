from flask import current_app
from gsicrawler.utils import add_metadata
import json
import celery
from functools import wraps


def scraper(source):
    def outer(func):
        @wraps(func)
        def inner(esendpoint=None, doctype=source, index='gsicrawler', timeout=1, **kwargs):

            response = {'parameters': kwargs, 'source': source}
            try:
                task = func().delay(esendpoint=esendpoint, doctype=doctype, index=index, **kwargs)
                response['task_id'] = task.id
                results = task.get(timeout=timeout)
                response['results'] = results
                response['status'] = task.state
                return response, 200
            except celery.exceptions.TimeoutError:
                response['status'] = task.state
                return response, 202
            except Exception as ex:
                response['status'] = 'ERROR'
                response['error'] = str(ex)
                return response, 500
        return inner
    return outer


@scraper('Twitter')
def twitter_scraper(**kwargs):
    return current_app.tasks.twitter_scraper

@scraper('Tripadvisor')
def tripadvisor_scraper(**kwargs):
    return current_app.tasks.tripadvisor_scraper

@scraper('Facebook')
def facebook_scraper(**kwargs):
    return current_app.tasks.facebook_scraper

@scraper('CNN')
def cnn_scraper(**kwargs):
    return current_app.tasks.cnn_scraper

@scraper('ElPais')
def elpais_scraper(**kwargs):
    return current_app.tasks.elpais_scraper

@scraper('ElMundo')
def elmundo_scraper(**kwargs):
    return current_app.tasks.elmundo_scraper

@scraper('NYTimes')
def nyt_scraper(**kwargs):
    return current_app.tasks.nyt_scraper

@scraper('AlJazeera')
def aljazeera_scraper(**kwargs):
    return current_app.tasks.aljazeera_scraper
