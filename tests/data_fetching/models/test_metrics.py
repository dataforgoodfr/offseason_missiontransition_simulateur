import numpy as np

from src.models.metrics import cumcount, uniquecount


def test_cumcount():
    inp = np.array(list("aaabaaacaaadaaac"))
    out = cumcount(inp)
    exp = [0, 1, 2, 0, 3, 4, 5, 0, 6, 7, 8, 0, 9, 10, 11, 1]
    np.testing.assert_array_equal(out, exp)


def test_uniquecount():
    inp = np.array(list("aaabaaacaaadaaac"))
    out = uniquecount(inp)
    exp = [1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 4]
    np.testing.assert_array_equal(out, exp)
