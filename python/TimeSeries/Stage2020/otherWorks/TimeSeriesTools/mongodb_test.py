from kafka import KafkaConsumer,TopicPartition

import sys
sys.path.append("../..")
import utils
import json
from opentracing_instrumentation.request_context import get_current_span, span_in_context
import argparse

def consumer_single_topic(topic):
    consumer = KafkaConsumer(bootstrap_servers='localhost:9092')
    tp = TopicPartition(topic,0)
    consumer.assign([tp])
    consumer.seek_to_end(tp)
    lastOffset = consumer.position(tp)
    print(lastOffset)
    consumer.seek_to_beginning(tp) 
    #end
    list_data=[]
    with tracer.start_span('collect_data',child_of=get_current_span()) as span:
        span.set_tag('kafka','collect_data_jour_1')
        with span_in_context(span):
            for message in consumer:
                msg = message.value.decode()
                list_data.append(msg)
                if message.offset == lastOffset - 1:
                    print(message.offset)
                    break
            consumer.close()
            #print(list_data[0])
            list_data.append('0:;;43.41266;-0.641605;91.6;34.2;1.015;14.6;87.1;323.6;1.7;324.3;;999;0;0;0;0;0;0;0;0;0;0;0;0;0')
            new_data = str_to_dict(list_data)
            return new_data
        
def str_to_dict(list_data):
    col= ['Heure','Temps écoulé','Latitude','Longitude',
          'Altitude','Head_Rel_True North','Pressure',
          'Temperature','Humidity','MDA Wnd Dir','MDA Wnd Speed',
          'MWD Wind Dir','MWD Wind Speed','CavityPressure',
          'CavityTemp','CH4','CH4_dry','C2H6','C2H6_dry',
          '13CH4','H2O','CO2','C2C1Ratio','Delta_iCH4_Raw',
          'HP_Delta_iCH4_30s','HP_Delta_iCH4_2min','HP_Delta_iCH4_5min']
    new_dict=[]
    for item in list_data:
        info=item.split(":",1)[1].split(";")
        dict_item ={col[i]:info[i] for i in range(len(col))}
        new_dict.append(dict_item)
    verify_empty_str(new_dict)
    return new_dict

def verify_empty_str(list_dict):
    col= ['Heure','Temps écoulé','Latitude','Longitude',
          'Altitude','Head_Rel_True North','Pressure',
          'Temperature','Humidity','MDA Wnd Dir','MDA Wnd Speed',
          'MWD Wind Dir','MWD Wind Speed','CavityPressure',
          'CavityTemp','CH4','CH4_dry','C2H6','C2H6_dry',
          '13CH4','H2O','CO2','C2C1Ratio','Delta_iCH4_Raw',
          'HP_Delta_iCH4_30s','HP_Delta_iCH4_2min','HP_Delta_iCH4_5min']        
    for index,item in enumerate(list_dict,start=0):
        for i in range(len(col)) :
            if item.get(col[i]):
                continue
            else:
                print("line: ",index,", position: ",i, ", require ",col[i])        
        
def insert_bulk(list_data,collection):
    with tracer.start_span('insert_bulk',child_of=get_current_span()) as span:
        span.set_tag('mongodb','operation:insert_many')
        with span_in_context(span):
            res = collection.insert_many(list_data)
            return len(res.inserted_ids)
            
def test_insert_bulk(collection,topic):
    with tracer.start_span('test_bulk_insertion') as span:
        span.set_tag('mongodb','insertion_test')
        with span_in_context(span):
            data=consumer_single_topic(topic)
            result = insert_bulk(data,collection)
            return result
        
def insert_one(list_data,collection):
    with tracer.start_span('insert_one',child_of=get_current_span()) as span:
        span.set_tag('mongodb','operation:insert_one')
        with span_in_context(span):
            for data in list_data:
                collection.insert_one(data)

            
def test_insert_one(collection,topic):
    with tracer.start_span('test_line_insertion') as span:
        span.set_tag('mongodb','insertion_test')
        with span_in_context(span):
            data=consumer_single_topic(topic)
            insert_one(data,collection)
        
def find_all_data(collection):
    data_list=[]
    with tracer.start_span('test_find_doc') as span:
        span.set_tag('mongodb','find_all_doc')
        with span_in_context(span):
            try:
                for d in collection.find():
                    data_list.append(d)
                span.log_kv({'event': 'find all data' , 'value': len(data_list) })
                print(len(data_list), " documents found")
                span.set_tag('error', 'false')
                return data_list
            except:
                span.set_tag('error', 'true')
                return            
        
def find_some_data(collection,query):
    with tracer.start_span('test_find_doc') as span:
        span.set_tag('mongodb','aggregrate_request')
        with span_in_context(span): 
            try:
                res = collection.find(query)
                data_list = list(res)
                span.log_kv({'event': 'find data with filter' , 'value': len(data_list) })
                span.set_tag('error', 'false')
                print(len(data_list), " documents found")
                return data_list
            except:
                span.set_tag('error', 'true')
                return  
            
def update_all_data(collection,new_values):
    with tracer.start_span('test_update_doc') as span:
        span.set_tag('mongodb','update_all_doc')
        with span_in_context(span): 
            try : 
                res = collection.update_many({},new_values)
                span.set_tag('error', 'false')
                span.log_kv({'event': 'update selected field of all doc' , 'value': res.modified_count })
                print("update selected field of doc found : ",res.modified_count)
                return res.modified_count
            except:
                span.set_tag('error', 'true')
                return
        
def update_some_data(collection,query,new_values):
    with tracer.start_span('test_update_doc') as span:
        span.set_tag('mongodb','update_some_doc')
        with span_in_context(span): 
            try:
                res = collection.update_many(query,new_values)
                span.set_tag('error', 'false')
                span.log_kv({'event': 'update selected field of doc found' , 'value': res.modified_count })
                print("update selected field of doc found : ",res.modified_count)
                return res.modified_count
            except:
                span.set_tag('error', 'true')
                return

            
def main():   
    global tracer
    parser = argparse.ArgumentParser(description='MongoDB test functions')
    parser.add_argument("--function",choices=["test_insert_bulk", "test_insert_one","find_some_data","find_all_data","update_some_data","update_all_data"],required=True, type=str, help="Function name")
    parser.add_argument("--query",default='{"timestamp":{"$regex":"10:"}}', type=str, help="Input query")
    parser.add_argument("--value",default='{"$set":{"timestamp":"00/00/0000 00:00"}}', type=str, help="New value")
    parser.add_argument("--topic",default="eolienne_jour_1", type=str, help="Topic name")
    parser.add_argument("--collection",default="test_eolienne", type=str, help="collection name")
    parser.add_argument("--tracer",default="mongodb_test_eolienne_1_jour", type=str, help="tracer name")
    
    args = parser.parse_args()
    fuc=args.function
    query_string=args.query
    value=args.value
    topic=args.topic
    collection=args.collection
    tracer_name=args.tracer
    query_dict=json.loads(query_string)
    new_value=json.loads(value)    
    
    tracer = utils.init_tracer(tracer_name) 
    client = utils.mongodb_connect("localhost", 28018)
    col=client.test[collection]

    if fuc == "test_insert_one":
        test_insert_one(col,topic)
    elif fuc == "test_insert_bulk":
        test_insert_bulk(col,topic)
    elif fuc == "find_some_data":
        find_some_data(col,query_dict) 
    elif fuc == "find_all_data":
        find_all_data(col)     
    elif fuc == "update_some_data":
        update_some_data(col,query_dict,new_value) 
    elif fuc == "update_all_data":
        update_all_data(col,new_value)  
    else:
        print("Function not exist")
    
if __name__=="__main__":
    main()