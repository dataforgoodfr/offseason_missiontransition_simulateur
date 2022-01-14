import pandas as pd
from thefuzz import fuzz
from tqdm import tqdm

from src.config import Config


def load_and_process_ademe():
    if not (Config.INTDIR / "ademe.parquet").exists():
        raise RuntimeError("Missing ADEME data")
    df_ademe = pd.read_parquet(Config.INTDIR / "ademe.parquet")
    sub_df_ademe = pd.DataFrame(
        dict(project=df_ademe["project"], index_ademe=df_ademe.index)
    )
    return df_ademe, sub_df_ademe


def load_and_process_mission_transition():
    if not (Config.INTDIR / "mission_transition.parquet").exists():
        raise RuntimeError("Missing Mission Transition data")
    df_mission_transition = pd.read_parquet(
        Config.INTDIR / "mission_transition.parquet"
    )
    df_mission_transition = df_mission_transition[
        df_mission_transition["funder_name"] == "ADEME"
    ]
    sub_df_mission_transition = pd.DataFrame(
        dict(name=df_mission_transition["name"], index_mt=df_mission_transition.index)
    )
    return df_mission_transition, sub_df_mission_transition


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
    ]
    return df_selected


def make_final_dataframe(df_selected, df_ademe, df_mission_transition):
    df_selected_with_ademe = pd.merge(
        df_selected, df_ademe.reset_index(), left_on="index_ademe", right_on="index"
    )

    final_df = pd.merge(
        df_selected_with_ademe,
        df_mission_transition.reset_index(),
        left_on="index_mt",
        right_on="index",
    )
    return final_df


if __name__ == "__main__":
    MATCHING_THRESHOLD = Config.MATCHING_THRESHOLD
    # Loading data
    df_ademe, sub_df_ademe = load_and_process_ademe()
    df_mission_transition, sub_df_mission_transition = load_and_process_ademe()

    df_product = sub_df_ademe.merge(sub_df_mission_transition, how="cross")

    # Extracting salient couples
    df_selected = make_matching(df_product, MATCHING_THRESHOLD)

    # Create and save final dataframe
    final_df = make_final_dataframe(df_selected, df_ademe, df_mission_transition)

    final_df.to_parquet(Config.INTDIR / "ademe_mt.parquet")
