#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 11:04:37 2019

@author: gratienj
"""

from libc.math cimport pow

cdef double square_and_add (double x):
    return pow(x, 2.0) + x

cpdef print_result (double x):
    print("({} ^ 2) + {} = {}".format(x, x, square_and_add(x)))
 
