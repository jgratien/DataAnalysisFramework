#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 12:38:06 2019

@author: gratienj
"""

import findspark
findspark.init()

import pyspark
from pyspark import SparkContext, SparkConf
from pyspark.sql import SQLContext, HiveContext, Row
from pyspark.storagelevel import StorageLevel
from pyspark.streaming import StreamingContext

def create_sc(app_name='AppName',
              master='local[*]',
              executor_memory='4G',
              nb_cores='0',
              driver_memory='32G',
              max_result_size='10G'):
    sc_conf = SparkConf()
    sc_conf.setAppName(app_name)
    sc_conf.setMaster(master)
    sc_conf.set('spark.executor.memory',executor_memory)
    if nb_cores != '0':
        sc_conf.set('spark.executor.cores', nb_cores)
    sc_conf.set('spark.driver.memory', driver_memory)
    sc_conf.set('spark.cores.max', '32')
    sc_conf.set('spark.driver.maxResultSize', max_result_size)
    sc_conf.set('spark.logConf', True)
    print(sc_conf.getAll())

    sc = None
    try:
        sc.stop()
        sc = SparkContext(conf=sc_conf)
    except:
        sc = SparkContext(conf=sc_conf)

    return sc

if __name__ == "__main__":
    sc = create_sc("UnitTest")
    print('SPARK CONTEXT INFO :')
    print('      VERSION      :',sc.version)
    print('      DIVER MEMORY :',sc._conf.get('spark.driver.memory'))