# -*- coding: utf-8 -*-
"""
Created on Wed Dec  5 14:42:01 2018

@author: Waseem
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import csv

def pre_processing(datafile, syncfile, segfile, poifile, processedfile):
    ## read CSV file
    route_list = []
    with open(segfile) as csv_file:
        csv_reader = csv.reader(csv_file)
        line_count = 0
        for row in csv_reader:
            tempStr = ''.join(row)
            if tempStr.startswith('#') or len(tempStr) == 0:
                  continue
            elif tempStr.startswith('PRV9_CNT_BGN'):
                  print(f'Column names are {", ".join(row)}')
                  line_count += 1
            else:
                  #print(f'\t{row[0]} works in the {row[1]} department, and was born in {row[2]}.')
                  line_count += 1
                  tlist = tempStr.split(";")
                  route_list.append(tlist)
        print(f'Processed {line_count} lines in SEG file.')
        route_list = np.array(route_list)
    
    
    geo_list = []
    with open(poifile) as csv_file:
        csv_reader = csv.reader(csv_file)
        line_count = 0
        for row in csv_reader:
            tempStr = ''.join(row)
            if tempStr.startswith('#') or len(tempStr) == 0:
                  continue
            elif tempStr.startswith('CNT'):
                  print(f'Column names are {", ".join(row)}')
                  line_count += 1
            else:
                  #print(f'\t{row[0]} works in the {row[1]} department, and was born in {row[2]}.')
                  line_count += 1
                  tlist = tempStr.split(";")
    #              for k in range(len(tlist)):
    #                  print(k)
    #                  ttlist.append(float(tlist[k]))
    #              geo_list.append(ttlist)
                  ttlist = [float(x) for x in tlist if len(x)>0]
                  geo_list.append(ttlist)
        print(f'Processed {line_count} lines in POI file.')
        print ("Program is running...")
        geo_list = np.array(geo_list)
        
    lat = geo_list[:,1]
    lon = geo_list[:,2]
    
    
    ### Interpolation external and geo-coordinates
    #get_lat = interp1d(geo_list[:,0], lat, fill_value= 'extrapolate')
    get_long = interp1d(geo_list[:,0], lon, fill_value= 'extrapolate')
    
    ### documented in time tdms file
    
    syncdat = pd.read_hdf(syncfile, 'sync', mode='r')
    timedat = pd.read_hdf(datafile, 'time', mode='r', where = 'INTCNT >= syncdat.IntCnt.iloc[3] and INTCNT <= syncdat.IntCnt.iloc[-1]')
    get_xcount = interp1d(syncdat.IntCnt[3:-2],syncdat.ExtCnt[3:-2], fill_value= 'extrapolate')
    get_icount = interp1d(syncdat.ExtCnt[3:-2],syncdat.IntCnt[3:-2], fill_value= 'extrapolate')
    xcounters = np.array(get_xcount(timedat.INTCNT))
    timedat = timedat.assign(EXTCNT=xcounters)
    
#    newext = np.arange(np.ceil(timedat.EXTCNT[0]/10)*10,np.floor(timedat.EXTCNT[-1]/10)*10,100)
#    distsamp = interp1d(timedat.EXTCNT,dispchab3)
#    newdisp = distsamp(newext)
    

    # Populating Track and ERS values (Modified)
    edir, tdir = 0,0
    switch_start = []
    switch_end = []
    for i in range(len(route_list)-2):
        if i==0:
            start_ind, stop_ind = int(route_list[i,0]), int(route_list[i,1])
            edir = np.zeros(len(xcounters[(start_ind <= xcounters) & (xcounters <= stop_ind)]))
            edir.fill(int(route_list[i,14]))
            tdir = np.repeat(route_list[i,15], len(edir))
            if route_list[i,11] != '':
                switch_start.append(start_ind)
                switch_end.append(stop_ind)
        else:
            start_ind, stop_ind = int(route_list[i,0]), int(route_list[i,1])
            temp = np.zeros(len(xcounters[(start_ind <= xcounters) & (xcounters <= stop_ind)]))
            edval = int(route_list[i,14])
            temp.fill(edval)
            edir = np.concatenate((edir,temp), axis=-1)
            tdval = route_list[i,15]
            tval = np.repeat(tdval, len(temp))
            tdir = np.concatenate((tdir,tval), axis=-1)
            if route_list[i,11] != '':
                switch_start.append(start_ind)
                switch_end.append(stop_ind)

    if len(timedat) != len(edir):
        edir = np.concatenate((edir, np.repeat(edval, (len(timedat)-len(edir)))), axis=-1)
        tdir = np.concatenate((tdir, np.repeat(tdval, (len(timedat)-len(tdir)))), axis=-1)
    ERS_DIR = edir
    TRACK_DIR = tdir
    
    timedat = timedat.assign(TRACK_DIR = TRACK_DIR, ERS_DIR = ERS_DIR)
    
    CHA1 = np.array(timedat.CHA1)
    CHA2 = np.array(timedat.CHA2)
    CHA3 = np.array(timedat.CHA3)
    
    CHB1 = np.array(timedat.CHB1)
    CHB2 = np.array(timedat.CHB2)
    CHB3 = np.array(timedat.CHB3)

    #2. Transformmed channels
    CHC1 = np.empty(len(tdir),dtype=object)
    CHC2 = np.empty(len(tdir),dtype=object)
    CHC3 = np.empty(len(tdir),dtype=object)
    
    CHC1[(tdir=='Op') & (edir==1)] = CHA1[(tdir=='Op') & (edir==1)]
    CHC1[(tdir=='Op') & (edir==-1)] = CHB1[(tdir=='Op') & (edir==-1)]
    CHC1[(tdir=='Af') & (edir==1)] = CHB1[(tdir=='Af') & (edir==1)]
    CHC1[(tdir=='Af') & (edir==-1)] = CHA1[(tdir=='Af') & (edir==-1)]
    
#    CHC2[(tdir=='Op') & (edir==1)] = CHA2[(tdir=='Op') & (edir==1)]
#    CHC2[(tdir=='Op') & (edir==-1)] = CHB2[(tdir=='Op') & (edir==-1)]
#    CHC2[(tdir=='Af') & (edir==1)] = CHB2[(tdir=='Af') & (edir==1)]
#    CHC2[(tdir=='Af') & (edir==-1)] = CHA2[(tdir=='Af') & (edir==-1)]
    
    CHC3[(tdir=='Op') & (edir==1)] = CHA3[(tdir=='Op') & (edir==1)]
    CHC3[(tdir=='Op') & (edir==-1)] = CHB3[(tdir=='Op') & (edir==-1)]
    CHC3[(tdir=='Af') & (edir==1)] = CHB3[(tdir=='Af') & (edir==1)]
    CHC3[(tdir=='Af') & (edir==-1)] = CHA3[(tdir=='Af') & (edir==-1)]

    CHD1 = np.empty(len(tdir), dtype=object)
    CHD2 = np.empty(len(tdir), dtype=object)
    CHD3 = np.empty(len(tdir), dtype=object)

    CHD1[(tdir == 'Op') & (edir == 1)] = CHB1[(tdir == 'Op') & (edir == 1)]
    CHD1[(tdir == 'Op') & (edir == -1)] = CHA1[(tdir == 'Op') & (edir == -1)]
    CHD1[(tdir == 'Af') & (edir == 1)] = CHA1[(tdir == 'Af') & (edir == 1)]
    CHD1[(tdir == 'Af') & (edir == -1)] = CHB1[(tdir == 'Af') & (edir == -1)]

#    CHD2[(tdir == 'Op') & (edir == 1)] = CHB2[(tdir == 'Op') & (edir == 1)]
#    CHD2[(tdir == 'Op') & (edir == -1)] = CHA2[(tdir == 'Op') & (edir == -1)]
#    CHD2[(tdir == 'Af') & (edir == 1)] = CHA2[(tdir == 'Af') & (edir == 1)]
#    CHD2[(tdir == 'Af') & (edir == -1)] = CHB2[(tdir == 'Af') & (edir == -1)]

    CHD3[(tdir == 'Op') & (edir == 1)] = CHB3[(tdir == 'Op') & (edir == 1)]
    CHD3[(tdir == 'Op') & (edir == -1)] = CHA3[(tdir == 'Op') & (edir == -1)]
    CHD3[(tdir == 'Af') & (edir == 1)] = CHA3[(tdir == 'Af') & (edir == 1)]
    CHD3[(tdir == 'Af') & (edir == -1)] = CHB3[(tdir == 'Af') & (edir == -1)]

    #LAT = np.array(get_lat(xcounters))
    #LON = np.array(get_long(xcounters))

    timedat = timedat.drop(['CHA1', 'CHA2', 'CHA3', 'CHB1', 'CHB2', 'CHB3'], axis = 1)
    timedat = timedat.assign(CHC1=CHC1, CHC3=CHC3, CHD1=CHD1, CHD3=CHD3)
    
    switch_counters = np.array([])
    
    for z in range(len(switch_start)):
        temparr = np.array(timedat[(timedat.EXTCNT >= switch_start[z]) & (timedat.EXTCNT <= switch_end[z])].index)
        switch_counters = np.concatenate((switch_counters, temparr),axis=0)
    
    timedat = timedat.drop(list(switch_counters), axis=0)
    timedat.to_hdf(processedfile, key='processed', mode='w')
