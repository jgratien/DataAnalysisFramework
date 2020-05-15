import json
import argparse
import tracer_utils
import requests
import copy
from kafka import KafkaConsumer,TopicPartition
from opentracing_instrumentation.request_context import get_current_span, span_in_context
import math
from datetime import datetime
from cerberus import Validator

def consumer_single_topic(topic, metric, source):
    print("fetching data from topic : ",topic)
    consumer = KafkaConsumer(bootstrap_servers='localhost:9092')
    tp = TopicPartition(topic,0)
    consumer.assign([tp])
    consumer.seek_to_end(tp)
    lastOffset = consumer.position(tp)
    print("lastOffset : ",lastOffset)
    consumer.seek_to_beginning(tp)
    firstOffset = consumer.position(tp)
    print("firstOffset : ",firstOffset)
    print(lastOffset-firstOffset, " data fetched")
    #end
    data =[
        {
        "name": metric,
        "datapoints": [],
        "tags": {
            "source":source,
            "column":"all"
            },
        "type": "string"
        }
    ]
    #print("data sturcture selected : type ",structure_type)
    with tracer.start_span('collect_data',child_of=get_current_span()) as span:
        span.set_tag('kafka','collect_data_eolienne_DT')
        with span_in_context(span):
            list_msg = []
            for message in consumer:
                msg = message.value.decode()
                list_msg.append(msg)
                if message.offset == lastOffset - 1:
                    consumer.close()
                    break
            # Insert validation test data
            if topic == "smartGrid":        
                list_msg.append("0:01/01/2019 09:15:12;;1.000000000;100.0")
                list_msg.append("0:01/01/2019 09:15:12;CRY.CENTRALE_SOLAIRE.CRY_act_prod_pow;;100.0")
            if topic == "eolienne_DT":
                list_msg.append("6:02/10/2019 09:11:08;6;;888888,00;;17,00;0,00;1,008;19,966;43,247597;-0,384963;91,8000;34,200;1,015;14,600;87,200;316,80;3,40;315,80;3,50;0,0000;0,0000;0,0000;0,0000;0,000000;0,000000;0,00;0,00;0,00;0,00;0,00;0,00;0,00;0,00;0,00;0,000000;0,000000;999,00;0,00;0,00;0,00;0,00;0,00;0,00;0,00;0,00;0,00;0,00;0,00;0,00;0,00")
            for index,msg in enumerate(list_msg,start=1):
                dict_item = str_to_dict(msg, topic)
                #print(dict_item)
                error = clean_data(dict_item, topic, index)
                if error == True :    
                    data_treated = type_convert(msg)
                    data[0]["datapoints"].append(data_treated)
                else : 
                    continue
            print(data[0]['datapoints'][0:2])
            print(data[0]['datapoints'][-1])
            return data


def str_to_dict(data, topic):
    head_smartGrid=["timestamp","tagname","value","quality"]
    head_eolienne=['Heure','Temps écoulé','Latitude','Longitude',
          'Altitude','Head_Rel_True North','Pressure',
          'Temperature','Humidity','MDA Wnd Dir','MDA Wnd Speed',
          'MWD Wind Dir','MWD Wind Speed','CavityPressure',
          'CavityTemp','CH4','CH4_dry','C2H6','C2H6_dry',
          '13CH4','H2O','CO2','C2C1Ratio','Delta_iCH4_Raw',
          'HP_Delta_iCH4_30s','HP_Delta_iCH4_2min','HP_Delta_iCH4_5min']
    
    if topic == "smartGrid":
        col = head_smartGrid
    if topic == "eolienne_DT":
        col = head_eolienne
    
    info=data.split(":",1)[1].split(";")
    dict_item ={col[i]:info[i] for i in range(len(col))}
    return dict_item
                
                
def clean_data(data, topic, index):
    schema_eolienne =  {
    "Heure":{'type': 'string','required': True,'empty': False},
    "Temps écoulé":{'type': 'string','required': True,'empty': False},
    "Latitude":{'type': 'string','required': True,'empty': False},
    "Longitude":{'type': 'string','required': True,'empty': False},
    "Altitude":{'type': 'string','required': True,'empty': False},
    "Head_Rel_True North":{'type': 'string','required': True,'empty': False},
    "Pressure":{'type': 'string','required': True,'empty': False},
    "Temperature":{'type': 'string','required': True,'empty': False},
    "Humidity":{'type': 'string','required': True,'empty': False},
    "MDA Wnd Dir":{'type': 'string','required': True,'empty': False},
    "MDA Wnd Speed":{'type': 'string','required': True,'empty': False},
    "MWD Wind Dir":{'type': 'string','required': True,'empty': False},
    "MWD Wind Speed":{'type': 'string','required': True,'empty': False},
    "CavityPressure":{'type': 'string','required': True,'empty': False},    
    "CavityTemp":{'type': 'string','required': True,'empty': False},
    "CH4":{'type': 'string','required': True,'empty': False},
    "CH4_dry":{'type': 'string','required': True,'empty': False},
    "C2H6":{'type': 'string','required': True,'empty': False},
    "C2H6_dry":{'type': 'string','required': True,'empty': False},
    "13CH4":{'type': 'string','required': True,'empty': False},
    "H2O":{'type': 'string','required': True,'empty': False},
    "CO2":{'type': 'string','required': True,'empty': False},
    "C2C1Ratio":{'type': 'string','required': True,'empty': False},
    "Delta_iCH4_Raw":{'type': 'string','required': True,'empty': False},
    "HP_Delta_iCH4_30s":{'type': 'string','required': True,'empty': False},
    "HP_Delta_iCH4_2min":{'type': 'string','required': True,'empty': False},
    "HP_Delta_iCH4_5min":{'type': 'string','required': True,'empty': False}
    }
    schema_smartGrid = {
    "timestamp":{'type': 'string','required': True,'empty': False},
    "tagname":{'type': 'string','required': True,'empty': False},
    "value":{'type': 'string','required': True,'empty': False},
    "quality":{'type': 'string','required': True,'empty': False}
    }
    
    if topic == "smartGrid":
        schema = schema_smartGrid
    if topic == "eolienne_DT":
        schema = schema_eolienne
    
    v = Validator(schema)
    res = v.validate(data)
    if (res == False):
        print("corrupt data in line :",index,", error : ",v.errors)
    return res           
                
def str_to_unix(date):
    dt = datetime.strptime(date, '%d/%m/%Y %H:%M:%S')
    epoch = datetime.utcfromtimestamp(0)
    return int((dt - epoch).total_seconds())*1000
                
def type_convert(data):
    data = data.replace(',', '.')
    time = str_to_unix(data.split(";",1)[0].split(":",1)[1])
    data_treated = [time, data.split(";",1)[1]]
    return data_treated

def metric_generator(data, topic):
    head_smartGrid=["timetamp","tagname","value","quality"]
    head_eolienne=['Temps écoulé', '4069 state', 'Battery voltage', 'Flow SP',
       'Unit Code', 'Flow M', 'Pressure', 'Temperature', 'Latitude',
       'Longitude', 'Altitude', 'Head. Rel. True North', 'Pressure.1',
       'Temperature.1', 'Humidity', 'MDA Wnd Dir', 'MDA Wnd Speed',
       'MWD Wind Dir', 'MWD Wind Speed', 'Gaz Concentration 1',
       'Gaz Concentration 2', 'Gaz Concentration 3', 'Gaz Concentration 4',
       'SPA 1', 'SPA 2', 'Cellule Photo', 'Temperature.2', 'Pressure.2',
       'Flow MassFlow 1', 'NOTUSED Flow MassFlow 2', 'Flow', 'Humidity.1',
       'Test', 'Details', 'SPA 3', 'SPA 4', 'CavityPressure', 'CavityTemp',
       'CH4', 'CH4_dry', 'C2H6', 'C2H6_dry', '13CH4', 'H2O', 'CO2',
       'C2C1Ratio', 'Delta_iCH4_Raw', 'HP_Delta_iCH4_30s',
       'HP_Delta_iCH4_2min', 'HP_Delta_iCH4_5min']
    data_list=[]
    
    if topic == "smartGrid":
        for i in range(len(head_smartGrid)):
            col = head_smartGrid[i]
            #print("current col name : ",col)
            new_data = copy.deepcopy(data)
            new_data[0]['tags'].update(column=col)
            for j in range(len(new_data[0]['datapoints'])):
                #print(i,', ',j)
                new_data[0]['datapoints'][j][1] = new_data[0]['datapoints'][j][1].split(";")[i]
            data_list.append(new_data)           
        return data_list
    
    if topic == "eolienne_DT":
        for i in range(len(head_eolienne)):
            col = head_eolienne[i]
            #print("current col name : ",col)
            new_data = copy.deepcopy(data)
            new_data[0]['tags'].update(column=col)
            for j in range(len(new_data[0]['datapoints'])):
                #print(i,', ',j)
                new_data[0]['datapoints'][j][1] = new_data[0]['datapoints'][j][1].split(";")[i]
            data_list.append(new_data)           
        return data_list        

def insert_bulk(data):
    with tracer.start_span('insert_bulk',child_of=get_current_span()) as span:
        span.set_tag('kairosdb','operation:insert_bulk')
        with span_in_context(span):
            response = requests.post(kairosdb_server + "/api/v1/datapoints", json.dumps(data))
            print("insertion test [without compression]: \t%d (status code)" % response.status_code )
            
def test_insert_bulk(topic, metric, source, structure):
    with tracer.start_span('test_bulk_insertion') as span:
        span.set_tag('kairosdb','insertion_test')
        with span_in_context(span):
            data=consumer_single_topic(topic, metric, source)
            if structure==1:
                insert_bulk(data)
            if structure==2:
                print("")
                
def insert_batch(data,batch_size):
    with tracer.start_span('insert_bulk',child_of=get_current_span()) as span:
        span.set_tag('kairosdb','operation:insert_batch')
        with span_in_context(span):    
            list_size = math.ceil(len(data[0]['datapoints'])/batch_size)
            print(list_size , " lists found")
            chunks = [data[0]['datapoints'][batch_size*i:batch_size*(i+1)] for i in range(list_size)]            
            for item in chunks:
                print("-----------------------------------------------")
                print(len(item), " data inserted")
                new_data = data
                new_data[0]['datapoints'] = item
                #print(new_data)
                response = requests.post(kairosdb_server + "/api/v1/datapoints", json.dumps(new_data))
                print("insertion test [without compression]: \t%d (status code)" % response.status_code )

        
def test_insert_batch(topic, metric, source, batch_size):
    with tracer.start_span('test_batch_insertion') as span:
        span.set_tag('kairosdb','insertion_test') 
        with span_in_context(span):
            data=consumer_single_topic(topic, metric, source)
            insert_batch(data,batch_size)  
            
def find_all_data(metric):
    with tracer.start_span('read_data') as span:
        span.set_tag('kairosdb','operation:read_all_data')
        with span_in_context(span):
            query = {
            "start_absolute":1,
            "metrics": [
                {
                    "name": metric
                }
            ]}
            response = requests.post(kairosdb_server + "/api/v1/datapoints/query", data=json.dumps(query))
            print("Status code: %d" % response.status_code)
            print("JSON response:")
            print(response.json())
            print(len(response.json()['queries'][0]['results'][0]['values'])," data fetched from kairosDB")
            
def delete_all_data(metric):
    with tracer.start_span('delete_data',child_of=get_current_span()) as span:
        span.set_tag('kairosdb','operation:delete_all_data')
        with span_in_context(span):    
            query = {
                "start_absolute":1,
                "metrics": [
                    {
                      "name": metric,
                    }
                ]}
            response = requests.post(kairosdb_server + "/api/v1/datapoints/delete", data=json.dumps(query))
            print("Status code (204 = Okay): %d" % response.status_code)
        
def main():   
    global tracer
    global kairosdb_server 

    parser = argparse.ArgumentParser(description='KairosDB test functions')
    parser.add_argument("--function",choices=["test_insert_bulk", "test_insert_batch","find_some_data","find_all_data","find_some_data","delete_all_data","test","validate"],required=True, type=str, help="Function name")
    parser.add_argument("--batch",default=25, type=int, help="Insert batch size")
    parser.add_argument("--metric",default="kairosdb_test", type=str, help="metric name")
    parser.add_argument("--topic",default="eolienne_DT",choices=["eolienne_DT","pollution","smartGrid"], type=str, help="Topic name")
    parser.add_argument("--tracer",default="influxdb_test_eolienne_DT", type=str, help="tracer name")
    parser.add_argument("--source",default="eolienne", choices=["eolienne","pollution","smartGrid"], type=str, help="test data source")
    parser.add_argument("--structure",default=1, choices=[1,2], type=int, help="test data structure")
    parser.add_argument("--time",default="02/10/2019 09:00:00", type=str, help="query time value")
    parser.add_argument("--query",default='{"start_absolute":1,"metrics": [{"name": "test_eolienne","tags": {"column" : ["Temps écoulé"]}}]}', type=str, help="input query dictionary")
    
    args=parser.parse_args()
    fuc=args.function
    batch_size=args.batch
    topic=args.topic
    tracer_name=args.tracer
    metric=args.metric
    source=args.source
    structure=args.structure
    time=args.time
    query=args.query
    
    tracer = tracer_utils.init_tracer(tracer_name) 
    kairosdb_server = "http://localhost:9080"
    
    if fuc == "test_insert_bulk":
        test_insert_bulk(topic, metric, source, structure)
        
    if fuc == "test_insert_batch":
        test_insert_batch(topic, metric, source, batch_size)
        
    if fuc == "find_all_data":
        find_all_data(metric)
        
    if fuc == "delete_all_data":
        delete_all_data(metric)
        
    if fuc == "test":   
        data=consumer_single_topic(topic, metric, source)
        results = metric_generator(data, topic)
        for item in results : 
            response = requests.post(kairosdb_server + "/api/v1/datapoints", json.dumps(item))
            print("insertion test [without compression]: \t%d (status code)" % response.status_code )

        #print(results)
    if fuc == "find_some_data":
        q=json.loads(query)
        response = requests.post(kairosdb_server + "/api/v1/datapoints/query", data=json.dumps(q))
        print("Status code: %d" % response.status_code)
        print("JSON response:")
        print(response.json())
        print(len(response.json()['queries'][0]['results'][0]['values'])," data fetched from kairosDB")
        
if __name__=="__main__":
    main()