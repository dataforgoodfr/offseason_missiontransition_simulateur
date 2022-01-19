from pathlib import Path

import pandas as pd

from src.data_processing.matching_ademe_mt import make_matching


class TestMatchingAdemeMissionTransition:
    def test_make_matching(self):
        df_product = pd.read_csv(
            Path(__file__).parent / "fixtures" / "matching_ademe_mt" / "df_product.csv",
        )
        df_selected = make_matching(df_product, 75)[
            ["projet_md5", "source"]
        ].reset_index(drop=True)

        true_df_selected = pd.read_csv(
            Path(__file__).parent
            / "fixtures"
            / "matching_ademe_mt"
            / "df_selected.csv",
        )

        pd.testing.assert_frame_equal(df_selected, true_df_selected)
