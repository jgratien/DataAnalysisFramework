#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 21:33:58 2019

@author: gratienj
"""

import json

from kafka import KafkaConsumer

def main(tag):

    consumer = KafkaConsumer("historian-topic-"+tag, bootstrap_servers='localhost:9092', group_id="historian-monitor")

    for message in consumer:
        recv_data = json.loads(message.value.decode())
        #print('RECV DATA',recv_data)
        print("DATE {}, VALUE {}".format(recv_data['date'],recv_data['value']))
        #prod = data['values']
        #for p in prod:
        #    print('PDATA',p)
        
if __name__=="__main__":
    tags=["CRY-CENTRALE-SOLAIRE-CRY-act-prod-pow","CRY-TGBT-NORMAL-CRY-act-cons-pow","LAU-PHOTOVOLTAIQUE-LAU-app-prod-pow"]
    main(tags[1])
