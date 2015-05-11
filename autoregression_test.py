# -*- coding: utf-8 -*-
"""
Created on Sat May  9 14:44:49 2015

@author: Yan
"""

signal = [56.0,58.0,13.0,27.0,37.0,30.0,-28.0,-53.0,-42.0,-18.0]
phi = [0,0.7777,0.0,0.2310,-0.1882,0.1078,-0.1709,0.0579,-0.1004,0.095,0.0]
for i in range(10,44100):
    x_new = 0
    for k in range(1,11):
        x_new += phi[k]*signal[i-k]
    signal.append(x_new)