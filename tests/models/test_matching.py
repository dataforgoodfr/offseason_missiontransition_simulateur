import numpy as np

from src.models.matching import FuzzyMatcher


def test_fuzzy_matcher():
    first = ["My name is Ali", "Prince Ali Ababouah"]
    second = ["My name is Ali Abdaal", "Ali is my name name"]

    matcher = FuzzyMatcher()
    score = matcher.predict_proba(first, second)
    exp = np.array([[1, 1], [0.6, 0.42]])
    np.testing.assert_array_equal(score, exp)
