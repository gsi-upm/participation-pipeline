#!/usr/bin/env python

import requests
import time
import os


# I generate the access_token by creating an empty Facebook App which gives me
# the app_id and app_secret needed.
# app_id = os.environ['FACEBOOK_APP_ID']
# app_secret= os.environ['FACEBOOK_APP_SECRET']
# Concatening them I am sure it won`t expire.
# access_token= app_id + "|" + app_secret
access_token = os.environ.get('FACEBOOK_ACCESS_TOKEN')


# We store the ids we are going to analyse
# Funcion utilizada para captar posibles errores y reintentar tras 5 segundos
def request_until_succeed(url, max_tries=5):
    #print (url)
    success = False
    response = None
    for i in range(max_tries):
        try: 
            response = requests.get(url)
            #print(response.json())
            if response.status_code == 200:
                break
        except:
            print ("Retrying. There was an error for URL %s: %s" % (url, response.text))
            time.sleep(5)
    return response

# Reducimos a 1 las stories, con el fin de poder procesarla facilmente
# La llamare una vez por pagina que quiera analizar
# FIELDS:
#    - message : texto de la noticia
#    - link : enlace url a la noticia en si
#     - created_time : fecha de publicacion de la noticia
#     - type : tipo de contenido (foto, video...)
#    - name : nombre de la publicacion (?)
#    - id : id de la publicacion
#    - reactions.type(LIKE).summary(total_count).limit(0).as(like)) : extrae el numero de likes (total_count) 
#    - comments.limit(1).summary(true) : extrae numero de comentarios y el ultimo (+ usuario + contenido + info)
#    - shares&limit= : extrae el numero de veces que se ha compartido la noticia
def getFBPageFeedData (page_id, num_status):

    page_idbak = page_id

    # Concatening them I am sure it won`t expire.
    base = "https://graph.facebook.com/v4.0"
    node = "/" + page_id + "/feed"
    parameters = "/?fields=created_time,story,message,name,id,reactions.type(LIKE).summary(total_count).limit(0).as(like),comments.limit(20).summary(true)&limit=%s&access_token=%s" % (num_status, access_token)
    url = base + node + parameters
    response = request_until_succeed(url)
    data = response.json()
    code = response.status_code
    if code != 200:
        raise Exception('Could not fetch data (error {}): {}'.format(code, response.text))
    print ("Analisis de %s realizado!" %page_id)
    #print(data['data'])
    results = [] 
    for post in data['data']:
            #print(post)
            aux = dict()
            if 'message' in post:
                aux["@type"] =  "schema:BlogPosting"
                aux["@id"] = 'https://www.facebook.com/'+page_idbak+'/posts/'+post["id"].split('_')[1]
                aux["schema:datePublished"] = post["created_time"]
                aux["schema:articleBody"] = post["message"]
                aux["schema:author"] = 'facebook'
                aux["schema:creator"] = page_idbak
                aux["schema:search"] = page_idbak
                for i, comment in enumerate(post['comments']['data']):
                    print(comment)
                    try:
                        url = base + '/{userid}/picture?redirect=false&height=100&access_token={token}'.format(userid=comment['id'],token=access_token)
                        profile = request_until_succeed(url)
                        print(profile)
                        post['comments']['data'][i]['from']['photo'] = profile['data']['url']
                    except:
                        print('No profile picture')
                aux['comments'] = post['comments']
                aux['likes'] = post['like']['summary']['total_count']
                results.append(aux)
    return results

if __name__ == '__main__':
    getFBPageFeedData ('restauranteslateral', 10)
