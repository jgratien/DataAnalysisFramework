#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  2 17:11:56 2019

@author: gratienj
"""

import requests
import json


def init_db():
    m3db_server = "http://localhost:7201"
    data = { "type": "local", "namespaceName": "default", "retentionTime": "2h" }
    response = request.post(m3db_server+"/api/v1/database/ create -d /",json.dumps(data))

def insert():
    # Simple test
    m3db_server = "http: //localhost:9003"
    data = { "namespace": "default", "id": "foo", "tags": [ { "name": "__name__", "value": "user_login" }, { "name": "city", "value": "new_york" }, { "name": "endpoint", "value": "/request" } ], "datapoint": { "timestamp":'"$(date +" % s    ")"', "value": 42.123456789 } }
    response = requests.post(m3db_server+"/writetagged - s - X POST - d", json.dumps(data))
    print("Simple test : \t%d (status code)" % response.status_code )


def query():
    # Simple test
    m3db_server = "http://localhost:9003"
    #query = { "namespace": "default", "query": { "regexp": { "field": "city", "regexp": ".*" } }, "rangeStart": 0, "rangeEnd":'"$(date +"%s")"' }
    query = {}
    query["namespace"] = "default"
    query["query"] = {}
    #query["query"]["regexp"] = {}
    #query["query"]["regexp"]["field"] = "city"
    #query["query"]["regexp"]["regexp"] = ".*"
    query["query"]["rangeStart"] = 0
    #query["query"]["rangeEnd"] = '\"$(date +\"%s\")\"'
    query["query"]["rangeEnd"] = 100
    response = requests.post('http://localhost:9003/query',data = { "namespace": "default", "query": { "regexp": { "field": "city", "regexp": ".*" } }, "rangeStart": 0, "rangeEnd":'\"$(date +\"%s\")\"' } )
    print("Status code: %d" % response.status_code)
    #print("JSON response:")
    #print(response.json())


if __name__=="__main__":
    #init_db()
    #insert()
    query()
