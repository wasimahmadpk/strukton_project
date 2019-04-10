import csv
import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d


def match_anomaly(abadata, allxcount, anomxcount, segfile):

    print('I am inside compare_anomaly function')

    # read CSV file
    route_list = []
    with open(segfile) as csv_file:
        csv_reader = csv.reader(csv_file)
        line_count = 0
        for row in csv_reader:
            tempStr = ''.join(row)
            if tempStr.startswith('#') or len(tempStr) == 0:
                continue
            elif tempStr.startswith('PRV10_CNT_BGN'):
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                # print(f'\t{row[0]} works in the {row[1]} department, and was born in {row[2]}.')
                line_count += 1
                tlist = tempStr.split(";")
                route_list.append(tlist)
        print(f'Processed {line_count} lines in SEG file.')
        route_list = np.array(route_list)

    winsize = 10000
    anomaly_positions = []
    all_km_positions_cha = []
    all_km_positions_chb = []
    for i in range(len(abadata)-1):
        cha_aba = abadata[i]
        chb_aba = abadata[i+1]
        ch_xcount = allxcount[i]
        cha_axcount = anomxcount[i]
        chb_axcount = anomxcount[i+1]

        for j in range(len(cha_aba)):
            start_idx = 0
            cha_dir_aba = cha_aba[j]
            chb_dir_aba = chb_aba[j]
            dir_xcount = ch_xcount[j]
            cha_dir_axcount = cha_axcount[j]
            chb_dir_axcount = chb_axcount[j]
            numwindows = math.floor(len(dir_xcount)/winsize)
            numwinb = round(len(dir_xcount)/10000)

            anom_pos_listA = []
            anom_pos_listB = []

            for k in range(len(cha_dir_axcount)):
                axcount = int(cha_dir_axcount[k])
                pos_list = []
                count_list = []

                for z in range(len(route_list)):
                    if(axcount >= int(route_list[z, 0]) and axcount <= int(route_list[z, 1])):
                        pos_start, pos_end = float(route_list[z, 7])*1000, float(route_list[z, 8])*1000
                        count_start, count_end = int(route_list[z, 0]), int(route_list[z, 1])
                        pos_list.append(pos_start)
                        pos_list.append(pos_end)
                        count_list.append(count_start)
                        count_list.append(count_end)

                        get_position = interp1d(count_list, pos_list, fill_value='extrapolate')
                        anom_pos = get_position(axcount)/1000
                        anom_pos_listA.append(anom_pos)
                        break
                    else:
                        continue

            for k in range(len(chb_dir_axcount)):
                axcount = int(chb_dir_axcount[k])
                pos_list = []
                count_list = []

                for z in range(len(route_list)):
                    if (axcount >= int(route_list[z, 0]) and axcount <= int(route_list[z, 1])):
                        pos_start, pos_end = float(route_list[z, 7])*1000, float(route_list[z, 8])*1000
                        count_start, count_end = int(route_list[z, 0]), int(route_list[z, 1])
                        pos_list.append(pos_start)
                        pos_list.append(pos_end)
                        count_list.append(count_start)
                        count_list.append(count_end)

                        get_position = interp1d(count_list, pos_list, fill_value='extrapolate')
                        anom_pos = get_position(axcount)/1000
                        anom_pos_listB.append(anom_pos)
                        break
                    else:
                        continue

            for a in range(numwindows):
                winanoma = []
                winanomb = []
                print(a, j)
                counters = dir_xcount[start_idx: start_idx + winsize]
                data_cha = cha_dir_aba[start_idx: start_idx + winsize]
                data_chb = chb_dir_aba[start_idx: start_idx + winsize]
                start_idx = start_idx + winsize

                for b in range(len(cha_dir_axcount)):
                    axcount = int(cha_dir_axcount[b])
                    if (axcount >= counters[0]) and (axcount <= counters[-1]):
                        winanoma.append(round(axcount))
                        km_position = round(anom_pos_listA[b], 3)
                    else:
                        continue

                for c in range(len(chb_dir_axcount)):
                    axcount = int(chb_dir_axcount[c])
                    if (axcount >= counters[0]) and (axcount <= counters[-1]):
                        winanomb.append(round(axcount))
                        km_position = round(anom_pos_listB[c], 3)
                    else:
                        continue

                if len(winanoma) > 0 or len(winanomb) > 0:
                    print('Inside plotting' + '_' + str(j))
                    mode = 'pushing' if j else 'pulling'
                    fname = str(counters[0]) + '_' + str(km_position) + ' km' + '_' + mode
                    plt.figure(6)
                    plt.subplot(211)
                    plt.title(fname)
                    plt.ylabel('Channel A')
                    plt.plot(counters, data_cha)
                    for xc in winanoma:
                        plt.axvline(x=xc, color='r', linestyle='--')
                    plt.subplot(212)
                    plt.ylabel('Channel B')
                    plt.plot(counters, data_chb)
                    for xc in winanomb:
                        plt.axvline(x=xc, color='r', linestyle='--')
                    plt.savefig(r'F:\strukton_project\Flevolijn\Prorail18022101si12\ABA\Prorail18022101si12\channel_comparison\{}.png'.format(fname))
                    plt.clf()

            anomaly_positions.append(anom_pos_listA)
            anomaly_positions.append(anom_pos_listB)

    return anomaly_positions

