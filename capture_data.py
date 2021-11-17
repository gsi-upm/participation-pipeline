import os, json, sys, datetime

def main(argv):
    
    now = datetime.datetime.now()ç
    #Lo pongo cada semana y que recoja de la semana anterior, porque tarda mucho en scrappear todos los hashtags
    yesterday_aux = (now - datetime.timedelta(days=6))
    yesterday = yesterday_aux.strftime("%Y-%m-%d")

    with open('hashtags.json', 'r') as myfile:
        data=myfile.read()
        obj = json.loads(data)

    i = int(now.strftime("%Y%m%d%H%M%S"))
    narr = argv[2] if len(argv) > 2 else None
    ide = argv[3] if len(argv) > 3 else None

    if narr == "Pro": narr = 0
    elif narr == "Counter": narr = 1
    elif narr == "Alternative": narr = 2
    else: narr = None

    if ide: ide = ide.replace('_', ' ')

    if narr is not None and ide is not None:
        narrative = obj[narr]
        for hashtag in narrative[ide]:
                    os.system(
                        '''
                        python -m luigi --module test-usecase.workflow StoreTask \
                        --library twint \
                        --query \"#{hashtag}\" \
                        --number {n} \
                        --source twitter \
                        --algorithm sentiment140 \
                        --lang es \
                        --id {id} \
                        --after {after} 
                        '''.format(hashtag=hashtag, id=i, n=50, after=yesterday)
                    )
                    i+=1

    else:
        for narrative in obj:
            for ideology in narrative:
                
                for hashtag in narrative[ideology]:
                    os.system(
                        '''
                        python -m luigi --module test-usecase.workflow StoreTask \
                        --library twint \
                        --query \"#{hashtag}\" \
                        --number {n} \
                        --source twitter \
                        --algorithm sentiment140 \
                        --lang es \
                        --id {id} \
                        --after {after}
                        '''.format(hashtag=hashtag, id=i, n=50, after=yesterday)
                    )
                    i+=1
                    

if __name__ == "__main__":
   main(sys.argv[1:])
