# -*- coding: utf-8 -*-
"""
Created on Thu Feb 01 13:21:46 2018

@author: Waseem
"""

import os
import csv
import numpy as np
import pandas as pd
import seaborn as sns
from string import ascii_letters
from gmapplot import gmap_plot
import matplotlib.pyplot as plt
from data_paths import data_paths
from geopy.distance import geodesic
from scipy.interpolate import interp1d
from compare_anomaly import match_anomaly
from data_processing import pre_processing
from severity_analysis import DefectSeverity
from extract_features import extract_features
from anomaly_detection import isolation_forest


class RailDefects:

    def __init__(self, flag):
        self.flag = flag
        fpaths = data_paths()
        self.data_file = fpaths.data_path[0]
        self.sync_file = fpaths.data_path[1]
        self.seg_file = fpaths.data_path[2]
        self.poi_file = fpaths.data_path[3]
        self.processed_file = fpaths.data_path[4]
        self.counters_path = fpaths.data_path[5]

    def anomaly_detection(self, pprocessed_file):

        self.processed_file = pprocessed_file
        if not os.path.isfile(self.processed_file):
            pre_processing(self.data_file, self.sync_file, self.seg_file, self.poi_file, self.processed_file)
        else:
            geo_list = []
            with open(self.poi_file) as csv_file:
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
                        line_count += 1
                        tlist = tempStr.split(";")
                        ttlist = [float(x) for x in tlist if len(x) > 0]
                        geo_list.append(ttlist)
                print(f'Processed {line_count} lines in POI file.')
                geo_list = np.array(geo_list)

            lat = geo_list[:, 1]
            lon = geo_list[:, 2]

            # Interpolation external and geo-coordinates
            get_lat = interp1d(geo_list[:, 0], lat, fill_value='extrapolate')
            get_long = interp1d(geo_list[:, 0], lon, fill_value='extrapolate')

            processed_data = pd.read_hdf(self.processed_file, 'processed', mode='r')

            # CHC1 = np.array(processed_data.CHC1)
            # CHC3 = np.array(processed_data.CHC3)
            # CHD1 = np.array(processed_data.CHD1)
            # CHD3 = np.array(processed_data.CHD3)
            EDIR = np.array(processed_data.ERS_DIR)
            CHA1 = np.array(processed_data.CHA1)
            CHA3 = np.array(processed_data.CHA3)
            CHB1 = np.array(processed_data.CHB1)
            CHB3 = np.array(processed_data.CHB3)

            int_count = np.array(processed_data.INTCNT)
            ext_count = np.array(processed_data.ExtCnt)
            # date_time = syncdat.DateTime

            # Pushing & Pulling ABA data for one side (left or right)
            pull_data_cha1 = CHA1[(EDIR == 1)]
            push_data_cha1 = CHA1[(EDIR == -1)]
            pull_data_cha3 = CHA3[(EDIR == 1)]
            push_data_cha3 = CHA3[(EDIR == -1)]

            pull_int_count = int_count[(EDIR == 1)]
            push_int_count = int_count[(EDIR == -1)]

            pull_ext_count = ext_count[(EDIR == 1)]
            push_ext_count = ext_count[(EDIR == -1)]

            pull_data = np.power((np.power(pull_data_cha1, 2) + np.power(pull_data_cha3, 2)), 1 / 2)
            push_data = np.power((np.power(push_data_cha1, 2) + np.power(push_data_cha3, 2)), 1 / 2)

            cha_data = np.power((np.power(CHA1, 2) + np.power(CHA3, 2)), 1 / 2)

            # Second side
            pull_data_chb1 = CHB1[(EDIR == 1)]
            push_data_chb1 = CHB1[(EDIR == -1)]
            pull_data_chb3 = CHB3[(EDIR == 1)]
            push_data_chb3 = CHB3[(EDIR == -1)]

            pull_data2 = np.power((np.power(pull_data_chb1, 2) + np.power(pull_data_chb3, 2)), 1 / 2)
            push_data2 = np.power((np.power(push_data_chb1, 2) + np.power(push_data_chb3, 2)), 1 / 2)
            ########################################
            rail_data = []
            rail_counters = []
            rail_xcounters = []
            data_list = []
            counters_list = []
            xcounters_list = []
            data_list.append(pull_data)
            data_list.append(push_data)
            counters_list.append(pull_int_count)
            counters_list.append(push_int_count)
            xcounters_list.append(pull_ext_count)
            xcounters_list.append(push_ext_count)
            ########################################
            data_list2 = []
            data_list2.append(pull_data2)
            data_list2.append(push_data2)
            rail_data.append(data_list)
            rail_data.append(data_list2)
            rail_counters.append(counters_list)
            rail_counters.append(counters_list)
            rail_xcounters.append(xcounters_list)
            rail_xcounters.append(xcounters_list)
            ########################################

            anom_xcount_list = []
            anom_score_list = []
            anom_xcount_train_list = []

            get_xcount = interp1d(int_count, ext_count, fill_value='extrapolate')
            get_icount = interp1d(ext_count, int_count, fill_value='extrapolate')

            # ///////////// Feature Extraction //////////////
            aba_data_side = []
            all_xcount_mode = []
            anom_xcount_mode = []
            anom_score_mode = []

            for i in range(len(rail_data)):
                aba_data_mode = []
                int_count_mode = []
                anom_xcount_list = []
                anom_score_list = []
                input_data = rail_data[i]

                for j in range(len(data_list)):
                    in_data = input_data[j]
                    if len(in_data) == 0:
                        continue
                    counters = counters_list[j]
                    list_of_features = extract_features(in_data, counters, 3000)

                    rms = np.array(list_of_features[:, 0])
                    kurtosis = np.array(list_of_features[:, 2])
                    skewness = np.array(list_of_features[:, 3])
                    peak_to_peak = np.array(list_of_features[:, 4])
                    crest_factor = np.array(list_of_features[:, 5])
                    impulse_factor = np.array(list_of_features[:, 6])
                    rmsf = np.array(list_of_features[:, 12])
                    int_count = np.array(list_of_features[:, 13])

                    # features comparison
                    plt.figure(2)
                    plt.subplot(311)
                    plt.ylabel('RMS')
                    plt.xlabel('Time')
                    plt.plot(rms)
                    plt.subplot(312)
                    plt.ylabel('Kurtosis')
                    plt.xlabel('Time')
                    plt.plot(kurtosis)
                    plt.subplot(313)
                    plt.ylabel('Peak to peak')
                    plt.xlabel('Time')
                    plt.plot(peak_to_peak)
                    plt.show()

                    mylist = np.stack((peak_to_peak, peak_to_peak), axis=-1)
                    norm_train, anom_train, norm_test, anom_test, anom_icount, anom_icount_train, anom_score = isolation_forest(
                        mylist, int_count)

                    # norm_train = np.concatenate(norm_train.tolist())
                    # anom_train = np.concatenate(anom_train.tolist())
                    # norm_test = np.concatenate(norm_test.tolist())
                    # anom_test = np.concatenate(anom_test.tolist())

                    all_xcount_mode.append(get_xcount(int_count))
                    anom_xcount_test = get_xcount(anom_icount)
                    anom_xcount_train = get_xcount(anom_icount_train)
                    anom_xcount = np.concatenate((anom_xcount_train, anom_xcount_test), axis=0)
                    anom_score = anom_score

                    anom_xcount_list.append(anom_xcount)
                    anom_score_list.append(anom_score)

                    # new code for validation of anomalies
                    latitude = get_lat(anom_xcount)
                    longitude = get_long(anom_xcount)
                    dist = [0]

                    for z in range(len(latitude) - 1):
                        point_one = (latitude[z], longitude[z])
                        point_two = (latitude[z + 1], longitude[z + 1])
                        distance = geodesic(point_one, point_two).km
                        dist.append(1000 * distance)

                    anom_xcount = [str(x) for x in anom_xcount]
                    latitude = [str(x) for x in latitude]
                    longitude = [str(x) for x in longitude]
                    dist = [str(x) for x in dist]

                    write_data = zip(anom_xcount, latitude, longitude, dist)
                    track_side = 'chb' if i else 'cha'
                    train_mode = 'pushing' if j else 'pulling'

                    with open(self.counters_path + '\Prorail18022101si12_' + track_side + '_' + train_mode + '.csv', 'w',
                              newline='') as file:
                        try:
                            writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                            writer.writerow(['counters', 'latitude', 'longitude', 'distance'])
                            for cnt, lat, lon, dist in write_data:
                                writer.writerow([cnt, lat, lon, dist])
                        finally:
                            file.close()
                    #######################################################

                    lat_list = get_lat(anom_xcount).tolist()
                    long_list = get_long(anom_xcount).tolist()
                    lat_list_train = get_lat(anom_xcount_train).tolist()
                    long_list_train = get_long(anom_xcount_train).tolist()

                    #    dlist = []
                    #    xcgcode = []

                    # geocodes_train = np.array(geocode)
                    # unique_gcodes_train = np.unique(geocodes_train, axis = 0)
                    # lat_list_train = unique_gcodes_train[:, 1].tolist()
                    # long_list_train = unique_gcodes_train[:, 2].tolist()

                    # lat_list_train = [float(i) for i in lat_list_train]
                    # long_list_train = [float(j) for j in lon_list_train]

                    # Calculation of time of data acquisition

                    # geo_xcount = geo_list[:,0]
                    # geo_icount = get_icount(geo_xcount)
                    # geo_icount[np.isnan(geo_icount)] = 0

                    # dlist = []
                    # dtval = []

                    # for j in range(len(geo_icount)):
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
                    # dtval = np.array(dtval)
                    # unique_dtval = np.unique(dtval, axis=0)

                    gmap_plot(lat_list_train + lat_list, long_list_train + long_list)

                    # ///// Plot Confusion Matrix /////////////

                    # YTrue = np.concatenate((X_true_test, X_true_outliers), axis=0)
                    # YPred = np.concatenate((y_pred_test, y_pred_outliers), axis=0)

                    # conf_mat = confusion_matrix(YTrue, YPred)
                    # Plot non-normalized confusion matrix
                    # plt.figure()
                    # plot_confusion_matrix(conf_mat, classes= ['Normal', 'Anomaly'],
                    #                      title='Confusion matrix')
                aba_data_side.append(aba_data_mode)
                anom_xcount_mode.append(anom_xcount_list)
                anom_score_mode.append(anom_score_list)

            # function call: compare anomalies in ABA on both channels i.e. CHA and CHB
            anomaly_positions = match_anomaly(rail_data, rail_xcounters, anom_xcount_mode, self.seg_file)
            # return anomaly_positions
            anom_pos_cha = np.array(anomaly_positions[0] + anomaly_positions[2])
            anom_xcount_cha = np.concatenate((anom_xcount_mode[0][0], anom_xcount_mode[0][1]), axis=0)
            anom_score_cha = np.concatenate((anom_score_mode[0][0], anom_score_mode[0][1]), axis=0)
            anom_pos_xcount = np.stack((anom_pos_cha, anom_xcount_cha, anom_score_cha), axis=-1)
            anom_pos_xcount_sorted = anom_pos_xcount[anom_pos_xcount[:, 0].argsort()]
            anom_pos_cha = list(anom_pos_xcount_sorted[:, 0])
            anom_xcount_cha = list(anom_pos_xcount_sorted[:, 1])
            anom_score_cha = list(anom_pos_xcount_sorted[:, 2])

            # Data-frame for severity analysis

            dict = {'position': anom_pos_cha, 'counters': anom_xcount_cha, 'score': anom_score_cha}
            df_anom_pos_score = pd.DataFrame(data=dict)
            ectpath = r'F:\strukton_project\Flevolijn\ECT\EC_data_2018_FC_FO_L.csv'
            headchecks = DefectSeverity(df_anom_pos_score, ectpath).get_trend()
            return headchecks

            ##################################

            write_data = zip(anom_pos_cha, anom_xcount_cha, anom_score_cha)
            track_side = 'cha_km'

            with open(self.counters_path + '\Prorail18022101si12_' + track_side + '.csv', 'w',
                      newline='') as file:
                try:
                    writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    writer.writerow(['positions', 'counters', 'severity'])
                    for pos, cnt, sev in write_data:
                        writer.writerow([pos, cnt, sev])
                finally:
                    file.close()


if __name__ == "__main__":
    obj = RailDefects(1)
    headchecks = obj.anomaly_detection(pprocessed_file=data_paths.data_path[4])
    plotlist = []
    plt.figure(15)
    plt.title('Severity Analysis')
    plt.xlabel('No. of anomalies')
    plt.ylabel('anomaly score and crack depth')
    plt.ylim(0, 2)
    depth = headchecks['depth'].tolist()
    score = headchecks['score'].tolist()
    plotlist.append(depth)
    plotlist.append(score)
    pltlist = [[plotlist[j][i] for j in range(len(plotlist))] for i in range(len(plotlist[0]))]
    pltarr = np.array(pltlist)
    sorted = pltarr[pltarr[:, 1].argsort()]
    depth = sorted[:, 0]
    score = sorted[:, 1]

    depthlab, = plt.plot(depth, label='crack depth (mm)')
    severity, = plt.plot(score, label='anomaly score (0~1)')
    plt.legend(loc='upper left', handles=[depthlab, severity])

    pltlist_trans = rez = [[plotlist[j][i] for j in range(len(plotlist))] for i in range(len(plotlist[0]))]
    df = pd.DataFrame(data=pltlist_trans,
                      columns=['depth', 'score'])

    # Compute the correlation matrix
    corr = df.corr()

    # Generate a mask for the upper triangle
    mask = np.zeros_like(corr, dtype=np.bool)
    mask[np.triu_indices_from(mask)] = True

    # Set up the matplotlib figure
    f, ax = plt.subplots(figsize=(11, 9))

    # Generate a custom diverging colormap
    cmap = sns.diverging_palette(220, 10, as_cmap=True)

    # Draw the heatmap with the mask and correct aspect ratio
    sns.heatmap(corr, mask=mask, cmap=cmap, vmax=.3, center=0,
                square=True, linewidths=.5, cbar_kws={"shrink": .5})
