#!/usr/bin/env python
"""Launcher for the command-line detection pipeline (``python raildefects_main.py``)."""

from railai.paths import data_paths
from railai.pipeline import RailDefects

if __name__ == "__main__":
    obj = RailDefects(1)
    obj.anomaly_detection(
        pprocessed_file=data_paths.data_path[4],
        seg_file=data_paths.data_path[2],
        features="RMS",
        sliding_window=2000,
        sub_sampling=128,
        impurity=0.025,
        num_trees=100,
    )
