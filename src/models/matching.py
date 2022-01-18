import numpy as np
from sklearn.utils.validation import check_array
from thefuzz import fuzz


def combined_fuzzy_matching(first, other):
    return max(
        fuzz.partial_ratio(first, other),
        fuzz.token_set_ratio(first, other),
    )


v_combined_fuzzy_matching = np.vectorize(combined_fuzzy_matching)


class FuzzyMatcher:
    def fit(self, first, second):
        return self

    def predict_proba(self, first, second):
        first = check_array(first, dtype=None, ensure_2d=False).reshape(-1, 1)
        second = check_array(second, dtype=None, ensure_2d=False).reshape(1, -1)
        return v_combined_fuzzy_matching(first, second) / 100
