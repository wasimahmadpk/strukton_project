# -*- coding: utf-8 -*-
"""Min-max normalisation used for Isolation Forest anomaly scores."""

import numpy as np


def normalize(data):
    mindata, maxdata = min(data), max(data)
    span = maxdata - mindata
    norm_data = []
    for i in range(len(data)):
        norm_data.append((data[i] - mindata) / span)
    return np.array(norm_data)
