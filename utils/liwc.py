def liwc_annotations(tweet, senpy_data):
    tweet['nif:isString'] = senpy_data['nif:isString']
    tweet['onyx:hasEmotionSet'] = []
    liwc_result = senpy_data['liwc:result']

    liwc_drives = {"affiliation", "achiev", "power", "reward", "risk"}
    liwc_social = {"family", "friend", "female", "male"}
    liwc_affective = {"anx", "anger", "sad", "posemo", "negemo"}
    liwc_concerns = {"work", "leisure", "home", "money", "relig", "death"}
    
    word_count = len(tweet["schema:headline"].split(" "))
    tweet["word_count"] = word_count   
    
    tweet["radar"], tweet["radar_drives"], tweet["radar_social"], tweet["radar_affective"], tweet["radar_concerns"] = [], [], [], [], []    
    for k,v in liwc_result.items():
        k = k.lower()
        tweet["radar"].append({'key': k, 'value':v})
        
        if k in liwc_drives:
            k = "achievement" if k == "achiev" else k

            tweet["radar_drives"].append({'key': "".join(k[0].upper() + k[1:].lower()), 'value':v*100/word_count})

            tweet['onyx:hasEmotionSet'].append({
                '@type': 'onyx:Emotion',
                'onyx:hasEmotionIntensity': v*100/word_count,
                'onyx:hasEmotionCategory': ''.join(k[0].upper() + k[1:].lower())
            })
            
        elif k in liwc_social:
            tweet["radar_social"].append({'key': "".join(k[0].upper() + k[1:].lower()), 'value':v*100/word_count})

            tweet['onyx:hasEmotionSet'].append({
                '@type': 'onyx:Emotion',
                'onyx:hasEmotionIntensity': v*100/word_count,
                'onyx:hasEmotionCategory': ''.join(k[0].upper() + k[1:].lower())
            })
            
        elif k in liwc_affective:
            k = 'anxiety' if k == 'anx' else k
            k = 'positive' if k == 'posemo' else k
            k = 'negative' if k == 'negemo' else k

            tweet["radar_affective"].append({'key': "".join(k[0].upper() + k[1:].lower()), 'value':v*100/word_count})

            tweet['onyx:hasEmotionSet'].append({
                '@type': 'onyx:Emotion',
                'onyx:hasEmotionIntensity': v*100/word_count,
                'onyx:hasEmotionCategory': ''.join(k[0].upper() + k[1:].lower())
            })
            
        elif k in liwc_concerns:
            k = "religion" if k == "relig" else k

            tweet["radar_concerns"].append({'key': "".join(k[0].upper() + k[1:].lower()), 'value':v*100/word_count})

            tweet['onyx:hasEmotionSet'].append({
                '@type': 'onyx:Emotion',
                'onyx:hasEmotionIntensity': v*100/word_count,
                'onyx:hasEmotionCategory': ''.join(k[0].upper() + k[1:].lower())
            })

    return tweet


def mft_annotations(tweet, senpy_data):
    tweet["mft:result"] = senpy_data["mft:result"]
    
    try:
        for k,v in tweet["mft:result"].items():
            tweet["radar"].append({"key": k, "value": v*100/tweet["word_count"]})
            tweet["radar_mft"].append({"key": k, "value": v*100/tweet["word_count"]})
    except KeyError:
        for k,v in tweet["mft:result"].items():
            tweet["radar"] = [{"key": k, "value": v*100/tweet["word_count"]}]
            tweet["radar_mft"] = [{"key": k, "value": v*100/tweet["word_count"]}]

    return tweet