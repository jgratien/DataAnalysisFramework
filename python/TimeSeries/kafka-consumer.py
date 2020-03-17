#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 21:33:58 2019

@author: gratienj
"""

import json

from kafka import KafkaConsumer

def main():

    consumer = KafkaConsumer("mytopic", bootstrap_servers='localhost:9092', group_id="velib-monitor-stations")

    for message in consumer:
        msg = message.value.decode()
        print('RECEIVED MSG',msg)
        
if __name__=="__main__":
    main()