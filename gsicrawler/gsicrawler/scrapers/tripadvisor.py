import requests
import json
import re
from bs4 import BeautifulSoup
import datetime
import locale


MONTHS = {'enero': 1,
          'febrero': 2,
          'marzo': 3,
          'abril': 4,
          'mayo': 5,
          'junio': 6,
          'julio': 7,
          'agosto': 8,
          'septiembre': 9,
          'octubre': 10,
          'noviembre': 11,
          'diciembre':12
}


def retrieveTripadvisorReviews(search, num):

    locale.setlocale(locale.LC_TIME, '')

    s = requests.session()
    res = s.get('https://www.tripadvisor.es/Search', headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36'})
    cookies = dict(res.cookies)
    url = 'https://www.tripadvisor.es/TypeAheadJson?interleaved=true&geoPages=true&details=true&action=API&types=geo%2Chotel%2Ceat%2Cattr%2Cvr%2Cair%2Ctheme_park%2Cal%2Cact&neighborhood_geos=true&link_type=geo&matchTags=true&matchGlobalTags=true&matchKeywords=true&matchOverview=true&matchUserProfiles=true&strictAnd=false&scoreThreshold=0.8&hglt=true&disableMaxGroupSize=true&max=7&injectNewLocation=true&injectLists=true&nearby=true&local=true&typeahead1_5=true&geoBoostFix=true&nearPages=true&nearPagesLevel=strict&rescue=true&supportedSearchTypes=find_near_stand_alone_query&query={}'.format(search)
    r = s.get(url, 
        headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36'}, 
        cookies = cookies)
    soup = r.json()
    restaurants = []
    for i, article in enumerate(soup['results']):
        if str(article['type']):
            url = "https://www.tripadvisor.es"+str(article['url'])
            restaurants.append(url)
    reviews =[]
    for restaurant in restaurants:
        s = requests.session()
        res = s.get(restaurant, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36'})
        cookies = dict(res.cookies)
        r = s.get(restaurant, 
            headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36'}, 
            cookies = cookies)
        soup = BeautifulSoup(r.text, 'html.parser')
        for i, article in enumerate(soup.select('.review-container')):
            aux = dict()
            aux['@id'] = "http://tripadvisor.es"+article.select('.quote')[0].find('a').get('href')
            for cls in article.select('.ui_bubble_rating')[0]['class']:
                rating = re.match(r'bubble_(\d*)', cls)
                if rating:
                    aux['schema:reviewRating'] = int(rating.group(1)) / 10
                    break
            aux['schema:author'] = 'Tripadvisor'
            aux["@type"] = "schema:Review"
            aux['schema:search'] = search
            aux['schema:creator'] = article.select('.member_info .info_text > div')[0].string
            aux['schema:headline'] = article.select('.quote span')[0].string
            aux['schema:reviewBody'] = article.select('.entry p')[0].text
            aux['schema:articleBody'] = article.select('.entry p')[0].text
            try:
                aux['schema:Place'] = article.select('.userLocation')[0].text
            except:
                pass
        
            day, _, mes, _, year = article.select('.ratingDate')[0].get('title').split(' ')
            month = MONTHS[mes]
            date = datetime.date(int(year), int(month), int(day))
            aux['schema:datePublished'] = str(date.strftime('%Y-%m-%dT00:00:00Z'))
            reviews.append(aux)

            num -= 1
            if num == 0:
                return reviews

    return reviews
