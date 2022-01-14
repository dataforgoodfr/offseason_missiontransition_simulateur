import pandas as pd
from thefuzz import fuzz
from tqdm import tqdm

from src.config import Config


def load_and_process_ademe():
    if not (Config.INTDIR / "ademe.parquet").exists():
        raise RuntimeError("Missing ADEME data")
    df_ademe = pd.read_parquet(Config.INTDIR / "ademe.parquet")
    return df_ademe


def load_and_process_mission_transition():
    if not (Config.INTDIR / "mission_transition.parquet").exists():
        raise RuntimeError("Missing Mission Transition data")
    df_mission_transition = pd.read_parquet(
        Config.INTDIR / "mission_transition.parquet"
    ).pipe(lambda df: df[df["funder_name"] == "ADEME"])
    return df_mission_transition


def compute_score(df_product):
    return max(
        [
            fuzz.partial_ratio(df_product["name"], df_product["project"]),
            fuzz.token_set_ratio(df_product["name"], df_product["project"]),
            fuzz.token_sort_ratio(df_product["name"], df_product["project"]),
        ]
    )


def make_matching(df_product, threshold):
    tqdm.pandas()
    df_product["score"] = df_product.progress_apply(compute_score, axis=1)
    df_selected = df_product.loc[
        df_product["score"] > threshold, ["index_ademe", "index_mt"]
    ].reset_index(drop=True)
    return df_selected


def make_final_dataframe(df_selected, df_ademe, df_mission_transition):
    df_selected_with_ademe = pd.merge(
        df_selected, df_ademe, left_on="index_ademe", right_index=True
    )

    final_df = pd.merge(
        df_selected_with_ademe,
        df_mission_transition,
        left_on="index_mt",
        right_index=True,
    ).reset_index(drop=True)
    return final_df


if __name__ == "__main__":
    # Loading data
    df_ademe = load_and_process_ademe()
    df_mission_transition = load_and_process_mission_transition()

    df_product = (
        df_ademe[["project"]]
        .reset_index()
        .merge(
            df_mission_transition[["name"]].reset_index(),
            how="cross",
            suffixes=["_ademe", "_mt"],
        )
    )

    df_selected = make_matching(df_product, Config.MATCHING_THRESHOLD)

    final_df = make_final_dataframe(df_selected, df_ademe, df_mission_transition)

    final_df.to_parquet(Config.INTDIR / "ademe_mt.parquet")
