
# coding: utf-8

import requests
import json
import time
from newspaper import Article
from bs4 import BeautifulSoup

def retrieveElMundoNews(search, num):

    r = requests.get('http://ariadna.elmundo.es/buscador/archivo.html?q={}&b_avanzada=&s=0&n={}'.format(search, num), headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}).text
    soup = BeautifulSoup(r, 'html.parser')

    #print(soup.select('.lista_resultados > li'))
    news =[]
    results = []

    for i, article in enumerate(soup.select('.lista_resultados > li')):
        if i > 0:
            aux = dict()
            aux["@type"] = "schema:NewsArticle"
            #aux['schema:author'] = article.select('.autor')[0].string
            aux['schema:author'] = 'El Mundo'
            date = time.strptime(article.select('.fecha')[0].string, "%d/%m/%Y")        
            aux['schema:datePublished'] = str(time.strftime('%Y-%m-%d', date))
            title = article.find('h3')
            aux['schema:headline'] = title.text
            aux["schema:search"] = search
            aux['@id'] = "http:"+title.find('a').get('href')
            news.append(aux)
            #print(aux)



    for newsitem in news:
        try:
            a = Article(newsitem["@id"])
            a.download()
            a.parse()
            newsitem["schema:articleBody"] = a.text
            results.append(newsitem)
        except:
            pass
    return results