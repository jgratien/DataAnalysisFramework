#!/usr/bin/env python3
''' Insert data in KairosDB using REST API through requests module.
    
    Please, check out the documentation on the KairosDB website:
        http://kairosdb.github.io/docs/build/html/restapi/AddDataPoints.html
    @author Fernando Paladini <fnpaladini@gmail.com>
'''

import requests
import json
import gzip

kairosdb_server = "http://localhost:6060"

# Simple test [without compression]
data = [
    {
        "name": "test",
        "datapoints": [
            [1359788400000, 123], 
            [1359788300000, 13.2], 
            [1359788410000, 23.1]
        ],
        "tags": {
            "project": "rola"
        }
    }
]
print(json.dumps(data))
response = requests.post(kairosdb_server + "/api/v1/datapoints", json.dumps(data))

print("Simple test [without compression]: \t%d (status code)" % response.status_code )
