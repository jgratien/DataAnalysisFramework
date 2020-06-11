import json
import time
import datetime
import os
import logging
import requests

class DataBaseInfo:
    HOST = 'localhost'
    PORT = '8080'

    def __init__(self,
                 host=HOST,
                 port=PORT):
        self.host = host
        self.port = port
        self.write_token = '2Xl.e.psRMuXA8mKMWwv.X1KgDXvI0H.fR69Qy34658tRMvDz.HgnKcvAErRmQB77d.Fx6u7jQ_hOOmi5OzsdK97ReYQSlBEeurxxoWDzalikccgvJIzEX1qZa1jBBOw'
        self.read_token  = 'BcquvKbk0Cd1Egb4ITqytPdXjN1kf6MTaK5hBEQfD.0rM61wEzV76nFogWt608XNQ8NCZYybDntMXSDugaTQx21jAv4qW59BM68wR.xUQxnMVwRW1Xe0q3eQw2l2swJxGe_uK2gwXGIydx_l5D5K.m8BfhSR0NQSz7Zx8ClQPhhRNFQocY_ZuV'
        
        self.read_headers = { 'X-Warp10-Token': self.read_token }
        self.write_headers = { 'X-Warp10-Token': self.write_token }
        
        self.template_path = os.path.dirname(os.path.abspath(__file__))
        
db_info = DataBaseInfo()

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

def insert_one_doc(warp10db_server,db_name, coll_name,doc):
    tags = { "db_name" : db_name }

    from mako.template import Template
    t = Template(filename=os.path.join(db_info.template_path,'insert_one.txt'))

    datapoint = { "class" : coll_name,
                  "latitude" : 0,
                  "longitude" : 0,
                  "altitude" : 0,
                  "tags" : tags,
                  "values" : [doc[0], json.dumps(doc[1])] }

    r = requests.post(warp10db_server+'/api/v0/update', headers=db_info.write_headers, data=t.render(datapoint=datapoint))
    if r.status_code != 200 :
        print(" warp10 server answer ",r.status_code)
        print(t.text)
    return r.status_code

def insert_one_doc_with_tags(warp10db_server,db_name, coll_name,tags,doc):
    query_tags = { "db_name" : db_name }
    for i,(k,v) in enumerate(tags.items()):
        query_tags[k] = v

    from mako.template import Template
    t = Template(filename=os.path.join(db_info.template_path,'insert_one.txt'))

    datapoint = {   "class" : coll_name,
                    "latitude" : 0,
                    "longitude" : 0,
                    "altitude" : 0,
                    "tags" : query_tags,
                    "values" : [doc[0], json.dumps(doc[1])] }

    r = requests.post(warp10db_server+'/api/v0/update', headers=db_info.write_headers, data=t.render(datapoint=datapoint))
    if r.status_code != 200 :
        print(" warp10 server answer ",r.status_code)
        print(t.text)
    return r.status_code

def insert_many_docs(warp10db_server,db_name, coll_name, doc_list):
    from mako.template import Template
    t = Template(filename=os.path.join(db_info.template_path,'insert_many.txt'))

    tags = { "db_name" : db_name }

    datapoint = {   "class" : coll_name,
                    "latitude" : 0,
                    "longitude" : 0,
                    "altitude" : 0,
                    "tags" : tags,
                    "values" : [[d[0], json.dumps(d[1])] for d in doc_list] }

    r = requests.post(warp10db_server+'/api/v0/update', headers=db_info.write_headers, data=t.render(datapoint=datapoint))
    if r.status_code != 200 :
        print(" warp10 server answer ",r.status_code)
        print(t.text)
    return r.status_code

def insert_many_docs_with_tags(warp10db_server,db_name, coll_name,tags,doc_list):
    from mako.template import Template
    t = Template(filename=os.path.join(db_info.template_path,'insert_many.txt'))

    query_tags = { "db_name" : db_name }
    for i,(k,v) in enumerate(tags.items()):
        query_tags[k] = v

    datapoint = {   "class" : coll_name,
                    "latitude" : 0,
                    "longitude" : 0,
                    "altitude" : 0,
                    "tags" : query_tags,
                    "values" : [[d[0], json.dumps(d[1])] for d in doc_list] }

    #print("DATAPOINTS:",t.render(datapoint=datapoint))
    r = requests.post(warp10db_server+'/api/v0/update', headers=db_info.write_headers, data=t.render(datapoint=datapoint))
    if r.status_code != 200 :
        print(" warp10 server answer ",r.status_code)
        print(t.text)
    return r.status_code

def delete_collection(warp10db_server, db_name,coll_name):
    query = warp10db_server + '?deleteall&' + coll_name+'{ \'db_name\' \' '+db_name+ '\' }'
    print(query)
    response = requests.get(query, headers=db_info.write_headers)
    return response.text

def get_all_docs(warp10db_server,db_name,coll_name):
    from mako.template import Template
    t = Template(filename=os.path.join(db_info.template_path,'fetch_coll.txt'))
    print("REQUEST:",t.render(token=self.db_info.read_token, coll_name=coll_name))
    response = requests.post(warp10db_server + "/api/v0/exec",
                                data=t.render(token=db_info.read_token,coll_name=coll_name))

    print("Status code: %d" % response.status_code)
    if response.status_code == 200:
        return response.json()
    else:
        print(response.text)
        return []

def get_docs_select_by_tags(warp10db_server, db_name, coll_name, tags):
    from mako.template import Template
    t = Template(filename=os.path.join(db_info.template_path,'fetch_select_coll.txt'))
    print("REQUEST:",t.render(token=db_info.read_token, coll_name=coll_name, tags=tags))
    response = requests.post(warp10db_server + "/api/v0/exec",
                                    data=t.render(token=db_info.read_token, coll_name=coll_name, tags=tags))

    print("Status code: %d" % response.status_code)
    if response.status_code == 200:
        return response.json()
    else:
        print(response.text)
        return []
    