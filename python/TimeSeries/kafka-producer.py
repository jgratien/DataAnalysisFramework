#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 17:15:37 2019

@author: gratienj
"""

import json

import time
import os
import pandas as pd

#import urllib.request


from kafka import KafkaProducer


#API_KEY = "XXX" # FIXME Set your own API key here

#url = "https://api.jcdecaux.com/vls/v1/stations?apiKey={}".format(API_KEY)

def main(folder,file):
    producer = KafkaProducer(bootstrap_servers="localhost:9092")
    #with open(os.path.join(data_dir,'Output','output_training.csv'),'r') as f:
    data_file=os.path.join(folder,file)

    data_df=pd.read_csv(data_file,sep=' ',header=None)
    while True:
        for index,row in data_df.iterrows():
            count=str(row[0])
            value=row[1]
            msg = count+":"+value
            producer.send("mytopic",msg.encode('utf8'))
            print("{} Produced records[{}] : {}".format(time.time(), index,msg))
            time.sleep(1)
    
    
if __name__=="__main__":
    data_folder='/work/irlin355_1/gratienj/BigData/DigitalSandBox/Data/TimeSeries'
    test='Test1.csv'    
    main(data_folder,test)
