# -*- coding: utf-8 -*-
"""
Created on Thu Feb 01 13:21:46 2018

@author: Waseem
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
#from performance import get_perform
from intersect import intersection
from data_processing import pre_processing
from geopy.distance import geodesic
from itertools import zip_longest
from data_paths import data_path
from scipy.interpolate import interp1d
from sklearn.cluster import KMeans
from extract_features import extract_features
from gmapplot import gmap_plot
from anomaly_detection import isolation_forest
from multi_anomaly_detection import multi_anomaly_detection
from sklearn.metrics import confusion_matrix
from confusion_mat import plot_confusion_matrix
import csv

#data_file = 'F:\strukton_project\Groningen\Prorail17112805si12\ABA\Prorail17112805si12\Prorail17112805si12.time.h5'
#sync_file = 'F:\strukton_project\Groningen\Prorail17112805si12\ABA\Prorail17112805si12\Prorail17112805si12.time.h5'
#seg_file = 'F:\strukton_project\Groningen\Routefile\Prorail17112805si12_seg.csv'
#poi_file = 'F:\strukton_project\Groningen\Routefile\Prorail17112805si12_poi.csv'
#processed_file = 'F:\strukton_project\Groningen\Prorail17112805si12\ABA\Prorail17112805si12\\Prorail17112805si12.processed.h5'

data_file = data_path[0]
sync_file = data_path[1]
seg_file = data_path[2]
poi_file = data_path[3]
processed_file = data_path[4]
counters_path = "F:\strukton_project\Groningen\Prorail17112805si12\ABA\Prorail17112805si12\counter_data"

if not os.path.isfile(processed_file):
    pre_processing(data_file, sync_file, seg_file, poi_file, processed_file)
else:
    geo_list = []
    with open('F:\strukton_project\Groningen\Routefile\Prorail17112805si12_poi.csv') as csv_file:
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
                  ttlist = [float(x) for x in tlist if len(x)>0]
                  geo_list.append(ttlist)
        print(f'Processed {line_count} lines in POI file.')
        geo_list = np.array(geo_list)
        
    lat = geo_list[:,1]
    lon = geo_list[:,2]
    
    
    ### Interpolation external and geo-coordinates
    get_lat = interp1d(geo_list[:,0], lat, fill_value= 'extrapolate')
    get_long = interp1d(geo_list[:,0], lon, fill_value= 'extrapolate')
    
    ## Get rail objects location
    obj_counters = np.array([])
    cntval = []
    cntstart = []
    cntstop = []
    with open(r'F:\strukton_project\Groningen\labeledData\temp_dist.csv') as csv_file:
        csv_reader = csv.reader(csv_file)
        line_count = 0
        
        for row in csv_reader:
            tempStr = ''.join(row)
            if tempStr.startswith('#') or len(tempStr) == 0:
                  continue
            elif tempStr.startswith('Numbers'):
                  print(f'Column names are {", ".join(row)}')
                  line_count += 1
            else:
                  line_count += 1
                  tlist = tempStr.split(";")
                  if tlist[6]== 'D:\\Prorail\\Data\\Groningen\\171128\\Prorail17112805si12':
                      if int(tlist[10])==1 or int(tlist[11])==1 or int(tlist[12])==1 or int(tlist[14])==1 or int(tlist[15])==1 or int(tlist[16])==1:
                          cntstart.append(int(tlist[4]) - 500)
                          cntstop.append(int(tlist[4]) + 500)
#                          temparr = np.array(list(range(cntstart, cntstop, 1)))
#                          obj_counters = np.concatenate((obj_counters, temparr), axis=0)
#                  
        print(f'Processed {line_count} lines in rail_objects file.')
        print ("Program is running...")

    
    ################################################################
    processed_data = pd.read_hdf(processed_file, 'processed', mode='r')
    
    for z in range(len(cntstart)):
        temparr = np.array(processed_data[(processed_data.EXTCNT >= cntstart[z]) & (processed_data.EXTCNT <= cntstop[z])].index)
        obj_counters = np.concatenate((obj_counters, temparr),axis=0)
    
    processed_data = processed_data.drop(list(obj_counters), axis=0)
    
    CHC1 = np.array(processed_data.CHC1)
    CHC3 = np.array(processed_data.CHC3)
    CHD1 = np.array(processed_data.CHD1)
    CHD3 = np.array(processed_data.CHD3)
    EDIR = np.array(processed_data.ERS_DIR)
    
    int_count = np.array(processed_data.INTCNT)
    ext_count = np.array(processed_data.EXTCNT)
#    date_time = syncdat.DateTime
    
    
    #Pushing & Pulling ABA data for one side (left or right)
    pull_data_chc1 = CHC1[(EDIR==1)]
    push_data_chc1 = CHC1[(EDIR==-1)]
    pull_data_chc3 = CHC3[(EDIR==1)]
    push_data_chc3 = CHC3[(EDIR==-1)]
    
    pull_int_count = int_count[(EDIR==1)]
    push_int_count = int_count[(EDIR==-1)]
    
    pull_data = np.power((np.power(pull_data_chc1,2) + np.power(pull_data_chc3,2)), 1/2)
    push_data = np.power((np.power(push_data_chc1,2) + np.power(push_data_chc3,2)), 1/2)
    
    ## Second side
    pull_data_chc1 = CHD1[(EDIR==1)]
    push_data_chc1 = CHD1[(EDIR==-1)]
    pull_data_chc3 = CHD3[(EDIR==1)]
    push_data_chc3 = CHD3[(EDIR==-1)]
    
    pull_int_count = int_count[(EDIR==1)]
    push_int_count = int_count[(EDIR==-1)]
    
    pull_data2 = np.power((np.power(pull_data_chc1,2) + np.power(pull_data_chc3,2)), 1/2)
    push_data2 = np.power((np.power(push_data_chc1,2) + np.power(push_data_chc3,2)), 1/2)
    
    ########################################
    data_list = []
    counters_list = []
    data_list.append(pull_data)
    data_list.append(push_data)
    counters_list.append(pull_int_count)
    counters_list.append(push_int_count)
    ########################################
    data_list2 = []
    data_list2.append(pull_data2)
    data_list2.append(push_data2)
    ########################################
    anom_xcount_list = []
    anom_xcount_train_list = []
    
    get_xcount = interp1d(int_count, ext_count, fill_value= 'extrapolate')
    get_icount = interp1d(ext_count, int_count, fill_value= 'extrapolate')
    #///////////// Feature Extraction //////////////
    aba_data_mode = []
    int_count_mode = []
    all_xcount_mode = []
    for i in range(len(data_list)):
    
        list_of_features = extract_features(data_list[i], counters_list[i], 3000)
        
        rms = np.array(list_of_features[:,0])
        skewness = np.array(list_of_features[:,3])
        peak_to_peak = np.array(list_of_features[:,4])
        crest_factor = np.array(list_of_features[:,5])
        rmsf = np.array(list_of_features[:,12])
        int_count = np.array(list_of_features[:,13])
        
        aba_data_mode.append(peak_to_peak)
        int_count_mode.append(int_count_mode)
        
        ## features comparison
        plt.figure(2)
        plt.subplot(411)
        plt.ylabel('RMS')
        plt.xlabel('Time')
        plt.plot(rms) 
        plt.subplot(412)
        plt.ylabel('Skewness')
        plt.xlabel('Time')
        plt.plot(skewness)
        plt.subplot(413)
        plt.ylabel('Peak to peak')
        plt.xlabel('Time')
        plt.plot(peak_to_peak)
        plt.subplot(414)
        plt.ylabel('Crest factor')
        plt.xlabel('Time')
        plt.plot(crest_factor)
        plt.show()
        print(rms)
      
        mylist = np.stack((peak_to_peak,crest_factor), axis=-1)
        
        #best_k(mylist)
        #//////K-Means Clustering and Data Labelling for Supervised Anomaly detection///////////////
        #norm_data = []
        #anom_data = []
        #kmeans = KMeans(n_clusters=2, random_state=1).fit(mylist)
        #clusters = np.array(kmeans.labels_.astype(float))
        #for i in range(len(clusters)):
        #    if clusters[i] == 0:
        #        norm_data.append(list_of_features[i,:])
        ##        plt.scatter(list_of_features[i,0],list_of_features[i,4], c = 'g', marker = '*')
        ##        plt.title("Data Clustering")
        ##        plt.xlabel("Feature 1")
        ##        plt.ylabel("Feature 2")
        ##        plt.show()
        #    elif clusters[i] ==1:
        #        anom_data.append(list_of_features[i,:])
        ##        plt.scatter(list_of_features[i,0],list_of_features[i,4], c = 'r', marker = 'o')
        ##        plt.title("Data Clustering")
        ##        plt.xlabel("Feature 1")
        ##        plt.ylabel("Feature 2")
        ##        plt.show()
        #        
        #         
        #norm_data = np.array(norm_data)
        #anom_data = np.array(anom_data)
        
        #X_train = np.concatenate((norm_data, anom_data), axis=0)
        
        #multi_anomaly_detection(norm_data, anom_data)
        
        norm_train, anom_train, norm_test, anom_test, anom_icount, anom_icount_train = isolation_forest(mylist, int_count)
        
    #    norm_train = np.concatenate(norm_train.tolist())
    #    anom_train = np.concatenate(anom_train.tolist())
    #    norm_test = np.concatenate(norm_test.tolist())
    #    anom_test = np.concatenate(anom_test.tolist())
        
        all_xcount_mode.append(get_xcount(int_count))
        anom_xcount_test = get_xcount(anom_icount)
        anom_xcount_train = get_xcount(anom_icount_train)
        anom_xcount = np.concatenate((anom_xcount_train, anom_xcount_test),axis=0)
        
        #new code for validation of anomalies
        latitude = get_lat(anom_xcount)
        longitude = get_long(anom_xcount)
        dist = [0]
        for z in range(len(latitude)-1):
            point_one = (latitude[z], longitude[z])
            point_two = (latitude[z+1], longitude[z+1])
            distance = geodesic(point_one, point_two).km
            dist.append(1000 * distance)
         
            
        anom_xcount = [str(x) for x in anom_xcount]
        latitude = [str(x) for x in latitude]
        longitude = [str(x) for x in longitude]
        dist = [str(x) for x in dist]
        
#        d = [list(anom_xcount), list(latitude), list(longitude), dist]
#        write_data = zip_longest(*d, fillvalue = '')
        write_data = zip(anom_xcount, latitude, longitude, dist)
        train_mode = 'pushing' if i else 'pulling' 
        with open(counters_path + '\prorail17112805si12_'+ train_mode +'.csv', 'w', newline='') as file:
            try:
                writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(['counters', 'latitude','longitude','distance'])
                for cnt, lat, lon, dist in write_data:
                    writer.writerow([cnt, lat, lon, dist])
            finally:
                file.close()
        #######################################################
        
        
        anom_xcount_list.append(anom_xcount)
        anom_xcount_train_list.append(anom_xcount_train)
        
        lat_list = get_lat(anom_xcount).tolist()
        long_list = get_long(anom_xcount).tolist()
        lat_list_train = get_lat(anom_xcount_train).tolist()
        long_list_train = get_long(anom_xcount_train).tolist()
        
        #    dlist = []
        #    xcgcode = []
        #    
        #geocodes_train = np.array(geocode)
        #unique_gcodes_train = np.unique(geocodes_train, axis = 0)
        #lat_list_train = unique_gcodes_train[:, 1].tolist()
        #long_list_train = unique_gcodes_train[:, 2].tolist()
        #
        #lat_list_train = [float(i) for i in lat_list_train]
        #long_list_train = [float(j) for j in lon_list_train]
        
        # Calculation of time of data acquisition
        
        #geo_xcount = geo_list[:,0]
        #geo_icount = get_icount(geo_xcount)
        #geo_icount[np.isnan(geo_icount)] = 0
        
        #dlist = []
        #dtval = []
        #
        #for j in range(len(geo_icount)):
        #    tval1 = geo_icount[j]
        #    for k in range(len(int_count2)):
        #        tval2 = int(int_count2[k])
        #        diff = abs(tval2 - tval1)
        #        dlist.append(diff)
        #    dlist = np.array(dlist)
        #    indmin = np.unravel_index(np.argmin(dlist, axis=None), dlist.shape)
        #    datetime = date_time[indmin[0]].tolist()
        #    xval = geo_list[indmin[0],[0]].tolist()
        #    dtval.append(datetime[0])
        #    dlist = []
        #    xcgcode = []
        #
        #dtval = np.array(dtval)
        #unique_dtval = np.unique(dtval, axis=0)
        
        gmap_plot(lat_list_train + lat_list, long_list_train + long_list)
                
        #///// Plot Confusion Matrix /////////////
        
        #YTrue = np.concatenate((X_true_test, X_true_outliers), axis=0)
        #YPred = np.concatenate((y_pred_test, y_pred_outliers), axis=0)
        #
        #conf_mat = confusion_matrix(YTrue, YPred)
        ## Plot non-normalized confusion matrix
        #plt.figure()
        #plot_confusion_matrix(conf_mat, classes= ['Normal', 'Anomaly'],
        #                      title='Confusion matrix')