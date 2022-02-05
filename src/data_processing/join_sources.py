import logging

import pandas as pd

from src.config import Config

from .common import mt_features

logger = logging.getLogger(__name__)


def join_sources():
    # ADEME is only used to join mission transition with sirene
    # All projet features must be obtained from missions transition
    ademe = pd.read_parquet(
        Config.INTDIR / "ademe.parquet", columns=["projet_md5", "siret"]
    )

    sirene = pd.read_parquet(
        Config.INTDIR / "sirene.parquet", columns=Config.SIRENE_FEATURES
    )
    matching = pd.read_parquet(Config.INTDIR / "ademe_mt.parquet")

    mt = pd.read_parquet(
        Config.INTDIR / "mission_transition.parquet",
    ).pipe(mt_features)

    combined = (
        pd.merge(mt, matching, on=["source"], how="inner")
        .merge(ademe, on=["projet_md5"], how="inner")
        .merge(sirene, on="siret", how="left")
        .drop(columns=["projet_md5", "siret", "source"])
    )
    logger.info(
        "join_source",
        extra={"shape": combined.shape, "features": sorted(combined.columns)},
    )
    combined.to_parquet(Config.INTDIR / "joined_project_siret.parquet")


if __name__ == "__main__":
    join_sources()
