import numpy as np

from railai.features import extract_features


def test_extract_features_window_count_and_spike():
    window = 64
    rng = np.random.default_rng(1)
    quiet = rng.normal(0.0, 0.05, size=window * 2)
    spike = rng.normal(0.0, 0.05, size=window)
    spike[20:25] = 8.0
    signal = np.concatenate([quiet, spike])
    counters = np.arange(len(signal), dtype=float)

    features = extract_features(signal, counters, window)
    assert features.shape[0] == 3
    assert features.shape[1] == 14
    rms = features[:, 0]
    assert rms[2] > rms[0]
    assert rms[2] > rms[1]
