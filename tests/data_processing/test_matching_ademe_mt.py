from pathlib import Path

import pandas as pd
import pytest

from src.data_processing.matching_ademe_mt import (
    make_final_dataframe,
    make_matching,
    make_sub_dataframes,
)


@pytest.fixture()
def dataframes():
    df_ademe = pd.read_csv(
        Path(__file__).parent / "fixtures" / "matching_ademe_mt" / "df_ademe.csv",
        index_col=0,
    )
    df_mission_transition = pd.read_csv(
        Path(__file__).parent
        / "fixtures"
        / "matching_ademe_mt"
        / "df_mission_transition.csv",
        index_col=0,
    )
    yield df_ademe, df_mission_transition


class TestMatchingAdemeMissionTransition:
    def test_make_sub_dataframes(self, dataframes):
        sub_df_ademe, sub_df_mission_transition = make_sub_dataframes(*dataframes)
        assert sub_df_ademe.columns.tolist() == ["project", "index_ademe"]
        assert sub_df_mission_transition.columns.tolist() == ["name", "index_mt"]

    def test_make_matching(self):
        sub_df_ademe = pd.read_csv(
            Path(__file__).parent
            / "fixtures"
            / "matching_ademe_mt"
            / "sub_df_ademe.csv"
        )
        sub_df_mission_transition = pd.read_csv(
            Path(__file__).parent
            / "fixtures"
            / "matching_ademe_mt"
            / "sub_df_mission_transition.csv"
        )

        df_product = sub_df_ademe.merge(sub_df_mission_transition, how="cross")
        df_selected = make_matching(df_product, 70)

        true_df_selected = pd.read_csv(
            Path(__file__).parent
            / "fixtures"
            / "matching_ademe_mt"
            / "df_selected.csv",
            index_col=0,
        )

        assert df_selected.equals(true_df_selected)

    def test_make_final(self, dataframes):
        df_selected = pd.read_csv(
            Path(__file__).parent / "fixtures" / "matching_ademe_mt" / "df_selected.csv"
        )
        df_ademe, df_mission_transition = dataframes
        final_df = make_final_dataframe(df_selected, df_ademe, df_mission_transition)

        true_final_df = pd.read_csv(
            Path(__file__).parent / "fixtures" / "matching_ademe_mt" / "final_df.csv",
            index_col=0,
        )

        assert (final_df["project"] == true_final_df["project"]).all()
        assert (final_df["name"] == true_final_df["name"]).all()
