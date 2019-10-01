# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 22:43:15 2018

@author: Waseem
"""
from __future__ import division
import math
import numpy as np


def extract_features(vibration_data, int_counter, window_size):

    # total windows
    nwindows = math.floor(len(vibration_data)/window_size)
   
    fvl2 = []
    sr_counter = 0
    s_idx = 0
    for i in range(nwindows):
        
        #  adjust internal counter while sampling ABA data
        int_count = int_counter[sr_counter:sr_counter + window_size]
        avg_icount = round(np.mean(int_count))
        sr_counter = sr_counter + round(window_size/1)
        
        fvl1 = []
        window = np.array(vibration_data[s_idx:s_idx + window_size], dtype=np.float32)

        # list of extracted features from ABA signal
        s_idx = s_idx + round(window_size/1)                   # start index for i-th window
        xavp = sum(pow(window, 2))/window_size                    # Average power
        xrms = math.sqrt(sum((pow(window, 2)))/window_size)       # RMS
        xsra = pow((sum(np.sqrt(abs(window)))/window_size), 2)    # Square root of amplitude
        xm = np.mean(window)                                      # Mean value
        sd = np.std(window)
        xkv = sum(pow(((window-xm)/sd), 4))/window_size           # Kurtosis value
        xsv = sum(pow(((window-xm)/sd), 3))/window_size           # Skewness value
        maxW = max(window)                             
        minW = min(window)
        xppv = maxW-minW                                         # Peak to Peak value
        xcf = max(abs(window))/np.sqrt((sum(pow(window, 2))/window_size))              # Crest factor
        xif = max(abs(window))/(sum(abs(window))/window_size)                          # Impulse factor
        xmf = max(abs(window))/(pow((sum(np.sqrt(abs(window)))/window_size), 2))       # Margin factor
        xsf = np.sqrt(sum(pow(window, 2))/(window_size))/(sum(abs(window))/window_size)  # Shape factor
        xkf = (pow(sum(((window - xm))/sd), 4)/window_size)/(pow((sum(pow(window, 2))/window_size), 2))  # Kurtosis factor
        
        X = np.fft.fft(window)
        rmsf = np.sqrt(np.sum(abs(X/len(X))**2))  # RMS frequency domain

        fvl1.append(xrms)        # feature_vectors(i,1) = RMS
        fvl1.append(xsra)        # feature_vectors(i,2) = Square root of amplitude
        fvl1.append(xkv)         # feature_vectors(i,3) = Kurtosis value
        fvl1.append(xsv)         # feature_vectors(i,4) = Skewness value
        fvl1.append(xppv)        # feature_vectors(i,5) = Peak to peak
        fvl1.append(xcf)         # feature_vectors(i,6) = Crest factor
        fvl1.append(xif)         # feature_vectors(i,7) = Impulse factor
        fvl1.append(xmf)         # feature_vectors(i,8) = Margin factor
        fvl1.append(xsf)         # feature_vectors(i,9) = Shape factor
        fvl1.append(xkf)         # feature_vectors(i,10) = Kurtosis factor
        fvl1.append(xm)          # feature_vectors(i,11) = Mean value
        fvl1.append(xavp)        # feature_vectors(i,12) = Average power
        fvl1.append(rmsf)        # feature_vectors(i,13) = RMS frequency domain
        fvl1.append(avg_icount)  # feature_vectors(i,14) = internal counters     keep track of internal counter
        fvl2.append(fvl1)

    feature_vectors = np.array(fvl2)
    feature_vectors[np.isnan(feature_vectors)] = 0
    return feature_vectors