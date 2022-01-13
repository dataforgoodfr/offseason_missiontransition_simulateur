import argparse
import os

import pandas as pd
from thefuzz import fuzz
from tqdm import tqdm

from src.config import Config


def load_data():
    if not os.path.exists(Config.INTDIR / "ademe.parquet"):
        raise RuntimeError("Missing ADEME data")
    df_ademe = pd.read_parquet(Config.INTDIR / "ademe.parquet")

    if not os.path.exists(Config.INTDIR / "mission_transition.parquet"):
        raise RuntimeError("Missing Mission Transition data")
    df_mission_transition = pd.read_parquet(
        Config.INTDIR / "mission_transition.parquet"
    )

    return df_ademe, df_mission_transition


def make_sub_dataframes(df_ademe, df_mission_transition):
    sub_df_ademe = pd.DataFrame(
        dict(project=df_ademe["project"], index_ademe=df_ademe.index)
    )
    sub_df_mission_transition = pd.DataFrame(
        dict(name=df_mission_transition["name"], index_mt=df_mission_transition.index)
    )
    return sub_df_ademe, sub_df_mission_transition


def compute_score(df_product):
    return fuzz.ratio(df_product["name"], df_product["project"])


def make_matching(df_product, threshold):
    tqdm.pandas()
    df_product["score"] = df_product.progress_apply(compute_score, axis=1)
    df_selected = df_product[df_product["score"] > threshold][
        ["index_ademe", "index_mt"]
    ]
    return df_selected


def make_final_dataframe(df_selected, df_ademe, df_mission_transition):
    df_ademe_ = df_ademe.copy()
    df_ademe_ = df_ademe_[df_ademe_.index.isin(df_selected["index_ademe"])]
    df_ademe_["merge_indexes"] = df_ademe_.apply(
        lambda row: df_selected[df_selected["index_ademe"] == row.name].index, axis=1
    )
    df_ademe_ = df_ademe_.explode("merge_indexes")

    df_mission_transition_ = df_mission_transition.copy()
    df_mission_transition_ = df_mission_transition_[
        df_mission_transition_.index.isin(df_selected["index_mt"])
    ]
    df_mission_transition_["merge_indexes"] = df_mission_transition_.apply(
        lambda row: df_selected[df_selected["index_mt"] == row.name].index, axis=1
    )
    df_mission_transition_ = df_mission_transition_.explode("merge_indexes")

    final_df = pd.merge(
        left=df_ademe_,
        right=df_mission_transition_,
        on="merge_indexes",
        suffixes=["_ademe", "_mt"],
    )
    return final_df


if __name__ == "__main__":
    # Parsing the threshold
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument(
        "--threshold",
        type=float,
        help="Threshold to apply for the fuzzy matching",
        default=70,
    )
    args = argument_parser.parse_args()

    # Loading data
    df_ademe, df_mission_transition = load_data()

    # Keeping the columns used in the fuzzy matching
    sub_df_ademe, sub_df_mission_transition = make_sub_dataframes(
        df_ademe, df_mission_transition
    )

    df_product = sub_df_ademe.merge(sub_df_mission_transition, how="cross")

    # Extracting salient couples
    df_selected = make_matching(df_product, args.threshold)

    # Create and save final dataframe
    final_df = make_final_dataframe(df_selected, df_ademe, df_mission_transition)

    final_df.to_parquet(Config.INTDIR / "ademe_mt.parquet")
