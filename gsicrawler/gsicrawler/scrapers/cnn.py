import requests
import json
import re
from unidecode import unidecode
from newsapi import NewsApiClient
from newspaper import Article
from datetime import datetime,timedelta
import os

def preprocessing(text):
	text= re.sub(r'(?:\s{2,})',' ',text)
	text=re.sub('\n\n','\n',text)
	text=unidecode(text)
	return(text)

def retrieveCnnNews(search,date_str):

	key=os.environ.get('NEWS_API_KEY')

	newsapi = NewsApiClient(api_key=key) #We are using NewsAPI https://newsapi.org/

	articles = newsapi.get_everything(q=search,
											sources='cnn',
											from_param=date_str,
											language='en',
											sort_by='relevancy')

	news=[]
	for article in articles['articles']:
		#if 'news' in article['url']:
		aux = {}
		a = Article(article['url'])
		a.download()
		a.parse()
		aux["@type"] = "schema:NewsArticle"
		aux["@id"] = article['url']
		aux["_id"] = article['url']
		aux["schema:datePublished"] =article['publishedAt']
		#aux["schema:dateModified"] = a.publish_date
		aux["schema:articleBody"] = preprocessing(a.text)
		aux["schema:about"] =a.keywords
		aux["schema:author"] = 'http://dbpedia.org/resource/CNN'
		aux["schema:headline"] =  article['title']
		#print(a.text)
		aux["schema:search"] = search
		aux["schema:thumbnailUrl"] = article['urlToImage']
		news.append(aux)

	return news

