import pandas as pd

from src.config import Config


def main():
    augmented = pd.read_parquet(Config.INTDIR / "augmented.parquet")

    # Include feature engineering later on
    final = augmented

    final.to_parquet(Config.PROCDIR / "financed_projects.parquet")


if __name__ == "__main__":
    main()
