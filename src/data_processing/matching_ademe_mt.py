import logging

import numpy as np
import pandas as pd
from thefuzz import fuzz

from src.config import Config

logger = logging.getLogger(__name__)


def load_and_process_ademe():
    if not (Config.INTDIR / "ademe.parquet").exists():
        raise RuntimeError("Missing ADEME data")
    df_ademe = pd.read_parquet(
        Config.INTDIR / "ademe.parquet", columns=["projet", "projet_md5"]
    )
    return df_ademe


def load_and_process_mission_transition():
    if not (Config.INTDIR / "mission_transition.parquet").exists():
        raise RuntimeError("Missing Mission Transition data")
    df_mission_transition = pd.read_parquet(
        Config.INTDIR / "mission_transition.parquet",
        columns=["source", "name", "funder_name"],
    ).pipe(lambda df: df[df["funder_name"] == "ADEME"])
    return df_mission_transition


def fuzzy_score(first: str, second: str) -> float:
    return max(
        [
            fuzz.partial_ratio(first, second),
            fuzz.token_set_ratio(first, second),
            fuzz.token_sort_ratio(first, second),
        ]
    )


v_fuzzy_score = np.vectorize(fuzzy_score)


def make_matching(df_product, threshold):
    return df_product.assign(
        score=lambda df: v_fuzzy_score(df["name"], df["projet"])
    ).pipe(lambda df: df[df["score"] > threshold])


def run_matching():
    df_ademe = load_and_process_ademe()
    df_mission_transition = load_and_process_mission_transition()

    df_product = df_ademe.merge(df_mission_transition, how="cross").pipe(
        make_matching, Config.MATCHING_THRESHOLD
    )[["source", "projet_md5"]]
    logger.info(
        "matching_ademe_mt",
        extra=dict(
            size=len(df_product),
            ademe_unique=df_product["projet_md5"].nunique(),
            mt_unique=df_product["source"].nunique(),
        ),
    )
    df_product.to_parquet(Config.INTDIR / "ademe_mt.parquet")


if __name__ == "__main__":
    run_matching()
