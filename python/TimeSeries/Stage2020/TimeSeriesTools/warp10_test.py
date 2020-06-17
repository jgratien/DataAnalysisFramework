import json
import argparse
import utils
import requests
import pandas as pd
import os
from datetime import datetime
import mako
from mako.template import Template
from opentracing_instrumentation.request_context import get_current_span, span_in_context

def readCsv(file,folder):
    data_file=os.path.join(folder,file)
    data_df=pd.read_csv(data_file,header=0)
    return data_df

def str_to_unix(date):
    dt = datetime.strptime(date, '%d/%m/%Y %H:%M:%S')
    epoch = datetime.utcfromtimestamp(0)
    return int((dt - epoch).total_seconds())*100000

def df_to_dict_smartGrid(df):
    list_dict = []
    head = ['timestamp','tagname','class','value']
    for i in range(df.index.stop):
        serie = df.iloc[i]
        values = serie.values[0].split(";")
        values[0] = str_to_unix(values[0])
        values[2] = float(values[2])
        values[3] = float(values[3])
        values[3] = json.dumps(values[2:4])
        values[2] = "smartGrid"
        d = dict(zip(head, values))
        list_dict.append(d)
    print(len(list_dict))
    return list_dict

def df_to_dict_eolienne(df):
    list_dict = []
    head = ['timestamp','tagname','class','value']
    for col in df.columns[2:] : 
        df[col] = df[col].str.replace(',','.')
    df['Heure'] = df['Heure'].apply(str_to_unix)
    df = df.apply(pd.to_numeric)
    
    for i in range(df.index.stop):
        info = []
        serie = df.iloc[i]
        info.append(int(serie[0]))
        info.append("P25-Fuite1")
        info.append("eolienne")
        #print(len(serie[1:51].values.tolist()))
        values = json.dumps(serie[1:51].values.tolist())
        info.append(values)
        d = dict(zip(head, info))
        #print(d)
        list_dict.append(d)       
    print(len(list_dict))
    return list_dict

def insertSeriesSmartGrid(df,url,headers):
    data = df_to_dict_smartGrid(df)
    t = Template (filename= './treatement.txt')
    print('Results:\n',t.render(data=data))
    r = requests.post(url, headers=headers, data=t.render(data=data))
    print("warp10 server answer " + str(r.status_code))
    print(str(r.text))

def insertSeriesEolienne(df,url,headers):
    data = df_to_dict_eolienne(df)
    t = Template (filename= './treatement.txt')
    print('Results:\n',t.render(data=data))
    r = requests.post(url, headers=headers, data=t.render(data=data))
    print("warp10 server answer " + str(r.status_code))
    print(str(r.text))
    
def findSeries(filename,url,headers):
    print("opening " + filename)
    fout = open(filename, 'rb')
    MC2file = fout.read()
    fout.close()
    r = requests.post(url, data=MC2file)
    print(" warp10 server answer " + str(r.status_code))
    print(r.text)

def deleteSeries(headers,url,selector):
    query = url + '?deleteall&'+ selector
    #response = requests.get('http://127.0.0.1:9090/api/v0/delete?deleteall&selector=smartGrid{}', headers=headers)
    response = requests.get(query,headers=headers)
    print(query)
    return response.text

def main():   
    global tracer
    parser = argparse.ArgumentParser(description='Warp10 test functions')
    parser.add_argument("--function",choices=["insert_smartGrid","insert_eolienne","find_data_smartGrid","find_data_eolienne","delete_data"],required=True, type=str, help="Function name")
    parser.add_argument("--tracer",default="warp10_test_smartGrid", type=str, help="tracer name")
    parser.add_argument("--selector",default='selector=smartGrid{}', type=str, help="Input GTS selector")
    
    args=parser.parse_args()
    fuc=args.function
    tracer_name=args.tracer
    selector=args.selector

    headers_write = {
    'X-Warp10-Token': 'cz7.51xyPcRvOUr3KH6UPFDUNdPIshpREsi0rBEWITDEG6BsGKpHZT4qFsOwvXmzyQxJXZ_VBPv5bwSEIRsV4Plu9ocCNgzG61KP23aSYceKUZLunmw69tqQy9sLzSfb',
}
    headers_read = {
    'X-Warp10-Token': 'Vori8lnlUKnmwYThCEE4UDsoXE92bNavuvMWRuTb75xLGlvhf6UwSHdn1EellRADvocKCgmXQOPLGCRDkoi30iM3b4DJcN1DdgbI2PDQIGhr2v.VJ_5o6DUmRCOJTYBCq0_M8n50x4yNVT8GuqwLdIaaiDCtbz1jt_u2TuCyHtRYPadaKQbPt.',
}
       

    
    if fuc == "insert_smartGrid":
        data_folder= r'/home/ymo/local/work-ref/data/TimeSeries'
        test='dataHistorian-Cryolite-20190101-OneDay.csv'    
        df = readCsv(test,data_folder)
        headers = headers_write
        url = "http://127.0.0.1:9090/api/v0/update"
        insertSeriesSmartGrid(df,url,headers)
        
    if fuc == "insert_eolienne":
        data_folder= r'/home/ymo/local/work-ref/data/Lacq/fuite1/fixed'
        test='myTestCsv_0.csv' 
        df = readCsv(test,data_folder)
        df.columns.values[0] = 'Heure'
        df.columns.values[1] = 'Temps écoulé'
        headers = headers_write
        url = "http://127.0.0.1:9090/api/v0/update"
        insertSeriesEolienne(df,url,headers)      
        
    if fuc == "find_data_smartGrid":
        headers = headers_read
        url = "http://127.0.0.1:9090/api/v0/exec"
        filename = "fetch_tag.mc2"
        findSeries(filename,url,headers)
        
    if fuc == "find_data_eolienne":
        headers = headers_read
        url = "http://127.0.0.1:9090/api/v0/exec"
        filename = "fetch_eolienne.mc2"
        findSeries(filename,url,headers)
        
    if fuc == "delete_data":
        headers = headers_write
        url = 'http://127.0.0.1:9090/api/v0/delete'
        selector = 'selector=eolienne{}'
        deleteSeries(headers,url,selector)
if __name__=="__main__":
    main()