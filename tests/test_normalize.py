import numpy as np

from railai.normalize import normalize


def test_normalize_spans_zero_to_one():
    scaled = normalize([0.0, 5.0, 10.0])
    assert np.allclose(scaled, [0.0, 0.5, 1.0])


def test_normalize_preserves_order():
    scaled = normalize([3.0, 1.0, 2.0])
    assert scaled[1] < scaled[2] < scaled[0]
