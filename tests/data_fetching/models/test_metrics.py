import numpy as np

from src.models.metrics import cumcount, relative_attribution_curve, uniquecount


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


def test_relative_attribution_curve():
    score = np.array([0, 2, 1, -1])
    first = np.array(list("abab"))
    second = np.array(list("bdeb"))
    rate_first, rate_second, th = relative_attribution_curve(first, second, score)

    np.testing.assert_array_equal(th, [2, 1, 0, -1])
    np.testing.assert_array_equal(rate_first, [0.5, 1, 1, 1])
    np.testing.assert_array_equal(rate_second, [1 / 3, 2 / 3, 1, 1])
