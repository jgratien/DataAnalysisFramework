#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 16:47:17 2019

@author: gratienj
"""
import time
import numpy as np ;
from CCL3D import resolve_labels_conflits_v2
from conflits_solver import solve, solveV2

conflits_list = [(1, 28), (3, 29), (9, 30), (55, 32), (33, 55), (55, 82), (57, 84)]
nb_conflits = len(conflits_list)

conflits = np.zeros((nb_conflits,2),dtype=int)
i=0
for c in conflits_list:
    conflits[i][0] = c[0]
    conflits[i][1] = c[1]
    i = i+1

t0 = time.process_time()
res = resolve_labels_conflits_v2(conflits, nb_conflits)
t1 = time.process_time() - t0
print(res)
print("TIME OF CORRECTION OF CONFLICTS SECOND VERSION:", t1)

conflits = np.zeros([2*len(conflits_list)],dtype=np.int32)
print("TYPE",conflits.dtype)
i=0
for c in conflits_list:
    conflits[2*i  ] = c[0]
    conflits[2*i+1] = c[1]
    i = i+1

t0 = time.process_time()
nb_label,res_list = solveV2(conflits,len(conflits_list))
t1 = time.process_time() - t0
print("TIME OF CORRECTION OF CONFLICTS CYTHON VERSION 2 :", t1)
print("NB LABELS",nb_label)
print("RESULT",res_list)

t0 = time.process_time()
nb_label,res_list = solve(conflits,len(conflits_list))
t1 = time.process_time() - t0
print("TIME OF CORRECTION OF CONFLICTS CYTHON VERSION 1 :", t1)
    
print("NB LABELS",nb_label)
print("RESULT",res_list)