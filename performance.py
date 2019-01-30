# -*- coding: utf-8 -*-
"""
Created on Thu Jan  3 14:09:57 2019

@author: Waseem
"""
from PIL import Image
import xml.etree.ElementTree as ET
import numpy as np
import glob
import csv
import os

#def get_perform():

print('Calculating Model\'s Performance')

tree_list = []
file_names = []
obj_dim = []
hit_rate, false_alarms, false_negatives = 0, 0, 0
for filename in glob.glob(
        r'F:\strukton_project\Groningen\Prorail17112805si12\ABA\Prorail17112805si12\xml\61\*.xml'):
    fname = os.path.basename(filename)
    print(fname)
    file_names.append(fname)
    tree = ET.parse(filename)
    # im = im.rotate(90)
    tree_list.append(tree)

counters_pull = []
counters_push = []

with open(
        'F:\strukton_project\Groningen\Prorail17112805si12\ABA\Prorail17112805si12\counter_data\prorail17112805si12_right_pushing.csv') as csv_file:
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
            # print(f'\t{row[0]} works in the {row[1]} department, and was born in {row[2]}.')
            line_count += 1
            tlist = tempStr.split(",")
            counters_push.append(float(row[0]))
    print(f'Processed {line_count} lines in push-counters file.')
    print("Program is running...")
    counters_push = np.array(counters_push)

with open(
        'F:\strukton_project\Groningen\Prorail17112805si12\ABA\Prorail17112805si12\counter_data\prorail17112805si12_right_pulling.csv') as csv_file:
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
            # print(f'\t{row[0]} works in the {row[1]} department, and was born in {row[2]}.')
            line_count += 1
            tlist = tempStr.split(",")
            counters_pull.append(float(row[0]))
    print(f'Processed {line_count} lines in pull-counters file.')
    print("Program is running...")
    counters_pull = np.array(counters_pull)

next_spots = []
prev_spots = []
all_spots = []
all_defects_spots = []
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
    prev_spots = []
    for j in range(len(counters_push) - 1):
        num = counters_push[j]
        tnum = list(str(int(num)))
        cnt_signum = int(tnum[0] + tnum[1] + tnum[2])
        itlist2.append(cnt_signum)
        anom_num = int(tnum[3] + tnum[4] + tnum[5] + tnum[6])*4 + 3150*4
        if label_signum == cnt_signum:
            if anom_num >= 40000:
                next_spots.append(abs(40000 - anom_num))
                prev_spots.append(40000 + anom_num)
            else:
                anom_spots.append(anom_num)
                all_spots.append(anom_num)
    # compare anomalies
    hit_container = []
    for s in range(len(anom_spots)):
        for w in range(len(defect_spots)):
            hit_container.append(abs(anom_spots[s] - defect_spots[w]))
        if any(hit_container) < 4000:
            hit_rate = hit_rate + 1
        else:
            false_alarms = false_alarms + 1
    # compare actual defects
    hit_container = []
    for s in range(len(defect_spots)):
        for w in range(len(anom_spots)):
            hit_container.append(abs(anom_spots[w] - defect_spots[s]))
        if any(hit_container) < 4000:
            continue
        else:
            false_negatives = false_negatives + 1


    # Comparison of actual defects vs detected anomalies
print('Hits: {} , False Alarms: {}, False Negatives: {}'.format(hit_rate, false_alarms, false_negatives))
