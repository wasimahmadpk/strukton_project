import numpy as np

from railai.detection import isolation_forest


def test_isolation_forest_flags_late_spikes():
    rng = np.random.default_rng(0)
    normal = rng.normal(0.0, 0.4, size=(240, 2))
    spikes = rng.normal(6.0, 0.2, size=(60, 2))
    data = np.vstack([normal, spikes])
    counters = np.arange(len(data), dtype=float)

    _ntr, _atr, _nte, anom_test, anom_icount, _train_counts, scores = isolation_forest(
        data, counters, sub_sampling=64, impurity=0.15, num_trees=40
    )

    assert anom_test.shape[0] >= 1
    assert len(anom_icount) >= 1
    assert np.all(anom_icount >= 100)
    assert len(scores) == len(anom_icount) + len(_train_counts)
    assert np.all((scores >= 0) & (scores <= 1))
