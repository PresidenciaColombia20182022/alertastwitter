from config import ACCESS_TOKEN,ACCESS_TOKEN_SECRET,CONSUMER_KEY, CONSUMER_SECRET,ACCESS_TOKEN2,ACCESS_TOKEN3,ACCESS_TOKEN_SECRET2,ACCESS_TOKEN_SECRET3,CONSUMER_KEY2,CONSUMER_KEY3,CONSUMER_SECRET2,CONSUMER_SECRET3, TELEGRAM
import tweepy
from tweepy import OAuthHandler
import sys
import pandas as pd
import json
from datetime import datetime
import time 
import os
import pickle
import psycopg2
import openpyxl
import telepot

#Obtiene la geolocalización de Colombia
def get_woeid(place):
    '''Get woeid by location'''
    try:
        trends = api.available_trends()
        for val in trends:
            if (val['name'].lower() == place.lower()):
                return(val['woeid'])
        print('Location Not Found')
    except Exception as e:
        print('Exception:',e)
        return(0)

#Obtiene las tendencias del momento en Twitter
def get_trends(place):
    #woeid colombia = 23424787
    col_trends = api.get_place_trends(id =get_woeid(place))
    trends = []
    for trend in col_trends[0]['trends']:
        trends.append((trend['name'], trend['tweet_volume']))
    pd_trends = pd.DataFrame(trends,columns = ['trend','tweet_volume'])
    pd_trends['index'] = pd_trends.index+1
    pd_trends = pd_trends[['index','trend','tweet_volume']]
    return pd_trends

#Función que obtiene las tendencias
def scraptweets(search_words, date_since, numTweets, apiauth):
    
    # Define un DataFrame de pandas con los metadatos de Twitter:
    db_tweets = pd.DataFrame(columns = ['username', 'acctdesc', 'location', 'following',
                                        'followers', 'totaltweets', 'usercreatedts', 'tweetcreatedts',
                                        'retweetcount', 'text', 'hashtags']
                                )
    
    #for i in range(0, numRuns):
        
        
        
        # Obtienes los tweets mediante un for loop
        # .Cursor() retorna un objeto que puedes iterar en un for loop
        # Cada item tiene información de cada tweet
#Intenta autenticarse con los primeros tokens, si algo falla, autentica con los segundos tokens.
    import itertools

    

    for element in itertools.cycle(apiauth):
        print(apiauth.index(element))
        try:
            tweets = tweepy.Cursor(element.search_tweets, q=search_words,lang = 'es', tweet_mode='extended').items(numTweets)
            print('api',apiauth.index(element))
            # Guarda los tweets en una lista de python
            tweet_list = [tweet for tweet in tweets]
            break
        except:
            continue

    '''
    try:
        tweets = tweepy.Cursor(apiauth[0].search_tweets, q=search_words,lang = 'es', tweet_mode='extended').items(numTweets)
        print('api 0')
        # Guarda los tweets en una lista de python
        tweet_list = [tweet for tweet in tweets]
    except:
        try:
            tweets = tweepy.Cursor(apiauth[1].search_tweets, q=search_words,lang = 'es', tweet_mode='extended').items(numTweets)
            print('api 1')
            # Guarda los tweets en una lista de python
            tweet_list = [tweet for tweet in tweets]
        except:         
            tweets = tweepy.Cursor(apiauth[2].search_tweets, q=search_words,lang = 'es', tweet_mode='extended').items(numTweets)
            print('api 2')
            # Guarda los tweets en una lista de python
            tweet_list = [tweet for tweet in tweets]
    '''
# Obtiene la siguiente info de Twitter:
        # user.screen_name - cuenta de twitter
        # user.description - descripción de la cuenta
        # user.location - De dónde es el tweet
        # user.friends_count - no. de otros usuarios que el usuario sigue (following)
        # user.followers_count - no. de usuarios que siguen a este usuario (followers)
        # user.statuses_count - total tweets realizados por el usuario 
        # user.created_at - Cuándo fue creada la cuenta
        # created_at - Cuándo fue creado el tweet
        # retweet_count - no. de retweets
        # retweeted_status.full_text - full text del tweet
        # tweet.entities['hashtags'] - hashtags en el  tweet
# Realiza el scraping de los tweets individualmente:
    noTweets = 0
    for tweet in tweet_list:
# Extrae los valores
        username = tweet.user.screen_name
        acctdesc = tweet.user.description
        location = tweet.user.location
        following = tweet.user.friends_count
        followers = tweet.user.followers_count
        totaltweets = tweet.user.statuses_count
        usercreatedts = tweet.user.created_at
        tweetcreatedts = tweet.created_at
        retweetcount = tweet.retweet_count
        hashtags = tweet.entities['hashtags']
        try:
            text = tweet.retweeted_status.full_text
        except AttributeError:  # No es Retweet
            text = tweet.full_text
# Añade las 11 variables a la lista - ith_tweet:
        ith_tweet = [username, acctdesc, location, following, followers, totaltweets,
                        usercreatedts, tweetcreatedts, retweetcount, text, hashtags]
# Append al dataframe - db_tweets
        db_tweets.loc[len(db_tweets)] = ith_tweet
# Incrementa el contador - noTweets  
        noTweets += 1
    
#Obtener la ruta donde guardar los archivos - path   
    path = os.getcwd()+'/'
    to_csv_timestamp = datetime.today().strftime('%Y%m%d')
#Carga el modelo de ML entrenado
    filename_model = os.getcwd()+"/models/twitter_classifier_model_v1.sav"
    loaded_model = pickle.load(open(filename_model, 'rb'))
    filename = path +to_csv_timestamp + search_words+'_TT.csv'

#Predice para cada tweet la categoría del tweet    
    db_tweets['prediction'] = db_tweets['text'].apply(lambda x: loaded_model.predict([x]))
    db_tweets['trend'] = search_words
    
#Si la predicción del 70% de los tweets es 'Política' entonces clasifica la tendencia como 'Política'
    if len(db_tweets[db_tweets['prediction']=='Política'])/len(db_tweets)>0.7:
      db_tweets['Política'] = 'Si'
    else:
      db_tweets['Política'] = 'No'
    
    db_tweets['date'] = datetime.strptime(date_since,'%Y-%m-%d')
    
    return db_tweets
#Función para insertar los datos a la base de datos PostgresQL
def insertdata(data_final):
        try:  
            con = psycopg2.connect(
                database="postgres",
                user="postgres",
                password="password",
                host="127.0.0.1",
                port="5432")
            cur = con.cursor()
            postgres_insert_query = """ INSERT INTO TENDENCIAS (TREND, TWEET_VOLUME, DATE) VALUES (%s,%s,%s)"""
            #record_to_insert = (list(data_final['trend']), list(data_final['tweet_volume']), list(data_final['date']))
            record_to_insert = data_final
            for record in range(len(data_final)):
                try:
                    cur.execute(postgres_insert_query,tuple(list(data_final.iloc[record])))
                    con.commit()
                    count = cur.rowcount
                    print(count, "Record {} inserted successfully into TRENDS table".format(record))
                except (Exception, psycopg2.Error) as error:
                    print("Record {} NOT inserted into TRENDS table".format(record), error)
                
            

        except (Exception, psycopg2.Error) as error:
            print("Failed to insert record into trend table", error)
        finally:
        # closing database connection.
            if con:
                cur.close()
                con.close()
                print("PostgreSQL connection is closed")
#Corre el programa de Python    
if __name__ == "__main__":
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    auth2 = tweepy.OAuthHandler(CONSUMER_KEY2, CONSUMER_SECRET2)
    auth2.set_access_token(ACCESS_TOKEN2, ACCESS_TOKEN_SECRET2)
    auth3 = tweepy.OAuthHandler(CONSUMER_KEY3, CONSUMER_SECRET3)
    auth3.set_access_token(ACCESS_TOKEN3, ACCESS_TOKEN_SECRET3)
    api = tweepy.API(auth, wait_on_rate_limit=False)
    if (not api):
        print ("Can't Authenticate")
        sys.exit(-1)
    api2 = tweepy.API(auth2, wait_on_rate_limit=True)
    if (not api):
        print ("Can't Authenticate")
        sys.exit(-1)
    api3 = tweepy.API(auth3, wait_on_rate_limit=True)
    if (not api):
        print ("Can't Authenticate")
        sys.exit(-1)
    listapi = [api,api2,api3]
    
    date_since = datetime.today().strftime('%Y-%m-%d')
    data = get_trends('Colombia')[['trend','tweet_volume']]
    data.fillna(0, inplace = True)
    
    search_words = list(data['trend'])
    numTweets = 50
    db_tweets = pd.DataFrame([])

    # Muestra cuánto tiempo toma al programa obtener los tweets:
    program_start = time.time()
    start_run = time.time()

    for i in range(len(search_words)):    
        # Llama la función scraptweets para obtener los tweets de acuerdo a la variable 'numTweets'
        
        db_tweets = pd.concat([db_tweets,scraptweets(search_words[i], date_since, numTweets,listapi)])
        print(i)
    # Scraping finalizado:
    end_run = time.time()
    duration_run = round((end_run-start_run)/60, 2)
    program_end = time.time()
    print('Scraping has completed!')
    print('Total time taken to scrap is {} minutes.'.format(round(program_end - program_start)/60, 2))
        
    #Extraer tweets de Política
    db_tweets_gobierno = db_tweets[db_tweets['Política'] == 'Si']
    data_final = pd.merge(left = pd.DataFrame(db_tweets_gobierno.trend.unique()),right = data,  left_on =[0], right_on=['trend'],how = 'left')[['trend','tweet_volume']]
    data_final['date'] = datetime.strptime(date_since,'%Y-%m-%d')
    print(data_final)
    try:
        data_final['date'] = data_final['date'].apply(lambda a: pd.to_datetime(a).date()) 
        db_tweets.to_excel(os.getcwd()+"/results.xlsx")
        db_tweets_gobierno.to_excel(os.getcwd()+"/results_gobierno.xlsx")
        data_final.to_json(os.getcwd()+"/data_final.json")
    except:
        pass
    #Conecta con la base de datos PosgresQL
    con = psycopg2.connect(
        database="postgres",
        user="postgres",
        password="password",
        host="127.0.0.1",
        port="5432")
    print("Database opened successfully")

    cur = con.cursor()
    try:
        cur.execute('''CREATE TABLE TRENDS
            (TREND CHAR(50),
            TWEET_VOLUME INT NOT NULL,
            DATE DATE);''')
        print("Table created successfully")
    except:
        print("Table already created")


    #con.commit()
    #con.close()

    insertdata(data_final)
    print(data_final.to_json())

    #Conectar el ID del grupo de TELEGRAM
    receiver_id = -618712627
    #Identificar el BOT con su Token correspondiente
    bot = telepot.Bot(TELEGRAM)
    print('ENVIA MENSAJE')
    #Enviar los mensajes al Telegram
    #bot.sendMessage(receiver_id,"Las tendencias más importantes al día de hoy son: ")
    #for i, value in enumerate(data_final['trend']):
    #    texto = '*'+str(value)+'* -> *'+str(data_final['tweet_volume'][i])+' Menciones*'
    #    bot.sendMessage(chat_id = receiver_id,
    #                    text = texto,
    #                    parse_mode = 'Markdown')
    #    print(value)
