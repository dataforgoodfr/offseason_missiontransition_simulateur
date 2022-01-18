from pathlib import Path

import pandas as pd
import pytest

from src.data_processing.matching_ademe_mt import make_final_dataframe, make_matching


@pytest.fixture()
def dataframes():
    df_ademe = pd.read_csv(
        Path(__file__).parent / "fixtures" / "matching_ademe_mt" / "df_ademe.csv",
    )
    df_mission_transition = pd.read_csv(
        Path(__file__).parent
        / "fixtures"
        / "matching_ademe_mt"
        / "df_mission_transition.csv",
    )
    yield df_ademe, df_mission_transition


class TestMatchingAdemeMissionTransition:
    def test_make_matching(self):
        df_product = pd.read_csv(
            Path(__file__).parent / "fixtures" / "matching_ademe_mt" / "df_product.csv",
        )
        df_selected = make_matching(df_product, 75)

        true_df_selected = pd.read_csv(
            Path(__file__).parent
            / "fixtures"
            / "matching_ademe_mt"
            / "df_selected.csv",
        )

        pd.testing.assert_frame_equal(df_selected, true_df_selected)

    def test_make_final(self, dataframes):
        df_selected = pd.read_csv(
            Path(__file__).parent / "fixtures" / "matching_ademe_mt" / "df_selected.csv"
        )
        df_ademe, df_mission_transition = dataframes
        final_df = make_final_dataframe(df_selected, df_ademe, df_mission_transition)

        true_final_df = pd.read_csv(
            Path(__file__).parent / "fixtures" / "matching_ademe_mt" / "final_df.csv",
        )

        pd.testing.assert_series_equal(final_df["project"], true_final_df["project"])
        pd.testing.assert_series_equal(final_df["name"], true_final_df["name"])
