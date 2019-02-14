# -*- coding: utf-8 -*-
"""
Created on Thu Jan  3 14:09:57 2019

@author: Waseem
"""

from PIL import Image
import numpy as np
import glob
import csv
import os


image_list = []
file_names = []

for filename in glob.glob(r'F:\strukton_project\Groningen\Prorail17112805si12\ABA\Prorail17112805si12\images\Prorail17112805\Prorail17112805\61\*.jpg'):
    file_name = os.path.basename(filename)
    print(file_name)
    file_names.append(file_name)
    im = Image.open(filename)
    # im = im.rotate(90)
    image_list.append(im)

counters_pull = []
counters_push = []

with open('F:\strukton_project\Groningen\Prorail17112805si12\ABA\Prorail17112805si12\counter_data\prorail17112805si12_left_pushing.csv') as csv_file:
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


with open('F:\strukton_project\Groningen\Prorail17112805si12\ABA\Prorail17112805si12\counter_data\prorail17112805si12_left_pulling.csv') as csv_file:
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
                counters_pull.append(float(row[0]))
        print(f'Processed {line_count} lines in pull-counters file.')
        print("Program is running...")

all_counters = np.array(counters_push + counters_pull)

next_spots = []
prev_spots = []
all_spots = []

for i in range(len(image_list)):
    image = image_list[i]
    im = image.convert('RGBA')
     
    data = np.array(im)   # "data" is a height x width x 4 numpy array
    print(data.shape)
    # red, green, blue, alpha = data.T # Temporarily unpack the bands for readability
    
    itlist1 = []
    itlist2 = []
    
    file, ext = os.path.splitext(file_names[i])
    fname = list(file)
    img_signum = int(fname[3]+fname[4]+fname[5])
    itlist1.append(img_signum)
    anom_spots = []
    anom_spots = anom_spots + next_spots

    # anom_spots = anom_spots + prev_spots
    next_spots = []
    prev_spots = []
    for j in range(len(all_counters)-1):
        num = all_counters[j]
        tnum = list(str(int(num)))
        cnt_signum = int(tnum[0]+tnum[1]+tnum[2])
        itlist2.append(cnt_signum)
        if j < len(counters_push):
            anom_num = int(tnum[3]+tnum[4]+tnum[5]+tnum[6])*4 + 3150*4
        else:
            anom_num = int(tnum[3]+tnum[4]+tnum[5]+tnum[6])*4 - 3150*4

        if img_signum == cnt_signum:
            if anom_num >= 40000:
                next_spots.append(abs(40000 - anom_num)-1)
                next_spots.append(abs(40000 - anom_num))
                next_spots.append(abs(40000 - anom_num)+1)
                prev_spots.append(40000 + anom_num)
            else:
                anom_spots.append(anom_num-1)
                anom_spots.append(anom_num)
                anom_spots.append(anom_num+1)
                all_spots.append(anom_num)
            
    # Replace white with red... (leaves alpha values alone...)
    # white_areas = (red == 27) & (blue == 27) & (green == 27)

    anom_points = np.zeros((data.shape[0], data.shape[1]), dtype=bool)
    anom_points[anom_spots, :] = True
    print(anom_points.shape)
    print(data.shape)
    data[..., :-1][anom_points] = (0, 128, 0)  # Transpose back needed
     
    im2 = Image.fromarray(data)
    im2 = im2.convert('RGB')
    im2.save(r'F:\strukton_project\Groningen\Prorail17112805si12\ABA\Prorail17112805si12\images\Prorail17112805\Prorail17112805\61_new\{}_new.jpg'.format(file), 'JPEG')