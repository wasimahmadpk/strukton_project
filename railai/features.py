# -*- coding: utf-8 -*-
"""Sliding-window statistical features from axle-box acceleration."""

from __future__ import division

import math

import numpy as np


def extract_features(vibration_data, int_counter, window_size):
    nwindows = math.floor(len(vibration_data) / window_size)

    fvl2 = []
    sr_counter = 0
    s_idx = 0
    for i in range(nwindows):
        int_count = int_counter[sr_counter:sr_counter + window_size]
        avg_icount = round(np.mean(int_count))
        sr_counter = sr_counter + round(window_size / 1)

        fvl1 = []
        window = np.array(vibration_data[s_idx:s_idx + window_size], dtype=np.float32)

        s_idx = s_idx + round(window_size / 1)
        xavp = sum(pow(window, 2)) / window_size
        xrms = math.sqrt(sum((pow(window, 2))) / window_size)
        xsra = pow((sum(np.sqrt(abs(window))) / window_size), 2)
        xm = np.mean(window)
        sd = np.std(window)
        xkv = sum(pow(((window - xm) / sd), 4)) / window_size
        xsv = sum(pow(((window - xm) / sd), 3)) / window_size
        maxW = max(window)
        minW = min(window)
        xppv = maxW - minW
        xcf = max(abs(window)) / np.sqrt((sum(pow(window, 2)) / window_size))
        xif = max(abs(window)) / (sum(abs(window)) / window_size)
        xmf = max(abs(window)) / (pow((sum(np.sqrt(abs(window))) / window_size), 2))
        xsf = np.sqrt(sum(pow(window, 2)) / (window_size)) / (sum(abs(window)) / window_size)
        xkf = (pow(sum(((window - xm)) / sd), 4) / window_size) / (pow((sum(pow(window, 2)) / window_size), 2))

        X = np.fft.fft(window)
        rmsf = np.sqrt(np.sum(abs(X / len(X)) ** 2))

        fvl1.append(xrms)
        fvl1.append(xsra)
        fvl1.append(xkv)
        fvl1.append(xsv)
        fvl1.append(xppv)
        fvl1.append(xcf)
        fvl1.append(xif)
        fvl1.append(xmf)
        fvl1.append(xsf)
        fvl1.append(xkf)
        fvl1.append(xm)
        fvl1.append(xavp)
        fvl1.append(rmsf)
        fvl1.append(avg_icount)
        fvl2.append(fvl1)

    feature_vectors = np.array(fvl2)
    feature_vectors[np.isnan(feature_vectors)] = 0
    return feature_vectors
