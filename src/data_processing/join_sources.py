import logging

import pandas as pd

from src.config import Config

logger = logging.getLogger(__name__)


def join_sources():
    # ADEME is only used to join mission transition with sirene
    # All projet features must be obtained from missions transition
    ademe = pd.read_parquet(
        Config.INTDIR / "ademe.parquet", columns=["projet_md5", "siret"]
    )

    # Only naf is currently used in the final model
    sirene = pd.read_parquet(
        Config.INTDIR / "sirene.parquet", columns=["siret", "naf_etab"]
    )
    matching = pd.read_parquet(Config.INTDIR / "ademe_mt.parquet")

    # For now no info about the project is required.
    # Info will be added depending on the underlying model needs
    mt = pd.read_parquet(
        Config.INTDIR / "mission_transition.parquet", columns=["source"]
    )

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
