import json

def read_hashtags():
    # read file
    with open('hashtags.json', 'r') as myfile:
        data=myfile.read()

    # parse file
    return json.loads(data)

    # narratives = obj[0]
    # counter = obj[1]
    # alternative = obj[2]

def get_narrative(hashtags):
    results = []
    narratives, _, _ = read_hashtags()
    for narrative, tags in narratives.items() :
        for tag in tags:
            if tag.lower() in hashtags:
                results.append(narrative)

    return results

def get_counter(hashtags):
    results = []
    _, counter, _ = read_hashtags()
    for narrative, tags in counter.items() :
        for tag in tags:
            if tag.lower() in hashtags:
                results.append(narrative)

    return results

def get_alternative(hashtags):
    results = []
    _, _, alternative = read_hashtags()
    for narrative, tags in alternative.items() :
        for tag in tags:
            if tag.lower() in hashtags:
                results.append(narrative)

    return results

def annotate_ideology(tweet_list):
    for tweet in tweet_list:

        # Semantic annotation
        tweet["marl:hasOpinion"] = []

        dbpedia = {
            "Religious": "dbpedia:Islamic_extremism",
            "Far left": "dbpedia:Left-wing_politics",
            "Far right": "dbpedia:Right-wing_politics",
            "Separatism": "dbpedia:Separatism"
        }

        narrative = get_narrative(tweet["schema:keywords"])
        counter = get_counter(tweet["schema:keywords"])
        alternative = get_alternative(tweet["schema:keywords"])

        # Kibana annotation
        tweet["narrative"] = narrative
        tweet["counter-narrative"] = counter
        tweet["alternative-narrative"] = alternative
        tweet['ideology'] = list(set(narrative+counter+alternative))

        
        for k in narrative:
            tweet["marl:hasOpinion"].append({
                '@type': 'marl:Opinion',
                "dbpedia:ideology": dbpedia[k],
                "dbpedia:alignment": "narr:Pro"
            })
            tweet[k] = "Pro"
            
        for k in counter:
            tweet["marl:hasOpinion"].append({
                '@type': 'marl:Opinion',
                "dbpedia:ideology": dbpedia[k],
                "dbpedia:alignment": "narr:Counter"
            })
            tweet[k] = "Counter"
            
        for k in alternative:
            tweet["marl:hasOpinion"].append({
                '@type': 'marl:Opinion',
                "dbpedia:ideology": dbpedia[k],
                "dbpedia:alignment": "narr:Alternative"
            })
            tweet[k] = "Alternative"

    return tweet_list