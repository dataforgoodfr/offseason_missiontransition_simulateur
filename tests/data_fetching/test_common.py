import numpy as np

from src.data_fetching.common import intmd5, v_intmd5


def test_intmd5():
    out = intmd5("hello world")
    assert out == 1589001147


def test_v_intmd5():
    out = v_intmd5(["hello", "world"])
    np.testing.assert_array_equal(out, [1564557354, 2105094199])
