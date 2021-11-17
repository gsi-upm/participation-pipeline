import tweepy
import twint
import json
import os
import argparse
import time
import logging

CONSUMER_KEY = os.environ['TWITTER_CONSUMER_KEY']
CONSUMER_SECRET = os.environ['TWITTER_CONSUMER_SECRET']
ACCESS_TOKEN = os.environ['TWITTER_ACCESS_TOKEN']
TOKEN_SECRET = os.environ['TWITTER_ACCESS_TOKEN_SECRET']


def search(api, query, count):
    searched_tweets = []
    last_id = -1
    max_tweets = count
    max_tweets = int(max_tweets)

    while len(searched_tweets) < max_tweets:
        count = max_tweets - len(searched_tweets)
        new_tweets = api.search(q=query, count=count, max_id=str(last_id - 1))
        if not new_tweets:
            break
        searched_tweets.extend(new_tweets)
        last_id = new_tweets[-1].id
    return searched_tweets


def timeline(api, query, count):
    return api.user_timeline(screen_name=query, count=count)


def retrieveTweets(querytype, query, count=200, keep=False, library="twint", before=None, after=None):
    if library == "twint":

        # consumer_key = CONSUMER_KEY
        # consumer_secret = CONSUMER_SECRET
        # access_token = ACCESS_TOKEN
        # access_token_secret = TOKEN_SECRET

        # auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        # auth.set_access_token(access_token, access_token_secret)

        # api = tweepy.API(auth)

        t = twint.Config()

        t.Search = query
        t.Store_object = True
        t.Limit = int(count)
        t.Near = "europe"

        if before:
            t.Until = before
        if after:
            t.Since = after

        try:
            twint.run.Search(t)
        except:
            pass

        tweet_list = twint.output.tweets_list.copy()
        results = []

        c = twint.Config()
        users = set()
        locations = {}

        for tweet in tweet_list:
            mytweet = tweet if keep else {}

            # Take tweet location
            if tweet.place:
                mytweet['location'] = { 
                    'lat': tweet.place["coordinates"][0],
                    'lon': tweet.place["coordinates"][1]
                }

            # Take location from known user
            elif tweet.username in users:
                mytweet["schema:locationCreated"] = locations[tweet.username]

            # Search for user location
            else:
                c.Username = tweet.username
                c.Store_object = True

                try:
                    twint.run.Lookup(c)
                    mytweet["schema:locationCreated"] = twint.output.users_list[-1].location

                    users.add(tweet.username)
                    locations.update({tweet.username: twint.output.users_list[-1].location})
                except:
                    pass

            # try:
            #     mytweet["schema:locationCreated"] = api.get_user(tweet.user_id_str, tweet.username).location
            # except:
            #     pass
                
            mytweet["@type"] =  ["schema:BlogPosting", ]
            mytweet["@id"] = 'https://twitter.com/{screen_name}/status/{id}'.format(screen_name=tweet.username, id=tweet.id)
            mytweet["schema:about"] = query
            mytweet["schema:search"] = query
            mytweet["schema:articleBody"] = tweet.tweet
            mytweet["schema:headline"] = tweet.tweet
            mytweet["schema:creator"] = tweet.username
            mytweet["schema:author"] = 'twitter'
            mytweet["schema:inLanguage"] = tweet.lang
            mytweet["schema:keywords"] = tweet.hashtags
            mytweet["schema:datePublished"] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.strptime(tweet.datetime,'%Y-%m-%d %H:%M:%S %Z'))

            if tweet.reply_to:
                mytweet["@type"].append("schema:Comment")
                mytweet["schema:parentItem"] = 'https://twitter.com/{screen_name}/status/{id}'.format(screen_name=tweet.reply_to[0]["screen_name"], id=tweet.reply_to[0]["id"])
            
            results.append(mytweet)

        print(json.dumps(results, indent=3))
        return results

    elif library == "tweepy":

        consumer_key = CONSUMER_KEY
        consumer_secret = CONSUMER_SECRET
        access_token = ACCESS_TOKEN
        access_token_secret = TOKEN_SECRET

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

        api = tweepy.API(auth)


        found = []

        if querytype == 'search':
            found = search(api, query, count)
            logging.warning(found)
        elif querytype == 'timeline':
            found = timeline(api, query, count)
        else:
            raise Exception('Unknown query type')


        results = []        
        for item in found:
            jsontweet = json.dumps(item._json)
            tweet = json.loads(jsontweet)

            mytweet = tweet if keep else {}


            mytweet["@type"] =  ["schema:BlogPosting", ]
            mytweet["photo"] = tweet['user']['profile_image_url']
            mytweet["@id"] = 'https://twitter.com/{screen_name}/status/{id}'.format(screen_name=tweet['user']['screen_name'], id=tweet["id"])
            mytweet["schema:about"] = query
            mytweet["schema:search"] = query
            mytweet["schema:articleBody"] = tweet["text"]
            mytweet["schema:headline"] = tweet["text"]
            mytweet["schema:creator"] = tweet['user']['screen_name']
            mytweet["schema:author"] = 'twitter'
            mytweet["source"] = 'twitter'
            mytweet["schema:datePublished"] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y'))


            if tweet["in_reply_to_status_id"]:
                mytweet["@type"].append("schema:Comment")
                mytweet["schema:parentItem"] = 'https://twitter.com/{screen_name}/status/{id}'.format(screen_name=tweet["in_reply_to_screen_name"], id=tweet["in_reply_to_status_id"])

            results.append(mytweet)

        return results

    else:
        return [{}]