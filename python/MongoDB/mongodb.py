#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 11:35:54 2019

@author: gratienj
"""
import os
import glob
import numpy as np
import cv2
import pymongo
import gridfs
from pymongo import MongoClient

def writeImageToDataBase(folder,collection):
    img_data = [img for img in glob.glob(os.path.join(folder,'*png'))]
    for idx,img_path in enumerate(img_data):
        print('IMAGE :',idx,img_path)
        img = cv2.imread(img_path, cv2.IMREAD_COLOR)
        img_data_id = grid_fs.put(img.tobytes())
        name=os.path.basename(img_path)
        img_doc = {"name":name,'id':idx,'data_id':img_data_id,'shape':{'nx':img.shape[0],'ny':img.shape[1],'nz':img.shape[2]}}
        img_id = collection.insert_one(img_doc).inserted_id
        print('DOC : ',img_id)    

def getImageCollectionFromDataBase(collection,gfs):
    import pprint
    for img in collection.find():
        pprint.pprint(img)
        print('ID:',img['id'])
        shape=img['shape']
        print('SHAPE',shape['nx'],shape['ny'],shape['nz'])
        data_file = gfs.find_one({"_id":img['data_id']})
        bytes_data = data_file.read()
        print('NB BYTES',bytes_data.__len__(),np.dtype('uint8').itemsize)
        array_data = np.frombuffer(bytes_data,dtype='uint8',count=int(bytes_data.__len__()/np.dtype('uint8').itemsize))
        array3D_data =np.reshape(array_data,(shape['nx'],shape['ny'],shape['nz']))
        print('SHAPE2 :',array3D_data.shape)
    
client = MongoClient('localhost', 27017)
#client = MongoClient('mongodb://%s:%s@islin-hdpnod1.ifp.fr' % ("tim8", "tim8"))

#
# GETTING a Database
db = client['img-database']
grid_fs = gridfs.GridFS(db,'bdata')

# GETTING a collection
img_collection = db['img-collection']


# INSERTING IMAGES IN DIRECTORY
dataFolder='/work/irlin355_1/gratienj/BigData/DigitalSandBox/Data/TGS/test'

getImageCollectionFromDataBase(img_collection,grid_fs)
