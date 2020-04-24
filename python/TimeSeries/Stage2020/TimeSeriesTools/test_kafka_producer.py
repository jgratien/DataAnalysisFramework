import pprint
import json
import time
import os
import pandas as pd
from kafka import KafkaProducer
import glob
def readFiles(path):
    all_files =  glob.glob(os.path.join(path,"*.csv"))
    li = []
    offset = 0
    for filename in all_files:
        print(filename,offset)
        df = pd.read_csv(filename, header=0, encoding='latin-1')
        li.append(df)
        offset += len(df)
    frame = pd.concat(li, axis=0, ignore_index=True)
    return frame

def producer_7j(df,topic):
    producer = KafkaProducer(bootstrap_servers="localhost:9092")
    while True:
        for index,row in df.iterrows():
            count=str(row.name)
            msg= str(row[0])
            for i in range(1,len(row)):
                msg = msg + ";"+ str(row[i])
            #Configuration of broker:auto.create.topics.enable
            msg=count+":"+msg
            producer.send(topic,msg.encode('utf8'))
            print("{} Produced records[{}] : {}".format(time.time(), index,msg))
            time.sleep(0.1)
        time.sleep(10000)

if __name__ == "__main__":
    # path = r'/work/weiy/DataAnalysisFramework-ref/data/Lacq/7jours'
    #path = r'/work/irlin355_1/gratienj/BigData/DigitalSandBox/Data/TimeSeries/Lacq/Jour_1_DT'
    #topic = "test_eolienne_DT"

    path = r'/work/irlin355_1/gratienj/BigData/DigitalSandBox/Data/TimeSeries/SmartGrid'
    topic = "test_smartgrid"

    df = readFiles(path)
    producer_7j(df,topic)
