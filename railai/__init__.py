# -*- coding: utf-8 -*-
"""RailAI: axle-box acceleration anomaly detection for rail infrastructure."""

from railai.detection import isolation_forest
from railai.features import extract_features
from railai.paths import data_paths

__all__ = [
    "RailDefects",
    "data_paths",
    "pre_processing",
    "extract_features",
    "isolation_forest",
]


def __getattr__(name):
    if name == "RailDefects":
        from railai.pipeline import RailDefects

        return RailDefects
    if name == "pre_processing":
        from railai.preprocessing import pre_processing

        return pre_processing
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
