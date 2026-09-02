# -*- coding: utf-8 -*-
"""Isolation Forest detector for sliding-window ABA features."""

import numpy as np
from sklearn.ensemble import IsolationForest

from railai.normalize import normalize


def isolation_forest(my_data, int_count, sub_sampling, impurity, num_trees):
    rng = np.random.RandomState(42)

    split = round(len(my_data) / 3)
    X_train = my_data[0:split, :]
    X_test = my_data[split:len(my_data), :]
    xtrain_count = int_count[0:round(len(int_count) / 3)]
    xtest_count = int_count[round(len(int_count) / 3):len(int_count)]
    print("Before iforest:", sub_sampling, impurity)

    clf = IsolationForest(
        max_samples=sub_sampling,
        max_features=my_data.shape[1],
        contamination=impurity,
        random_state=rng,
    )
    print("After iforest:", sub_sampling, impurity)
    clf.fit(X_train)
    y_pred_train = clf.predict(X_train)
    y_pred_test = clf.predict(X_test)

    norm_train = np.where(y_pred_train == 1)
    anom_train = np.where(y_pred_train == -1)
    norm_test = np.where(y_pred_test == 1)
    anom_test = np.where(y_pred_test == -1)
    anom_icount = xtest_count[anom_test]
    anom_icount_train = xtrain_count[anom_train]

    ZZ = clf.decision_function(my_data)
    y_pred = np.concatenate((y_pred_train, y_pred_test), axis=0)
    anomalies = ZZ[(y_pred == -1)]

    adjusted_anom_scores = [-1 * s - .5 for s in anomalies]
    anom_scores = 1 - normalize(adjusted_anom_scores)

    norm_train = X_train[norm_train, :]
    anom_train = X_train[anom_train, :]
    norm_test = X_test[norm_test, :]
    anom_test = X_test[anom_test, :]

    return norm_train, anom_train, norm_test, anom_test, anom_icount, anom_icount_train, anom_scores
