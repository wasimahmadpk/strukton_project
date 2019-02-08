
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 00:27:42 2018

@author: Waseem
"""

import numpy as np
from normalization import normalize
from histogram import plot_hist
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
from random import sample
from sklearn.ensemble import IsolationForest

print(__doc__)


def isolation_forest(my_data, int_count):

    rng = np.random.RandomState(42)

    # Generate train and test data
    X_train = my_data[0:round(len(my_data)/2), :]
    X_test = my_data[round(len(my_data)/2):len(my_data), :]
    xtrain_count = int_count[0:round(len(int_count)/2)]
    xtest_count = int_count[round(len(int_count)/2):len(int_count)]

    # fit the model
    clf = IsolationForest(max_samples=256, max_features=my_data.shape[1], contamination=0.1, random_state=rng)
    clf.fit(X_train)
    y_pred_train = clf.predict(X_train)
    y_pred_test = clf.predict(X_test)
    
    norm_train = np.where(y_pred_train == 1)
    anom_train = np.where(y_pred_train == -1)
    norm_test = np.where(y_pred_test == 1)
    anom_test = np.where(y_pred_test == -1)
    anom_icount = xtest_count[anom_test]
    anom_icount_train = xtrain_count[anom_train]

    # Anomaly score
    ZZ = clf.decision_function(X_test)
    anomalies = ZZ[(y_pred_test == -1)]
    anom_scores = 1 - normalize(anomalies)
    plt.figure(3)
    plt.plot(anom_scores)

    # Contour plot of normal and anomalous samples in train and test set
    aa, bb = np.meshgrid(np.linspace(np.min(my_data[:, 1])-1, 50, 30),
                         np.linspace(np.min(my_data[:, 0])-1, 10, 30))
    decision = clf.decision_function(np.c_[aa.ravel(), bb.ravel()])
    Z = decision.reshape(aa.shape)

    plt.figure(4)
    plt.cla()
    plt.title("Anomaly detection-iForest")
    cb = plt.contourf(aa, bb, Z, cmap=plt.cm.Blues_r)
    a = plt.scatter(X_train[norm_train, 1], X_train[norm_train, 0], c='white',
                    s=25, edgecolor='k')
    b = plt.scatter(X_test[norm_test, 1], X_test[norm_test, 0], c='green',
                    s=25, edgecolor='k')
    c = plt.scatter(X_test[anom_test, 1], X_test[anom_test, 0], c='red',
                    s=25, edgecolor='k')
    plt.axis('tight')
    plt.xlim((np.min(my_data[:, 1])-1, 50))
    plt.ylim((np.min(my_data[:, 0])-1, 10))
    plt.legend([a, b, c],
               ["training data", "normal data", "anomalies"],
               loc="upper")
    plt.xlabel('Kurtosis')
    plt.ylabel('RMS')
    plt.colorbar(cb)
    plt.show()

    norm_train = X_train[norm_train, :]
    anom_train = X_train[anom_train, :]
    norm_test = X_test[norm_test, :]
    anom_test = X_test[anom_test, :]
    
    return norm_train, anom_train, norm_test, anom_test, anom_icount, anom_icount_train