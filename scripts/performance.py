# -*- coding: utf-8 -*-
"""
Created on Thu Jan  3 14:09:57 2019

@author: Waseem
"""
import xml.etree.ElementTree as ET
import numpy as np
import glob
import csv
import os

print('Calculating Model\'s Performance')

lab_list = []
tree_list = []
file_names = []
obj_dim = []
hit_rate, false_alarms, false_negatives = 0, 0, 0
for filename in glob.glob(
                          r'D:\strukton_project\Groningen\Prorail17112805si12\ABA\Prorail17112805si12\xml\61\*.xml'):
    fname = os.path.basename(filename)
    print(fname)
    file_names.append(fname)
    tree = ET.parse(filename)
    tree_list.append(tree)

    file, ext = os.path.splitext(fname)
    fname = list(file)
    label_signum = int(fname[3] + fname[4] + fname[5])
    lab_list.append(label_signum)

counters_pull = []
counters_push = []

with open(
        'D:\strukton_project\Groningen\Prorail17112805si12\ABA\Prorail17112805si12\counter_data\prorail17112805si12_cha_pushing.csv') as csv_file:
    csv_reader = csv.reader(csv_file)
    line_count = 0
    for row in csv_reader:
        tempStr = ''.join(row)
        if tempStr.startswith('#') or len(tempStr) == 0:
            continue
        elif tempStr.startswith('counters'):
            print(f'Column names are {", ".join(row)}')
            line_count += 1
        else:
            line_count += 1
            tlist = tempStr.split(",")
            counters_push.append(float(row[0]))
    print(f'Processed {line_count} lines in push-counters file.')
    print("Program is running...")

# with open(
#         'D:\strukton_project\Groningen\Prorail17112805si12\ABA\Prorail17112805si12\counter_data\prorail17112805si12_cha_pulling.csv') as csv_file:
#     csv_reader = csv.reader(csv_file)
#     line_count = 0
#     for row in csv_reader:
#         tempStr = ''.join(row)
#         if tempStr.startswith('#') or len(tempStr) == 0:
#             continue
#         elif tempStr.startswith('counters'):
#             print(f'Column names are {", ".join(row)}')
#             line_count += 1
#         else:
#             # print(f'\t{row[0]} works in the {row[1]} department, and was born in {row[2]}.')
#             line_count += 1
#             tlist = tempStr.split(",")
#             counters_pull.append(float(row[0]))
#     print(f'Processed {line_count} lines in pull-counters file.')

all_counters = np.array(counters_push + counters_pull)
next_spots = []
prev_spots = []
all_spots = []
all_defects_spots = []
defect_track = []
anom_track = []
anomalies = 0

# for y in range(len(all_counters)):
#     num = all_counters[y]
#     tnum = list(str(int(num)))
#     cnt_signum = int(tnum[0] + tnum[1] + tnum[2])
#     if any(np.array(cnt_signum) == np.array(lab_list)):
#         continue
#     elif any(np.array(cnt_signum) == np.array(lab_list)):
#         continue
#     else:
#         false_alarms = false_alarms + 1


for i in range(len(tree_list)):

    root = tree_list[i]
    defect_spots = []
    # all items data
    print('Defect Data:')

    for obj in root.findall('object/bndbox'):

        xmin = obj.find('xmin').text
        xmax = obj.find('xmax').text
        xdim = (int(xmin) + int(xmax)) / 2
        print(xmin, xdim, xmax)
        defect_spots.append(xdim)
        all_defects_spots.append(xdim)

    defect_track.append(defect_spots)
    itlist1 = []
    itlist2 = []

    file, ext = os.path.splitext(file_names[i])
    fname = list(file)
    label_signum = int(fname[3] + fname[4] + fname[5])
    itlist1.append(label_signum)
    anom_spots = []
    anom_spots = anom_spots + next_spots
    # anom_spots = anom_spots + prev_spots
    next_spots = []

    for j in range(len(all_counters)):
        num = all_counters[j]
        tnum = list(str(int(num)))
        cnt_signum = int(tnum[0] + tnum[1] + tnum[2])
        itlist2.append(cnt_signum)

        if j < len(counters_push):
            anom_num = int(tnum[3] + tnum[4]+tnum[5] + tnum[6])*4 + 3150*4   # plus
        else:
            anom_num = int(tnum[3] + tnum[4]+tnum[5] + tnum[6])*4 - 3150*4   # minus

        if label_signum == cnt_signum & cnt_signum < 634:
            anomalies = anomalies + 1
            if anom_num >= 40000:
                next_spots.append(abs(40000 - anom_num))
            elif anom_num < 0:
                prev_spots.append(40000 + anom_num)
            else:
                anom_spots.append(anom_num)
                all_spots.append(anom_num)

    anom_track.append(anom_spots)
    if i > 1:
        a_spots = anom_track[i-1] + prev_spots
        d_spots = defect_track[i-1]
        prev_spots = []
    else:
        a_spots = anom_track[i] + prev_spots
        d_spots = defect_track[i]

    # compare anomalies
    hit_container = []
    for s in range(len(a_spots)):
        for w in range(len(d_spots)):
            hit_container.append(abs(a_spots[s] - d_spots[w]))
        if any(np.array(hit_container) < 5000):
            continue
        else:
            false_alarms = false_alarms + 1

    # compare actual defects
    hit_container = []
    for s in range(len(d_spots)):
        for w in range(len(a_spots)):
            hit_container.append(abs(a_spots[w] - d_spots[s]))
        if any(np.array(hit_container) < 5000):
            hit_rate = hit_rate + 1
        else:
            false_negatives = false_negatives + 1

# Model performance in terms of hit rate, false alarms and miss rate
print('Anomalies: {}, Hits: {}, False Alarms: {}, Misses: {}'.format(hit_rate+false_alarms, hit_rate, false_alarms,                                                                           false_negatives))
print('All defects: ', len(all_defects_spots))