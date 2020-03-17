#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  2 17:11:56 2019

@author: gratienj
"""

import requests
import json
import gzip

kairosdb_server = "http://localhost:8080"

def insert():
    # Simple test [without compression]
    data = [{"name": "test","datapoints": [[1359788400000, 123],[1359788300000, 13.2],[1359788410000, 23.1]],"tags": {"project": "rola"}}]
    response = requests.post(kairosdb_server + "/api/v1/datapoints", json.dumps(data))
    print("Simple test [without compression]: \t%d (status code)" % response.status_code )

    # Complex test [gzipping before send to KairosDB]
    data = [{"name": "test_gzip","datapoints":[[1359788400000, 10],[1359788300000, 11.223],[1359788410000, 24.09]],"tags": {"project": "test_gzip",}}]
    gzipped = gzip.compress(bytes(json.dumps(data), 'UTF-8'))

    headers = {'content-type': 'application/gzip'}
    response = requests.post(kairosdb_server + "/api/v1/datapoints", gzipped, headers=headers)
    print("Complex test [with compression]: \t%d (status code)" % response.status_code)

def query():
    # Simple test
    query = {"start_relative": {"value": "4","unit": "years"},"metrics": [{"name": "test","limit": 10000}]}
    response = requests.post(kairosdb_server + "/api/v1/datapoints/query", data=json.dumps(query))
    print("Status code: %d" % response.status_code)
    print("JSON response:")
    print(response.json())

def query2():
    # Simple test
    query = {"start_absolute": 1359788400000,"metrics": [{"name": "test","limit": 10000}]}
    response = requests.post(kairosdb_server + "/api/v1/datapoints/query", data=json.dumps(query))
    print("Status code: %d" % response.status_code)
    print("JSON response:")
    print(response.json())

def query3():
    # Simple test
    query = {"start_absolute": 0,"metrics": [{"name": "test-historian","limit": 10000}]}
    response = requests.post(kairosdb_server + "/api/v1/datapoints/query", data=json.dumps(query))
    print("Status code: %d" % response.status_code)
    print("JSON response:")
    print(response.json())
if __name__=="__main__":
    #insert()
    query3()