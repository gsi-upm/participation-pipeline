import requests
import json
from newspaper import Article
import re
from datetime import datetime,timedelta
from nytimesarticle import articleAPI
import os
from unidecode import unidecode



def preprocessing(text):
	text= re.sub(r'(?:\s{2,})',' ',text)
	text=re.sub('\n\n','\n',text)
	text=unidecode(text)
	return(text)


def retrieveNytimesNews(search,date_str):

	key=os.environ.get('NY_TIMES_API_KEY')
	
	date_object = datetime.strptime(date_str,'%Y-%m-%d')
	date=date_object.strftime("%Y%m%d")

	api = articleAPI(key)
	articles = api.search( q = search, begin_date = int(date))

	news = []
	for newsitem in articles['response']['docs']:
		if newsitem["source"] != "Internet Video Archive":
			aux = dict()
			aux["@type"] = "schema:NewsArticle"
			aux["@id"] = newsitem["web_url"]
			aux["_id"] = newsitem["web_url"]
			aux["schema:datePublished"] = newsitem["pub_date"]
			aux["schema:dateModified"] = newsitem["pub_date"]
			aux["schema:articleBody"] = "articletext"
			aux["schema:about"] = [key["value"] for key in newsitem["keywords"]]
			aux["schema:author"] = 'http://dbpedia.org/resource/The_New_York_Times'
			aux["schema:headline"] = preprocessing(newsitem["headline"]["main"])
			aux["schema:search"] = search
			if (len(newsitem["multimedia"]) > 0):
				aux["schema:thumbnailUrl"] = "https://www.nytimes.com/" + newsitem["multimedia"][0]["url"]
			else: 
				aux["schema:thumbnailUrl"] = "https://www.neto.com.au/assets/images/default_product.gif"
			news.append(aux)

	for newsitem in news:
		a = Article(newsitem["@id"])
		a.download()
		a.parse()
		newsitem["schema:articleBody"] = preprocessing(a.text)
			
	return(news)



