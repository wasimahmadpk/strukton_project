# -*- coding: utf-8 -*-
"""
Created on Thu Feb 01 13:21:46 2018

@author: Waseem
"""

import os
import csv
import numpy as np
import pandas as pd
from string import ascii_letters
from gmapplot import gmap_plot
import matplotlib.pyplot as plt
from data_paths import data_paths
from normalization import normalize
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

    def anomaly_detection(self, pprocessed_file, features='RMS', sliding_window=1000, sub_sampling=128, impurity=0.05, num_trees=100):

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
            ext_count = np.array(processed_data.EXTCNT)
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

            if len(push_ext_count) == 0:
                push_ext_count = pull_ext_count

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
            if len(push_data) != 0:
                data_list.append(push_data)
            counters_list.append(pull_int_count)
            counters_list.append(push_int_count)
            xcounters_list.append(pull_ext_count)
            if len(push_ext_count) != 0:
                xcounters_list.append(push_ext_count)
            ########################################
            data_list2 = []
            data_list2.append(pull_data2)
            if len(push_data2) != 0:
                data_list2.append(push_data2)
            rail_data.append(data_list)
            rail_data.append(data_list2)
            rail_counters.append(counters_list)
            rail_counters.append(counters_list)
            rail_xcounters.append(xcounters_list)
            rail_xcounters.append(xcounters_list)
            ########################################

            get_xcount = interp1d(int_count, ext_count, fill_value='extrapolate')
            get_icount = interp1d(ext_count, int_count, fill_value='extrapolate')

            # ///////////// Extract Train Speed /////////////
            # ze = Zedf(rp.run.paths['default'].parent.joinpath('ZOES'), rp.run.name)
            # vel = int(ze.ze_get(np.mean([data.loc[k]['CNT_BGN'], data.loc[k]['CNT_END']]), 'velocity') * 3.6)

            # ///////////// Feature Extraction //////////////
            aba_data_side = []
            all_xcount_mode = []
            anom_xcount_mode = []
            anom_score_mode = []

            for i in range(2):
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
                    list_of_features = extract_features(in_data, counters, sliding_window)

                    rms = np.array(list_of_features[:, 0])
                    kurtosis = np.array(list_of_features[:, 2])
                    skewness = np.array(list_of_features[:, 3])
                    peak_to_peak = np.array(list_of_features[:, 4])
                    crest_factor = np.array(list_of_features[:, 5])
                    impulse_factor = np.array(list_of_features[:, 6])
                    rmsf = np.array(list_of_features[:, 12])
                    int_count = np.array(list_of_features[:, 13])

                    # # features comparison
                    # plt.figure(2)
                    # plt.subplot(211)
                    # plt.ylabel('ABA')
                    # plt.plot(list(range(0, 401000)), in_data[:401000])
                    # # plt.subplot(212)
                    # # plt.ylabel('RMS')
                    # # plt.plot(list(range(1000, 401000, 2000)), rms[:200], '*')
                    # # plt.subplot(413)
                    # # plt.ylabel('Kurtosis')
                    # # plt.plot(list(range(1000, 401000, 2000)), kurtosis[:200], '*')
                    # plt.subplot(212)
                    # plt.ylabel('Peak to peak')
                    # plt.xlabel('Data Samples')
                    # plt.plot(list(range(1000, 401000, 2000)), peak_to_peak[:200], '*')
                    # plt.show()

                    # plt.figure(2)
                    # plt.subplot(211)
                    # plt.ylabel('ABA')
                    # plt.plot(list(range(390000, 400000)), in_data[390000:400000])
                    # plt.subplot(212)
                    # plt.ylabel('RMS')
                    # plt.xlabel('Samples')
                    # plt.plot(list(range(391000, 401000, 2000)), rms[195:200], 'r*')
                    # plt.xlim(390000, 400000)
                    # plt.show()

                    if features=='RMS':
                        mylist = np.stack((rms, rms), axis=-1)
                    if features == 'Kurtosis':
                        mylist = np.stack((kurtosis, kurtosis), axis=-1)
                    if features == 'Crest factor':
                        mylist = np.stack((crest_factor, crest_factor), axis=-1)
                    if features == 'Impulse factor':
                        mylist = np.stack((impulse_factor, impulse_factor), axis=-1)
                    if features == 'Skewness':
                        mylist = np.stack((skewness, skewness), axis=-1)
                    if features == 'Peak-to-peak':
                        mylist = np.stack((peak_to_peak, peak_to_peak), axis=-1)
                    if features == 'All':
                        mylist = np.stack((rms, kurtosis, peak_to_peak, crest_factor, impulse_factor, skewness), axis=-1)


                    norm_train, anom_train, norm_test, anom_test, anom_icount, anom_icount_train, anom_score = isolation_forest(
                        mylist, int_count, sub_sampling, impurity, num_trees)

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
                        # distance = geodesic(point_one, point_two).km
                        # dist.append(1000 * distance)
                        dist.append(longitude[z])

                    anom_xcount = [str(x) for x in anom_xcount]
                    latitude = [str(x) for x in latitude]
                    longitude = [str(x) for x in longitude]
                    dist = [str(x) for x in dist]

                    write_data = zip(anom_xcount, latitude, longitude, dist)
                    track_side = 'chb' if i else 'cha'
                    train_mode = 'pushing' if j else 'pulling'

                    with open(self.counters_path + '\Prorail17112805si12_' + track_side + '_' + train_mode + '.csv', 'w',
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

                    gmap_plot(lat_list_train + lat_list, long_list_train + long_list)

                aba_data_side.append(aba_data_mode)
                anom_xcount_mode.append(anom_xcount_list)
                anom_score_mode.append(anom_score_list)

            # function call: compare anomalies in ABA on both channels i.e. CHA and CHB and return anomaly_positions
            anomaly_positions = match_anomaly(rail_data, rail_xcounters, anom_xcount_mode, self.seg_file)
            # ///////////////////////////////////////////

            if len(anomaly_positions) > 2:
                anom_pos_cha = np.round(anomaly_positions[0] + anomaly_positions[2], 2)
                anom_xcount_cha = np.round(np.concatenate((anom_xcount_mode[0][0], anom_xcount_mode[0][1]), axis=0), 2)
                anom_score_cha = np.round(np.concatenate((anom_score_mode[0][0], anom_score_mode[0][1]), axis=0), 3)
            else:
                anom_pos_cha = np.round(anomaly_positions[0], 2)
                anom_xcount_cha = np.round(anom_xcount_mode[0][0], 2)
                anom_score_cha = np.round(anom_score_mode[0][0], 3)

            anom_pos_xcount = np.stack((anom_pos_cha, anom_xcount_cha, anom_score_cha), axis=-1)
            anom_pos_xcount_sorted = anom_pos_xcount[anom_pos_xcount[:, 0].argsort()]
            anom_pos_cha = list(anom_pos_xcount_sorted[:, 0])
            anom_xcount_cha = list(anom_pos_xcount_sorted[:, 1])
            anom_score_cha = list(anom_pos_xcount_sorted[:, 2])

            # # Data-frame for severity analysis

            # dict = {'position': anom_pos_cha, 'counters': anom_xcount_cha, 'score': anom_score_cha}
            # df_anom_pos_score = pd.DataFrame(data=dict)
            # ectpath = r'D:\strukton_project\WP_180306\ECT\EC_data_2018_FC_FO_LR.csv'
            # headchecks = DefectSeverity(df_anom_pos_score, ectpath).get_trend()
            #
            # plotlist = []
            # depth = normalize(headchecks['depth'].tolist())
            # score = headchecks['score'].tolist()
            # plotlist.append(depth)
            # plotlist.append(score)
            # pltlist = [[plotlist[j][i] for j in range(len(plotlist))] for i in range(len(plotlist[0]))]
            # pltarr = np.array(pltlist)
            # sorted = pltarr[pltarr[:, 0].argsort()]
            # cracksize = sorted[:, 0]
            # anomscore = sorted[:, 1]
            #
            # write_data = zip(cracksize, anomscore)
            # track_side = 'cha_crack_anom'
            #
            # with open(self.counters_path + '\Prorail18030614si12_' + track_side + '.csv', 'w',
            #           newline='') as file:
            #     try:
            #         writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            #         writer.writerow(['crack_depth', 'anom_severity'])
            #         for crack, sev in write_data:
            #             writer.writerow([crack, sev])
            #     finally:
            #         file.close()
            #
            # ##################################

            write_data = zip(anom_pos_cha, anom_xcount_cha, anom_score_cha)
        return anom_pos_xcount_sorted

    def save_output(self, write_data, fname):

        track_side = 'cha_km'
        with open(fname + '.csv', 'w', newline='') as file:
        # with open(self.counters_path + '\Prorail17112805si12_' + track_side + '.csv', 'w',
        #           newline='') as file:
            try:
                writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(['positions', 'counters', 'severity'])
                for pos, cnt, sev in write_data:
                    writer.writerow([pos, cnt, sev])
            finally:
                file.close()


if __name__ == "__main__":

    obj = RailDefects(1)
    model_outcome = obj.anomaly_detection(pprocessed_file=data_paths.data_path[4])

    # # plotting crack depth vs anomaly score
    # plotlist = []
    # plt.figure(15)
    # plt.title('Severity Analysis')
    # plt.xlabel('No. of anomalies')
    # plt.ylabel('Anomaly score and Crack depth')
    # plt.ylim(0, 2)
    # depth = normalize(headchecks['depth'].tolist())
    # score = headchecks['score'].tolist()
    # plotlist.append(depth)
    # plotlist.append(score)
    # pltlist = [[plotlist[j][i] for j in range(len(plotlist))] for i in range(len(plotlist[0]))]
    # pltarr = np.array(pltlist)
    # sorted = pltarr[pltarr[:, 1].argsort()]
    #
    # depthlab, = plt.plot(sorted[:, 0], label='crack depth')
    # severity, = plt.plot(sorted[:, 1], label='anomaly score')
    # plt.legend(loc='upper left', handles=[depthlab, severity])
