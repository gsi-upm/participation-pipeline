
# coding: utf-8

# In[41]:

import requests
import json
import time
from newspaper import Article
from bs4 import BeautifulSoup

def retrieveElPaisNews(search, num):


    s = requests.Session()
    res = s.get('https://elpais.com/buscador/')
    cookies = dict(res.cookies)
    r = s.get('https://elpais.com/buscador/?qt={}&sf=0&np=1&bu=ep&of=html'.format(search), 
                     headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}, 
                     cookies = cookies).text


    # In[43]:

    soup = BeautifulSoup(r, 'html.parser')


    # In[46]:

    print(len(soup.select('.article')))
    news = []
    results = []
    for i, article in enumerate(soup.select('.article')):
        aux = dict()
        aux["@type"] = "schema:NewsArticle"
        #aux['schema:author'] = article.select('.autor')[0].string
        aux['schema:author'] = 'El Pais'
        date = time.strptime(article.select('.fecha')[0].string, "%d/%m/%Y")        
        aux['schema:datePublished'] = str(time.strftime('%Y-%m-%d', date))
        title = article.find('h2')
        aux['schema:headline'] = title.text
        aux["schema:search"] = search
        aux['@id'] = 'https://elpais.com'+title.find('a').get('href')
        news.append(aux)

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