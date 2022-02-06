import pandas as pd

from src.config import Config

from .common import mt_features


def main():
    joined = pd.read_parquet(Config.INTDIR / "joined_project_siret.parquet").assign(
        target=1
    )
    mt = pd.read_parquet(
        Config.INTDIR / "mission_transition.parquet",
    ).pipe(mt_features)

    sirene = pd.read_parquet(
        Config.INTDIR / "sirene.parquet", columns=Config.SIRENE_FEATURES
    )

    neg_samples = (
        # For now we force negative examples to be 5x the positive
        _negative_sample(mt, sirene, len(joined) * 5)
        .assign(target=0, occurence=1)
        .merge(mt, on=["source"], how="left")
        .merge(sirene, how="left", on=["siret"])
        .drop_duplicates(subset=["siret", "source"])
    )

    combined = pd.concat([joined, neg_samples], axis=0)
    combined.to_parquet(Config.INTDIR / "augmented.parquet")


def _negative_sample(mt: pd.DataFrame, sirene: pd.DataFrame, n: int) -> pd.DataFrame:
    combs = pd.merge(mt[["source"]], sirene[["siret"]], how="cross")
    return combs.sample(n=n, random_state=345)


if __name__ == "__main__":
    main()