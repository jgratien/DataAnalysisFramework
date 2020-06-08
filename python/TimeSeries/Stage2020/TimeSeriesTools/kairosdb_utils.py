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
