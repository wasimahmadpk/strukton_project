# -*- coding: utf-8 -*-
"""
Created on Tue Dec 18 16:27:50 2018

@author: Waseem
"""

import numpy as np

def normalize(data):
    
    norm_data = []
    mindata, maxdata = min(data), max(data)
    for i in range(len(data)):
        norm_data.append((data[i] - mindata)/(maxdata-mindata))
    return np.array(norm_data)
        
    