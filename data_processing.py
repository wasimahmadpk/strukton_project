# -*- coding: utf-8 -*-
"""
Created on Wed Dec  5 14:42:01 2018

@author: Waseem
"""

import codecs
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import csv


def pre_processing(datafile, syncfile, segfile, poifile, processedfile):

    # read CSV file
    print('Data pre-processing is running... ')
    route_list = []
    # get data from SEG file
    with open(segfile) as csv_file:
        csv_reader = csv.reader(csv_file)
        line_count = 0
        prefixes = ["CNT_BGN", "PRV10_CNT_BGN", "PRV9_CNT_BGN"]
        for row in csv_reader:
            tempStr = ''.join(row)
            if tempStr.startswith('#') or len(tempStr) == 0:
                continue
            elif tempStr.startswith(tuple(prefixes)):
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                # print(f'\t{row[0]} works in the {row[1]} department, and was born in {row[2]}.')
                line_count += 1
                tlist = tempStr.split(";")
                route_list.append(tlist)
        print(f'Processed {line_count} lines in SEG file.')
        route_list = np.array(route_list)

    # Get data from POI file
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
                # print(f'\t{row[0]} works in the {row[1]} department, and was born in {row[2]}.')
                line_count += 1
                tlist = tempStr.split(";")
                ttlist = [float(x) for x in tlist if len(x) > 0]
                geo_list.append(ttlist)
        print(f'Processed {line_count} lines in POI file.')
        print("Program is running...")
        geo_list = np.array(geo_list)
        
    lat = geo_list[:, 1]
    lon = geo_list[:, 2]

    # Interpolation external and geo-coordinates
    # get_lat = interp1d(geo_list[:,0], lat, fill_value= 'extrapolate')
    # get_long = interp1d(geo_list[:,0], lon, fill_value= 'extrapolate')

    # read Sync CSV file

    # syncdat = []
    # with open(syncfile) as csv_file:
    #     csv_reader = csv.reader(csv_file)
    #     line_count = 0
    #     for row in csv_reader:
    #         tempStr = ''.join(row)
    #         if tempStr.startswith('#') or len(tempStr) == 0:
    #             line_count += 1
    #             continue
    #         elif tempStr.startswith('Type'):
    #             print(f'Column names are {", ".join(row)}')
    #             line_count += 1
    #         elif line_count < 5:
    #             line_count += 1
    #             continue
    #         else:
    #             # print(f'\t{row[0]} works in the {row[1]} department, and was born in {row[2]}.')
    #             line_count += 1
    #             tlist = tempStr.split(";")
    #             ttlist = []
    #             ttlist.append(tlist[1])
    #             ttlist.append(tlist[3])
    #             ttlist = [float(x) for x in ttlist if len(x) > 0]
    #             syncdat.append(ttlist)
    #     print(f'Processed {line_count} lines in POI file.')
    #     print("Program is running...")
    #     syncdat = np.array(syncdat)
    #     syncdat = pd.DataFrame(data=syncdat, columns=['IntCnt', 'ExtCnt'])

    # documented in time tdms file
    syncdat = pd.read_hdf(datafile, 'sync', mode='r')
    print(syncdat.shape)
    timedat = pd.read_hdf(datafile, 'time', mode='r', where='INTCNT >= syncdat.IntCnt.iloc[3] and INTCNT <= syncdat.IntCnt.iloc[-1]')
    get_xcount = interp1d(syncdat.IntCnt[3:-2], syncdat.ExtCnt[3:-2], fill_value='extrapolate')
    get_icount = interp1d(syncdat.ExtCnt[3:-2], syncdat.IntCnt[3:-2], fill_value='extrapolate')

    # xcounters = timedat.ExtCnt
    xcounters = np.array(get_xcount(timedat.INTCNT))
    timedat = timedat.assign(EXTCNT=xcounters)

    # Train speed calculation

    # inc_win = 1000
    # num_speed_win = round(len(timedat)/inc_win)
    # start_idx = 0
    # train_speed = []
    # for s in range(num_speed_win):
    #
    #     if start_idx + inc_win < len(timedat):
    #         diff_idx = timedat.index.values[start_idx + inc_win] - timedat.index.values[start_idx]
    #         diff_ict = timedat['INTCNT'].iloc[start_idx + inc_win] - timedat['INTCNT'].iloc[start_idx]
    #         vel = (diff_ict/diff_idx) * 23.04
    #         start_idx = start_idx + inc_win
    #         train_speed = train_speed + [vel]*inc_win
    #
    # train_speed = pd.DataFrame(train_speed)
    # plt.plot(train_speed)
    # plt.xlabel('Data Counters')
    # plt.xlabel('Train Speed (km/h)')

    # Get rail objects location

    # obj_counters = np.array([])
    # cntval = []
    # cntstart = []
    # cntstop = []
    # with open(r'F:\strukton_project\Groningen\labeledData\temp_dist.csv') as csv_file:
    #     csv_reader = csv.reader(csv_file)
    #     line_count = 0
    #
    #     for row in csv_reader:
    #         tempStr = ''.join(row)
    #         if tempStr.startswith('#') or len(tempStr) == 0:
    #             continue
    #         elif tempStr.startswith('Numbers'):
    #             print(f'Column names are {", ".join(row)}')
    #             line_count += 1
    #         else:
    #             line_count += 1
    #             tlist = tempStr.split(";")
    #             if tlist[6] == 'D:\\Prorail\\Data\\Groningen\\171128\\Prorail17112805si12':
    #                 if int(tlist[10]) == 1 or int(tlist[11]) == 1 or int(tlist[12]) == 1 or int(tlist[14]) == 1 or int(
    #                         tlist[15]) == 1 or int(tlist[16]) == 1:
    #                     cntstart.append(int(tlist[4]) - 500)
    #                     cntstop.append(int(tlist[4]) + 500)
    #     print(f'Processed {line_count} lines in rail_objects file.')

    ################################################################

    # Populating Track and ERS values
    edir, tdir = 0, 0
    switch_start = []
    switch_end = []
    for i in range(len(route_list)-2):
        if i == 0:
            start_ind, stop_ind = int(route_list[i, 0]), int(route_list[i, 1])
            edir = np.zeros(len(xcounters[(start_ind < xcounters) & (xcounters < stop_ind)]))
            edir.fill(int(route_list[i, 14]))
            tdir = np.repeat(route_list[i, 15], len(edir))
            if route_list[i, 11] != '':
                switch_start.append(start_ind)
                switch_end.append(stop_ind)
        else:
            start_ind, stop_ind = int(route_list[i, 0]), int(route_list[i, 1])
            temp = np.zeros(len(xcounters[(start_ind < xcounters) & (xcounters < stop_ind)]))
            edval = int(route_list[i, 14])
            temp.fill(edval)
            edir = np.concatenate((edir, temp), axis=-1)
            tdval = route_list[i, 15]
            tval = np.repeat(tdval, len(temp))
            tdir = np.concatenate((tdir, tval), axis=-1)
            if route_list[i, 11] != '':
                switch_start.append(start_ind)
                switch_end.append(stop_ind)

    if len(timedat) != len(edir):
        edir = np.concatenate((edir, np.repeat(edval, (abs(len(timedat)-len(edir))))), axis=-1)
        tdir = np.concatenate((tdir, np.repeat(tdval, (abs(len(timedat)-len(tdir))))), axis=-1)
    ERS_DIR = edir
    TRACK_DIR = tdir
    
    timedat = timedat.assign(TRACK_DIR=TRACK_DIR, ERS_DIR=ERS_DIR)
    
    # CHA1 = np.array(timedat.CHA1)
    # CHA2 = np.array(timedat.CHA2)
    # CHA3 = np.array(timedat.CHA3)
    
    # CHB1 = np.array(timedat.CHB1)
    # CHB2 = np.array(timedat.CHB2)
    # CHB3 = np.array(timedat.CHB3)

    # # 2. Transformmed channels
    # CHC1 = np.empty(len(tdir), dtype=object)
    # CHC2 = np.empty(len(tdir), dtype=object)
    # CHC3 = np.empty(len(tdir), dtype=object)
    #
    # CHC1[(tdir == 'Op') & (edir == 1)] = CHA1[(tdir == 'Op') & (edir == 1)]
    # CHC1[(tdir == 'Op') & (edir == -1)] = CHB1[(tdir == 'Op') & (edir == -1)]
    # CHC1[(tdir == 'Af') & (edir == 1)] = CHB1[(tdir == 'Af') & (edir == 1)]
    # CHC1[(tdir == 'Af') & (edir == -1)] = CHA1[(tdir == 'Af') & (edir == -1)]
    #
    # # CHC2[(tdir=='Op') & (edir==1)] = CHA2[(tdir=='Op') & (edir==1)]
    # # CHC2[(tdir=='Op') & (edir==-1)] = CHB2[(tdir=='Op') & (edir==-1)]
    # # CHC2[(tdir=='Af') & (edir==1)] = CHB2[(tdir=='Af') & (edir==1)]
    # # CHC2[(tdir=='Af') & (edir==-1)] = CHA2[(tdir=='Af') & (edir==-1)]
    #
    # CHC3[(tdir == 'Op') & (edir == 1)] = CHA3[(tdir == 'Op') & (edir == 1)]
    # CHC3[(tdir == 'Op') & (edir == -1)] = CHB3[(tdir == 'Op') & (edir == -1)]
    # CHC3[(tdir == 'Af') & (edir == 1)] = CHB3[(tdir == 'Af') & (edir == 1)]
    # CHC3[(tdir == 'Af') & (edir == -1)] = CHA3[(tdir == 'Af') & (edir == -1)]
    #
    # CHD1 = np.empty(len(tdir), dtype=object)
    # CHD2 = np.empty(len(tdir), dtype=object)
    # CHD3 = np.empty(len(tdir), dtype=object)
    #
    # CHD1[(tdir == 'Op') & (edir == 1)] = CHB1[(tdir == 'Op') & (edir == 1)]
    # CHD1[(tdir == 'Op') & (edir == -1)] = CHA1[(tdir == 'Op') & (edir == -1)]
    # CHD1[(tdir == 'Af') & (edir == 1)] = CHA1[(tdir == 'Af') & (edir == 1)]
    # CHD1[(tdir == 'Af') & (edir == -1)] = CHB1[(tdir == 'Af') & (edir == -1)]
    #
    # # CHD2[(tdir == 'Op') & (edir == 1)] = CHB2[(tdir == 'Op') & (edir == 1)]
    # # CHD2[(tdir == 'Op') & (edir == -1)] = CHA2[(tdir == 'Op') & (edir == -1)]
    # # CHD2[(tdir == 'Af') & (edir == 1)] = CHA2[(tdir == 'Af') & (edir == 1)]
    # # CHD2[(tdir == 'Af') & (edir == -1)] = CHB2[(tdir == 'Af') & (edir == -1)]
    #
    # CHD3[(tdir == 'Op') & (edir == 1)] = CHB3[(tdir == 'Op') & (edir == 1)]
    # CHD3[(tdir == 'Op') & (edir == -1)] = CHA3[(tdir == 'Op') & (edir == -1)]
    # CHD3[(tdir == 'Af') & (edir == 1)] = CHA3[(tdir == 'Af') & (edir == 1)]
    # CHD3[(tdir == 'Af') & (edir == -1)] = CHB3[(tdir == 'Af') & (edir == -1)]

    # LAT = np.array(get_lat(xcounters))
    # LON = np.array(get_long(xcounters))

    timedat = timedat.drop(['CHA2', 'CHB2'], axis=1)
    # timedat = timedat.assign(CHC1=CHC1, CHC3=CHC3, CHD1=CHD1, CHD3=CHD3)
    
    switch_counters = np.array([])
    
    for z in range(len(switch_start)):
        temparr = np.array(timedat[(timedat.EXTCNT >= switch_start[z]) & (timedat.EXTCNT <= switch_end[z])].index)
        switch_counters = np.concatenate((switch_counters, temparr), axis=0)

    # chc1_mean = np.mean(timedat.CHC1)
    # chc3_mean = np.mean(timedat.CHC3)
    # chd1_mean = np.mean(timedat.CHD1)
    # chd3_mean = np.mean(timedat.CHD3)

    cha1_mean = np.mean(timedat.CHA1)
    cha3_mean = np.mean(timedat.CHA3)
    chb1_mean = np.mean(timedat.CHB1)
    chb3_mean = np.mean(timedat.CHB3)

    # timedat.CHC1[list(switch_counters)] = chc1_mean
    # timedat.CHC3[list(switch_counters)] = chc3_mean
    # timedat.CHD1[list(switch_counters)] = chd1_mean
    # timedat.CHD3[list(switch_counters)] = chd3_mean
    switch_counters = list(set(switch_counters))
    # timedat.CHA1[switch_counters] = cha1_mean
    # timedat.CHA3[switch_counters] = cha3_mean
    # timedat.CHB1[switch_counters] = chb1_mean
    # timedat.CHB3[switch_counters] = chb3_mean

    timedat.at[switch_counters, 'CHA1'] = cha1_mean
    timedat.at[switch_counters, 'CHA3'] = cha3_mean
    timedat.at[switch_counters, 'CHB1'] = chb1_mean
    timedat.at[switch_counters, 'CHB3'] = chb3_mean

    # for z in range(len(cntstart)):
    #     temparr = np.array(timedat[(timedat.EXTCNT >= cntstart[z]) & (timedat.EXTCNT <= cntstop[z])].index)
    #     obj_counters = np.concatenate((obj_counters, temparr), axis=0)

    # timedat.CHC1[list(obj_counters)] = chc1_mean
    # timedat.CHC3[list(obj_counters)] = chc3_mean
    # timedat.CHD1[list(obj_counters)] = chd1_mean
    # timedat.CHD3[list(obj_counters)] = chd3_mean

    # timedat.CHA1[list(obj_counters)] = cha1_mean
    # timedat.CHA3[list(obj_counters)] = cha3_mean
    # timedat.CHB1[list(obj_counters)] = chb1_mean
    # timedat.CHB3[list(obj_counters)] = chb3_mean

    # timedat = timedat.drop(list(switch_counters), axis=0)
    return timedat
    # timedat.to_hdf(processedfile, key='processed', mode='w')
