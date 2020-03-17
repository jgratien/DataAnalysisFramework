import time
import findspark
findspark.init()
import pyspark
from pyspark import SparkContext, SparkConf
import numpy as np
from struct import unpack_from
import os
from pyspark.sql import SQLContext, HiveContext, Row
from pyspark.storagelevel import StorageLevel
from pyspark.streaming import StreamingContext

def create_sc(app_name):
    sc_conf = SparkConf()
    sc_conf.setAppName(app_name)
    sc_conf.setMaster('local[*]')
    sc_conf.set('spark.executor.memory', '6g')
    sc_conf.set('spark.executor.cores', '4')
    sc_conf.set('spark.driver.memory', '32G')
    sc_conf.set('spark.cores.max', '32')
    sc_conf.set('spark.driver.maxResultSize', '10G')
    sc_conf.set('spark.logConf', True)
    print(sc_conf.getAll())

    sc = None
    try:
        sc.stop()
        sc = SparkContext(conf=sc_conf)
    except:
        sc = SparkContext(conf=sc_conf)

    return sc

sc = create_sc("First_cube")
dataFolder = 'Binary_files'
filename = os.path.join(dataFolder,'binary_file3')
print ("VERSION SPAARK", sc.version)
t0 = time.process_time()
record_length = 1
binary_rdd = sc.binaryRecords(filename, record_length)  # .partitions(8)
# map()s each binary record to unpack() it
def func(iterator):
  for s in iterator:
     res = unpack_from('b', s)
  return res
#print("NB Partitions :", binary_rdd.getNumPartitions())
unpacked_rdd = binary_rdd.map(lambda record: unpack_from('b', record))
raw_data = unpacked_rdd.collect()
t1=time.process_time()-t0
print("HDFS READING TIME : ",t1)

