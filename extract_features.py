# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 22:43:15 2018

@author: Waseem
"""
from __future__ import division
import math
import numpy as np

def power(my_list, pwr):
    return [x**pwr for x in my_list]

def absol(mylist):
    return [abs(x) for x in mylist]

def sqroot(mylist):
    return [math.sqrt(x) for x in mylist]

def extract_features(vibrationData, int_counter, windowSize): 
   
    nwindows = math.floor(len(vibrationData)/windowSize)    # total images
    #print (nwindows,'is window size')
    
    # the LBP block label histograms of all the images 
    #featureVectors = np.zeros((nwindows,3))
   
    fvl2 = []
    sr_counter = 0
    s_idx = 0
    for i in range(nwindows):
        
        #  adjust internal counter while sampling ABA data
        int_count = int_counter[sr_counter:sr_counter + windowSize]
        avg_icount = round(np.mean(int_count))
        sr_counter = sr_counter + round(windowSize/1.25)
        
        fvl1 = []
        window = np.array(vibrationData[s_idx:s_idx + windowSize], dtype = np.float32)
        s_idx = s_idx + round(windowSize/1.25)               # start index for i-th image
        xavp = sum(pow(window, 2))/windowSize                                           # Average power
        xrms = math.sqrt(int(sum((pow(window, 2))))/windowSize)                              # RMS
        xsra = pow((sum(np.sqrt(absol(window)))/windowSize), 2)                          #Square  root of amplitude
        xm = np.mean(window);                                                                   # Mean value
        sd = np.std(window);   
        xkv = sum(pow(((window-xm)/sd), 4))/windowSize                                  # Kurtosis value
        xsv = sum(pow(((window-xm)/sd), 3))/windowSize
        #print("xkv value:", xkv)                                   # Skewness value
        maxW = max(window)                             
        minW = min(window)
        xppv = maxW-minW                                                           # Peak to Peak value
        xcf = max(abs(window))/np.sqrt((sum(pow(window, 2))/windowSize))                   # Crest factor
        xif = max(abs(window))/(sum(abs(window))/windowSize)                          # Impulse factor
        xmf = max(abs(window))/(pow((sum(np.sqrt(abs(window)))/windowSize), 2))            # Margin factor
        xsf = np.sqrt(sum(pow(window, 2))/(windowSize))/(sum(abs(window))/windowSize)          # Shape factor
        xkf = (pow(sum(((window - xm))/sd), 4)/windowSize)/(pow((sum(pow(window, 2))/windowSize), 2))  #Kurtosis factor
        
        X = np.fft.fft(window)
        rmsf = np.sqrt(np.sum(abs(X/len(X))**2)) # RMS frequency domain

        fvl1.append(xrms)  # featureVectors(i,1) = xrms;
        fvl1.append(xsra)  # featureVectors(i,2) = xsra;
        fvl1.append(xkv)  # featureVectors(i,3) = xkv;
        fvl1.append(xsv)  # featureVectors(i,4) = xsv;
        fvl1.append(xppv)  # featureVectors(i,5) = xppv;
        fvl1.append(xcf)  # featureVectors(i,6) = xcf;
        fvl1.append(xif)  # featureVectors(i,7) = xif;
        fvl1.append(xmf)  # featureVectors(i,8) = xmf;
        fvl1.append(xsf)  # featureVectors(i,9) = xsf;
        fvl1.append(xkf)  # featureVectors(i,10) = xkf;

        fvl1.append(xm)           # featureVectors(i,11) = xm;
        fvl1.append(xavp)         # featureVectors(i,12) = xavp;
        fvl1.append(rmsf)         # featureVectors(i,13) = rmsf;
        fvl1.append(avg_icount)  # featureVectors(i,14) = int_count     keep track of internal counter
        fvl2.append(fvl1)

    featureVectors = np.array(fvl2)
    featureVectors[np.isnan(featureVectors)] = 0
    return featureVectors