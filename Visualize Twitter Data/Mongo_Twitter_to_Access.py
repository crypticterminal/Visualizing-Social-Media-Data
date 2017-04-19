'''
Created on Mar 29, 2017

@author: Xuebin Wei
www.lbsocial.net
'''
import pymongo
from pymongo import MongoClient

from time import mktime
from datetime import datetime
from time import strptime
import pyodbc 
client = MongoClient()

db = client.tweet_db # change to your tweet db

tweet_collection = db.tweet_collection # change to your tweet collection
tweet_collection.create_index([("id", pymongo.ASCENDING)],unique = True)
tweet_collection.create_index([("coordinates", pymongo.ASCENDING)])
tweet_cursor = tweet_collection.find({'coordinates' : {"$ne" : None}}) # get tweet with coordinates
num_of_tweet = float(tweet_cursor.count())

db_file = '' #change the location to your Access file

odbc_conn_str = 'DRIVER={Microsoft Access Driver (*.mdb)};DBQ=%s' %(db_file) 

conn = pyodbc.connect(odbc_conn_str)

cursor = conn.cursor()
i = 0
for document in tweet_cursor:
    try:
        tweet_created_at = document["created_at"].split()
     

        tweet_month = strptime(tweet_created_at[1],'%b').tm_mon
        if tweet_month<10:
            tweet_month_str = '0'+ str(tweet_month)
        else:
            tweet_month_str = str(tweet_month)
     
        tweet_date =tweet_created_at[5]+'-'+tweet_month_str+'-'+tweet_created_at[2]
        tweet_time = tweet_created_at[3]
        tweet_date_time = tweet_date +' '+tweet_time
        time_diff = datetime.now()-datetime.fromtimestamp(mktime(strptime(tweet_date_time, "%Y-%m-%d %H:%M:%S"))) 
        z =  50000000.0/time_diff.total_seconds() # height of tweet points, relative time difference to current time, recent tweets on top
         
        i = i+1 
        print(i/num_of_tweet)
        sql_insert_statement = """insert into tweet(tweet_id, user_id,tweet_date, tweet_time, tweet_date_time, x, y,z) values('{}','{}','{}','{}','{}','{}','{}','{}');""".format\
                                 (document['id_str'],document["user"]["id_str"],tweet_date,tweet_time,tweet_date_time,document["coordinates"]['coordinates'][0],document["coordinates"]['coordinates'][1],z)

        cursor.execute(sql_insert_statement)
        cursor.commit()
    except:
        pass

cursor.close()
conn.close()
