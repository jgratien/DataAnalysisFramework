#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 15:01:51 2019

@author: gratienj
"""

import numpy ;
cimport numpy as np ;

cdef extern from "conflits_solverCPP.h":
    int solveC(int* conflits_list,int nb_conflits, int* res_list)
    int solveV2C(int* conflits_list,int nb_conflits, int* res_list)

def solve(conflits_list,nb_conflits):
    print("CONFLIT TYPE",conflits_list.dtype)
    cdef np.ndarray[int,ndim=1,mode='c'] buff = numpy.ascontiguousarray(conflits_list,dtype=conflits_list.dtype)
    cdef int* conflits_list_ptr = <int*> buff.data
    cdef int nb_labels_max = 2*nb_conflits
    res_list = numpy.zeros([2*nb_labels_max],dtype=conflits_list.dtype)
    cdef np.ndarray[int,ndim=1,mode='c'] buff2 = numpy.ascontiguousarray(res_list, dtype = conflits_list.dtype)
    cdef int* res_list_ptr = <int*> buff2.data
    
    nb_labels = solveC(conflits_list_ptr,nb_conflits,res_list_ptr)
    return nb_labels,res_list

def solveV2(conflits_list,nb_conflits):
    print("CONFLIT TYPE",conflits_list.dtype)
    cdef np.ndarray[int,ndim=1,mode='c'] buff = numpy.ascontiguousarray(conflits_list,dtype=conflits_list.dtype)
    cdef int* conflits_list_ptr = <int*> buff.data
    cdef int nb_labels_max = 2*nb_conflits
    res_list = numpy.zeros([2*nb_labels_max],dtype=conflits_list.dtype)
    cdef np.ndarray[int,ndim=1,mode='c'] buff2 = numpy.ascontiguousarray(res_list, dtype = conflits_list.dtype)
    cdef int* res_list_ptr = <int*> buff2.data
    
    nb_labels = solveV2C(conflits_list_ptr,nb_conflits,res_list_ptr)
    return nb_labels,res_list