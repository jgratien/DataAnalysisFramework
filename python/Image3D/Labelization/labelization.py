#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 16:44:01 2019

@author: gratienj
"""
#
#
#   10    11    12
#   20    21    22    23
#         31    31    33
#                     43
# 
#conflits_list = [(10,20),(11,21),(12,22),(21,31),(22,31),(23,33),(33,43)]
conflits_list = [(1, 28), (3, 29), (9, 30), (55, 32), (33, 55), (55, 82), (57, 84)]

import numpy as np
import time

def convert_list_to_matrix(conf_list):
    labels = []
    labels_index = {}
    for label1, label2 in conf_list:
        if label1 not in labels:
            labels_index[label1] = len(labels)
            labels.append(label1)
        if label2 not in labels:
            labels_index[label2] = len(labels)
            labels.append(label2)
    Nl = len(labels)
    Nc = len(conf_list)
    matrix_res = np.zeros((Nc + 1, Nl), dtype=int)
    for k in range(Nl):
        matrix_res[0,labels_index[labels[k]]] = labels[k]
    for k in range(Nc):
        c=conf_list[k]
        j0=labels_index[c[0]]
        j1=labels_index[c[1]]
        matrix_res[k+1, j0] = 1
        matrix_res[k+1, j1] = -1

    return matrix_res, Nc, Nl


def conflicts_reduction(A):
    nc = A.shape[0]-1
    nl = A.shape[1]
    if A.shape[0]-1 <= A.shape[1]:
        for j in range(0, nc):
            max_el = A[j + 1, j]
            idx_col = j
            if max_el == 0:
                is_found = False
                for k in range(j+1, A.shape[1]):
                     # Changer les colonnes
                     if A[j+1, k] != 0:
                         if j != k:
                            idx_col = k
                            is_found = True
                     if is_found is True :
                         break
                if is_found is True:
                    tmp = np.copy(A[:, j])
                    A[:, j] = np.copy(A[:, idx_col])
                    A[:, idx_col] = np.copy(tmp)
            Ajj = A[j + 1, j]

            # Eliminer tous les éléments non nuls de la colonne
            for i in range(j+2, A.shape[0]):
                if A[i, j] != 0:
                    A[i, :] -= A[i, j] // Ajj * A[j+1, :]


def system_resolution(A):
    nl = A.shape[1]
    nc = A.shape[0]-1
    X = np.zeros(nl, dtype=int)
    X[0:nc] = -1
    X[nc:nl] = A[0, nc:nl]
    for i in range(nc-1, -1, -1):
        s = 0
        for j in range(i+1, nl):
            s = s - A[i+1, j] * X[j]
        X[i] = s // A[i+1, i]
    return X

def resolve_labels_conflits(conflits):
    import copy
    print("CONFLITS IN",conflits)
    labels = []
    label_conflits={}
    c_index=0
    for c in conflits:
        if c[0] not in labels:
            labels.append(c[0])
            label_conflits[c[0]] = [c_index]
        else:
            label_conflits[c[0]].append(c_index)
            
        if c[1] not in labels:
            labels.append(c[1])
            label_conflits[c[1]] = [c_index]
        else:
            label_conflits[c[1]].append(c_index)
        c_index = c_index+1
    print("NB CONFLITS",c_index,len(conflits))
    print("NB LABELS",len(labels))
    print(label_conflits)
    print("REDUCE CONFLITS MATRIX")
    
    ordered_labels=[]
    ic=0
    for c in conflits:
        print("CONFLIT :",ic)
        l=c[0]
        print("LABEL",l)
        ordered_labels.append(l)
        l1=c[1]
        for k in label_conflits[l]:
            if k>ic:
                lc=conflits[k]
                print("TUP",lc,l,l1)
                lc0=lc[0]
                lc1=lc[1]
                if lc[0]==l:
                    conflits[k] = copy.deepcopy((l1,lc1))
                else:
                    conflits[k] = copy.deepcopy((lc0,l1))
                print("NEW TUP",conflits[k])
        ic=ic+1
    
    independant_labels=[]
    new_labels = {}
    for l in labels:
        if l not in ordered_labels:
            independant_labels.append(l)
            new_labels[l] = l
            
    print("REDUCED CONFLITS",conflits)
    print("DEPENDANT LABELS",ordered_labels)
    print("INDEPENDANT LABELS",independant_labels)
    nc=len(conflits)
    for i in range(nc):
        c=conflits[nc-i-1]
        new_labels[c[0]] = new_labels[c[1]]
    print("NEW LABELS",new_labels)
    return new_labels
    

mat, nc, nl = convert_list_to_matrix(conflits_list)
print("Matrice avant tri : \n", mat, nc, nl)
conflicts_reduction(mat)
print("RESULTAT : \n", mat)
X = system_resolution(mat)
print(X)
NX = resolve_labels_conflits(conflits_list)