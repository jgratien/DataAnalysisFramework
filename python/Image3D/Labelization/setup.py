#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 15:04:31 2019

@author: gratienj
"""

from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
from Cython.Distutils import build_ext
 
compile_args = ['-g', '-std=c++11', '-stdlib=libc++']

extensions = [
    Extension(name="conflits_solver", 
              sources=["conflits_solver.pyx","conflits_solverCPP.cpp"],
              language='c++',
              extra_compile_args=['-g', '-std=c++11'])  # à renommer selon les besoins
]
 
setup(
    cmdclass = {'build_ext':build_ext},
    ext_modules = cythonize(extensions),
)