import numpy as np
import pandas as pd

from src.config import Config


def main():
    df = pd.read_parquet(Config.INTDIR / "augmented.parquet").pipe(define_folds)

    df.to_parquet(Config.PROCDIR / "financed_projects.parquet")


def define_folds(df: pd.DataFrame) -> pd.DataFrame:
    return df.assign(valid_fold=lambda df: np.int8((df["siret"] // 1000_000) % 5))


if __name__ == "__main__":
    main()
