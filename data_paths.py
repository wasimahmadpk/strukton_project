# -*- coding: utf-8 -*-
"""Default data locations for the Groningen measurement used in the thesis.

Set ``STRUKTON_DATA_ROOT`` to relocate the tree without editing this file.
When that variable is unset, the original Windows paths are used unchanged.
"""

import os

# Exact paths from the 2019 thesis checkout (Groningen, 28 Nov 2017).
_ORIG_DATA = r"F:\UTDATA3OCT\strukton_project\Groningen\Prorail17112805si12\ABA\Prorail17112805si12\Prorail17112805si12.time.h5"
_ORIG_SEG = r"F:\UTDATA3OCT\strukton_project\Groningen\Routefile\Prorail17112805si12_seg.csv"
_ORIG_POI = r"F:\UTDATA3OCT\strukton_project\Groningen\Routefile\Prorail17112805si12_poi.csv"
_ORIG_PROCESSED = r"F:\UTDATA3OCT\strukton_project\Groningen\Prorail17112805si12\ABA\Prorail17112805si12\Prorail17112805si12.processed.h5"
_ORIG_COUNTERS = r"F:\UTDATA3OCT\strukton_project\Groningen\Prorail17112805si12\ABA\Prorail17112805si12\counter_data"

_MEASUREMENT = "Prorail17112805si12"


class data_paths:
    """Holds the six file locations consumed by ``RailDefects``."""

    def __init__(self):
        root = os.environ.get("STRUKTON_DATA_ROOT")
        if root:
            aba = os.path.join(root, _MEASUREMENT, "ABA", _MEASUREMENT)
            self.data_file = os.path.join(aba, _MEASUREMENT + ".time.h5")
            self.sync_file = self.data_file
            self.seg_file = os.path.join(root, "Routefile", _MEASUREMENT + "_seg.csv")
            self.poi_file = os.path.join(root, "Routefile", _MEASUREMENT + "_poi.csv")
            self.processed_file = os.path.join(aba, _MEASUREMENT + ".processed.h5")
            self.counters_path = os.environ.get(
                "STRUKTON_COUNTERS", os.path.join(aba, "counter_data")
            )
        else:
            self.data_file = _ORIG_DATA
            self.sync_file = _ORIG_DATA
            self.seg_file = _ORIG_SEG
            self.poi_file = _ORIG_POI
            self.processed_file = _ORIG_PROCESSED
            self.counters_path = os.environ.get("STRUKTON_COUNTERS", _ORIG_COUNTERS)

        self.data_path = [
            self.data_file,
            self.sync_file,
            self.seg_file,
            self.poi_file,
            self.processed_file,
            self.counters_path,
        ]


_default = data_paths()
data_paths.data_file = _default.data_file
data_paths.sync_file = _default.sync_file
data_paths.seg_file = _default.seg_file
data_paths.poi_file = _default.poi_file
data_paths.processed_file = _default.processed_file
data_paths.counters_path = _default.counters_path
data_paths.data_path = _default.data_path
