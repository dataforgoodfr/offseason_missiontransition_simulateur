import pandas as pd

from src.data_processing.join_sources import add_occurence


def test_add_occurence():
    inp = pd.DataFrame({"source": [1, 2, 1], "siret": [1, 2, 1]})
    out = add_occurence(inp)
    exp = pd.DataFrame({"source": [1, 2], "siret": [1, 2], "occurence": [2, 1]})
    pd.testing.assert_frame_equal(out, exp)
