import urllib.request
import re
import os
from newspaper import Article
import requests
from datetime import datetime,timedelta
from unidecode import unidecode
from newsapi import NewsApiClient


def preprocessing(text):
    text= re.sub(r'(?:\s{2,})',' ',text)
    text=re.sub('\n\n','\n',text)
    text=unidecode(text)
    return(text)


def retrieveAlJazeeraNews(query, date_str):

    key=os.environ.get('NEWS_API_KEY')

    newsapi = NewsApiClient(api_key=key) #We are using NewsAPI https://newsapi.org/

    articles = newsapi.get_everything(q=query,
                                      sources='al-jazeera-english',
                                      from_param=date_str,
                                      language='en',
                                      sort_by='relevancy')
    
    #print(articles)
    news=[]
    for article in articles['articles']:
        #if 'news' in article['url']:
        aux = {}
        a = Article(article['url'])
        a.download()
        a.parse()
        aux["@type"] = "schema:NewsArticle"
        aux["@id"] = article['url']
        aux["schema:datePublished"] = article['publishedAt']
        aux["schema:articleBody"] = preprocessing(a.text)
        aux["schema:about"] = a.keywords
        aux["schema:author"] =  'http://dbpedia.org/resource/Al_Jazeera'
        aux["schema:headline"] =  article['title']
        aux["schema:search"] = query
        aux["schema:thumbnailUrl"] = article['urlToImage']
        news.append(aux)

    return news