#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 16:39:49 2019

@author: gratienj
"""

import os
import sys
os.environ["PYSPARK_PYTHON"] = ""
os.environ["JAVA_HOME"] = "/work/irlin355_1/gratienj/local/Java/1.8.0_92"
os.environ["SPARK_HOME"] = "/work/irlin355_1/gratienj/BigData/local/spark/spark-2.4.0-bin-hadoop2.7/"
os.environ["PYLIB"] = os.environ["SPARK_HOME"] + "/python/lib"
os.environ["PYSPARK_SUBMIT_ARGS"] = "--master local[2] pyspark-shell"

sys.path.insert(0, os.environ["PYLIB"] +"/py4j-0.10.7-src.zip")
sys.path.insert(0, os.environ["PYLIB"] +"/pyspark.zip")
import findspark as fs
fs.init()

from pyspark import SparkConf
from pyspark import SparkContext
conf = SparkConf()
conf.setMaster('yarn-client')
conf.setAppName('anaconda-pyspark')
sc = SparkContext(conf=conf)

nums= sc.parallelize([1,2,3,4])	
nums.take(1) 	

import numpy as np
import pymongo
import gridfs
from pymongo import MongoClient
import pprint

client = MongoClient('localhost', 27017)
#client = MongoClient('mongodb://%s:%s@islin-hdpnod1.ifp.fr' % ("tim8", "tim8"))

#
# GETTING a Database
db = client['img-database']
grid_fs = gridfs.GridFS(db,'bdata')

# GETTING a collection
img_collection = db['img-collection']



img = img_collection.find_one({"id":0})

pprint.pprint(img)
print('ID:',img['id'])
shape=img['shape']
print('SHAPE',shape['nx'],shape['ny'],shape['nz'])
data_file = grid_fs.find_one({"_id":img['data_id']})
bytes_data = data_file.read()
print('NB BYTES',bytes_data.__len__(),np.dtype('uint8').itemsize)
array_data = np.frombuffer(bytes_data,dtype='uint8',count=int(bytes_data.__len__()/np.dtype('uint8').itemsize))
array3D_data =np.reshape(array_data,(shape['nx'],shape['ny'],shape['nz']))
print('SHAPE2 :',array3D_data.shape)