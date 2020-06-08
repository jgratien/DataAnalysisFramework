from influxdb import InfluxDBClient


import json
import time
import datetime
import os
import pandas as pd
import logging
from opentracing_instrumentation.request_context import get_current_span, span_in_context

def influxdb_connect(domain, port):
    print ("Trying to connect to InfluxDB server without proxy:", domain, "on port:", port)
    proxies = { "http": None, "https": None}
    try:
        client = InfluxDBClient(host=domain, 
                                port=port,
                                proxies=proxies)
        print("connection sucess!")
        return client
    except:
        print("connection error!")
        return 

def get_all_data(client,db_name,coll_name,scheme):
    cols = [ k for k in scheme.keys()]
    
    client.switch_database(db_name)
    results = client.query(f'SELECT * FROM "{db_name}"."autogen"."{coll_name}"',epoch='ms')
    points = results.get_points(measurement=coll_name)
    results = []
    id = 0
    for point in points:
        date = point['time']
        str_value = str(id)+';'+str(date)+';'+point['data']
        values = str_value.split(';')
        results.append({ cols[i]:values[i] for i in range(len(cols))})
        #print(cols[1],',',date,',',str_value)
        id += 1
    return results

def create_database(client,db_name):
    client.create_database(db_name)

def delete_database(client,db_name):
    client.drop_database(db_name)

def test_database_exists(client,db_name):
    return db_name in client.get_list_database()

def insert_many_docs(client,db_name, coll_name,doc_list):
    if not test_database_exists(client,db_name):
        print(f"DATBASE {db_name} does not exist, will be created")
        create_database(client,db_name)
        
    client.switch_database(db_name)
    json_body = []
    for doc in doc_list:
        json_body.append({"measurement": coll_name,
                          "time": doc[0],
                          "fields": {"data": doc[1]} })
        #print('JSON BODY',doc[0],doc[1])
    status = client.write_points(json_body, time_precision='ms',protocol=u'json')
    if status == True :
        print(f"{len(doc_list)} documents have been inserted")
    else:
        print("Error while inserting documents")
    return status