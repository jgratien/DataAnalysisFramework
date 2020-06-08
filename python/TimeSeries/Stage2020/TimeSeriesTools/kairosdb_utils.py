import json
import time
import datetime
import os
import logging
import requests

def convert_to_dict(response,scheme):
    cols = [ k for k in scheme.keys()]
    id = 0
    data = []
    for d in response:
        timestamp = d[0]
        str_value = str(id)+';'+str(d[0])+';'+d[1]
        values = str_value.split(';')
        dict = { cols[i]:values[i] for i in range(len(cols))}
        data.append(dict)
        id = id + 1
    return data

def convert_to_dict_with_tags(response,tags,scheme):
    cols = [ k for k in scheme.keys()]
    id = 0
    tagname = 'TAG'
    for i,(k,v) in enumerate(tags.items()):
        tagname = tagname+'.'+v[0]
    data = []
    for d in response:
        timestamp = d[0]
        str_value = str(id)+';'+str(d[0])+';'+tagname+';'+d[1]
        values = str_value.split(';')
        dict = { cols[i]:values[i] for i in range(len(cols))}
        data.append(dict)
        id = id + 1
    return data

def get_all_data(server,db_name,coll_name,scheme):
    query = {
            "start_absolute":1,
            "metrics": [
                {
                    "name": db_name,
                    "tags": {
                        'source' : coll_name,
                        'column' : 'all'
                    }
                }
            ]}
    response = requests.post(server + "/api/v1/datapoints/query", data=json.dumps(query))
    if response.status_code == 200:
        return convert_to_dict(response.json()['queries'][0]['results'][0]['values'],scheme)
    else:
        return []
    return response

def get_data_select_by_tags(server,db_name,coll_name,tags,scheme):
    tag_query = { 'source' : coll_name }
    for i,(k,v) in enumerate(tags.items()):
        tag_query[k] = v
    query = {
            "start_absolute":1,
            "metrics": [
                {
                    "name": db_name,
                    "tags": tag_query,
                }
            ]}
    response = requests.post(server + "/api/v1/datapoints/query", data=json.dumps(query))
    if response.status_code == 200:
        values = response.json()['queries'][0]['results'][0]['values']
        tags = response.json()['queries'][0]['results'][0]['tags']
        return convert_to_dict_with_tags(values,tags,scheme)
    else:
        return []
    return response


def insert_many_docs(kairosdb_server,db_name, coll_name,doc_list):
    t0 = time.process_time()
    data = [
            {
                "name": db_name,
                "datapoints": [],
                "tags": {
                    "source": coll_name,
                    "column": "all"
                },
                "type": "string"
            }
        ]
    for d in doc_list:
        data[0]['datapoints'].append(d)
    t1 = time.process_time()
    print('.. %f seconds for create query' % (t1 - t0))

    t0 = time.process_time()
    response = requests.post(kairosdb_server + "/api/v1/datapoints", json.dumps(data))
    t1 = time.process_time()
    print('.. %f seconds for posting query' % (t1 - t0))
    print("insertion many doc: \t%d (status code)" % response.status_code)
    return response.status_code

def insert_many_docs_with_tags(kairosdb_server,db_name, coll_name,tags,doc_list):
    t0 = time.process_time()
    data = [
            {
                "name": db_name,
                "datapoints": [],
                "tags": {
                    "source": coll_name,
                    "column": "all"
                },
                "type": "string"
            }
        ]
    
    for i, (k, v) in enumerate(tags.items()):
        data[0]["tags"][k] = v
        
    for d in doc_list:
        data[0]['datapoints'].append(d)
    t1 = time.process_time()
    #print('.. %f seconds for create query' % (t1 - t0))

    t0 = time.process_time()
    response = requests.post(kairosdb_server + "/api/v1/datapoints", json.dumps(data))
    t1 = time.process_time()
    #print('.. %f seconds for posting query' % (t1 - t0))
    #print("insertion many doc: \t%d (status code)" % response.status_code)
    return response.status_code


def insert_one_doc_with_tags(kairosdb_server,db_name, coll_name,tags,doc):
    t0 = time.process_time()
    data = [
            {
                "name": db_name,
                "datapoints": [],
                "tags": {
                    "source": coll_name,
                    "column": "all"
                },
                "type": "string"
            }
        ]
    for i, (k, v) in enumerate(tags.items()):
        data[0]["tags"][k] = v
    
    data[0]['datapoints'].append(doc)
    t1 = time.process_time()
    #print('.. %f seconds for create query' % (t1 - t0))

    t0 = time.process_time()
    response = requests.post(kairosdb_server + "/api/v1/datapoints", json.dumps(data))
    t1 = time.process_time()
    #print('.. %f seconds for posting query' % (t1 - t0))
    #print("insertion one doc: \t%d (status code)" % response.status_code)
    return response.status_code