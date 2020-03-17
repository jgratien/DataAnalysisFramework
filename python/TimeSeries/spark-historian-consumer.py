#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 21:33:58 2019

@author: gratienj
"""
import os
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.4.4 pyspark-shell'

#    Spark
from pyspark import SparkContext
#    Spark Streaming

from pyspark.streaming import StreamingContext
#    Kafka

from pyspark.streaming.kafka import KafkaUtils

#    json parsing
import json

from kafka import KafkaConsumer

import findspark
findspark.init()

import pyspark
from pyspark import SparkContext, SparkConf
from pyspark.sql import SQLContext, HiveContext, Row
from pyspark.storagelevel import StorageLevel
from pyspark.streaming import StreamingContext

def create_sc(app_name='AppName',
              master='local[*]',
              executor_memory='1G',
              nb_cores='1',
              driver_memory='2G',
              max_result_size='10G'):
    sc_conf = SparkConf()
    sc_conf.setAppName(app_name)
    sc_conf.setMaster(master)
    sc_conf.set('spark.executor.memory',executor_memory)
    if nb_cores != '0':
        sc_conf.set('spark.executor.cores', nb_cores)
    sc_conf.set('spark.driver.memory', driver_memory)
    sc_conf.set('spark.cores.max', '32')
    sc_conf.set('spark.driver.maxResultSize', max_result_size)
    sc_conf.set('spark.logConf', True)
    print(sc_conf.getAll())

    sc = None
    try:
        sc.stop()
        sc = SparkContext(conf=sc_conf)
    except:
        sc = SparkContext(conf=sc_conf)

    return sc

from SmartGrid import analyzeLog

def process(rdd):
    
    import requests
    kairosdb_server = "http://localhost:8080"
    v=[]
    for t in rdd.collect():
        v.append([t[0],t[1]])
    data = [{"name": "test-historian","datapoints": v,"tags": {"project": "historian"}}]
    response = requests.post(kairosdb_server + "/api/v1/datapoints", json.dumps(data))
    #print("RESPONSE",response)

def main(tag):
    
    
    sc = create_sc("UnitTest")
    sc.setLogLevel("INFO")

    print('SPARK CONTEXT INFO  :')
    print('      VERSION       :',sc.version)
    print('      DRIVER MEMORY :',sc._conf.get('spark.driver.memory'))
    
    stream = StreamingContext(sc, 60)
    
    kafka_stream = KafkaUtils.createStream(stream, 'localhost:2181', 'spark-historian-consumer', {'historian-topic-CRY-TGBT-NORMAL-CRY-act-cons-pow':1})
    #kafka_stream = KafkaUtils.createStream(stream, 'victoria.com:2181', 'spark-streaming', {'imagetext':1})
    #parsed = kafka_stream.map(lambda v: json.loads(v[1]))
    parsed = kafka_stream.map(lambda v: analyzeLog(v[1]))
    #parsed.pprint()
    parsed.foreachRDD(lambda k: process(k))
    
    

    parsed.pprint()

    stream.start()
    stream.awaitTermination()
        
if __name__=="__main__":
    tags=["CRY-CENTRALE-SOLAIRE-CRY-act-prod-pow","CRY-TGBT-NORMAL-CRY-act-cons-pow","LAU-PHOTOVOLTAIQUE-LAU-app-prod-pow"]
    main(tags[1])
