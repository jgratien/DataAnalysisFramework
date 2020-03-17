from influxdb import InfluxDBClient
from pymongo import MongoClient,errors

from kafka import KafkaConsumer,TopicPartition

import json
import time
import os
import pandas as pd
import logging
from jaeger_client import Config
from opentracing_instrumentation.request_context import get_current_span, span_in_context

def influxdb_connect(domain, port, database_name):
    print ("Trying to connect to InfluxDB server without proxy:", domain, "on port:", port)
    proxies = { "http": None, "https": None}
    try:
        client = InfluxDBClient(host=domain, 
                                port=port, 
                                database=database_name,
                                proxies=proxies)
        print("connection sucess!")
        return client
    except:
        print("connection error!")
        return 


def mongodb_connect(domain, port):
    domain_str = str(domain) + ":" + str(port)
    try:
        print ("Trying to connect to MongoDB server:", domain, "on port:", port)
        client = MongoClient(host = [domain_str],
                             serverSelectionTimeoutMS = 2000)
        #print ("server_info():", client.server_info())
    except errors.ServerSelectionTimeoutError as err:
        print ("pymongo ERROR:", err)
        client = None
    return client

def init_tracer(service):
    logging.getLogger('').handlers = []
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)    
    config = Config(
        config={
            'sampler': {
                'type': 'const',
                'param': 1,
            },
            'logging': True,
        },
        service_name=service,
    )
    if config._initialized == False :
        return config.initialize_tracer()
    else :
        print("error : create new tracer...")
        return config.new_tracer()    