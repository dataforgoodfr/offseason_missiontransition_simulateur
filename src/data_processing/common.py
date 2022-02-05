import pandas as pd


def mt_features(df: pd.DataFrame) -> pd.DataFrame:
    columns = ["source"] + [x for x in df.columns if x.startswith("topic")]
    return df[columns]
