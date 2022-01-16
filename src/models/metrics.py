import numpy as np
from sklearn.utils.validation import check_array


def dfill(a: np.ndarray) -> np.ndarray:
    n = a.size
    b = np.concatenate([[0], np.where(a[:-1] != a[1:])[0] + 1, [n]])
    return np.arange(n)[b[:-1]].repeat(np.diff(b))


def argunsort(s: np.ndarray) -> np.ndarray:
    n = s.size
    u = np.empty(n, dtype=np.int64)
    u[s] = np.arange(n)
    return u


def cumcount(a: np.ndarray) -> np.ndarray:
    """
    Count the cumulative number of occurence of element at each position
    """
    n = a.size
    s = a.argsort(kind="mergesort")
    i = argunsort(s)
    b = a[s]
    return (np.arange(n) - dfill(b))[i]


def uniquecount(a: np.ndarray) -> np.ndarray:
    """
    Count the cumulative number of unique values of the array
    """
    return (cumcount(a) == 0).cumsum()


def relative_attribution_curve(
    first: np.ndarray, second: np.ndarray, score: np.ndarray
) -> (np.ndarray, np.ndarray, np.ndarray):
    """
    Return the relative proportion of unique elements matched per dataset,
    as a funciton of the score.
    """
    first = check_array(first, dtype=None, ensure_2d=False)
    second = check_array(second, dtype=None, ensure_2d=False)
    score = check_array(score, ensure_2d=False)

    sorted_idx = np.argsort(score, kind="mergesort")[::-1]

    th = score[sorted_idx]
    first = uniquecount(first[sorted_idx]) / len(np.unique(first))
    second = uniquecount(second[sorted_idx]) / len(np.unique(second))
    return first, second, th
