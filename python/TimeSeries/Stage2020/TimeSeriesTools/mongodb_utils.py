from pymongo import MongoClient,errors

from kafka import KafkaConsumer,TopicPartition

import json
import time
import os
import pandas as pd
import logging
from jaeger_client import Config
from opentracing_instrumentation.request_context import get_current_span, span_in_context


def mongodb_connect(domain, port):
    domain_str = str(domain) + ":" + str(port)
    try:
        print ("Trying to connect to MongoDB server:", domain, "on port:", port)
        client = MongoClient(host = [domain_str])
        #print ("server_info():", client.server_info())
    except errors.ServerSelectionTimeoutError as err:
        print ("pymongo ERROR:", err)
        client = None
    return client

def get_all_data(client,db_name,coll_name,scheme):
    db = client[db_name]
    collection = db[coll_name]
    data_list=[]
    for d in collection.find():
        data_list.append(d)
    print(len(data_list), " documents found")
    return data_list

def get_data_select_by_tags(client,db_name,coll_name,tags,scheme):
    db = client[db_name]
    collection = db[coll_name]
    for i,(k,v) in enumerate(tags.items()):
        if i==0:
            tagname = v
        else:
            tagname = tagname+'.'+v
    data_list=[]
    for d in collection.find({ 'tagname' : tagname }):
        data_list.append(d)
    print(len(data_list), " documents found")
    return data_list

def insert_many_docs(client,db_name,coll_name,doc_list):
    db = client[db_name]
    collection = db[coll_name]
    doc_id = collection.insert_many(doc_list)
    return doc_id

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