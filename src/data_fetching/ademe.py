import logging
from pathlib import Path

import numpy as np
import pandas as pd
import requests

from src.config import Config
from src.data_fetching.common import v_intmd5

logger = logging.getLogger(__name__)


def save_ademe_projects(outfn: Path):
    url = "https://koumoul.com/data-fair/api/v1/datasets/les-aides-financieres-de-l%27ademe/raw"
    r = requests.get(url)
    if r.status_code != 200:
        raise RuntimeError(f"API error : {r.content}")
    with open(outfn, "bw") as f:
        f.write(r.content)


def process_ademe(fn: Path, outfn: Path):
    columns = {
        "idBeneficiaire": "siret",
        "nomBeneficiaire": "denomination",
        "dateConvention": "date_convention",
        "montant": None,
        "nature": None,
        "objet": "projet",
    }
    types = {"idBeneficiaire": int}
    df = (
        pd.read_excel(fn, usecols=columns.keys())
        .dropna(subset=["idBeneficiaire"])
        .astype(types)
        .rename(columns={k: v for k, v in columns.items() if v})
        .pipe(_drop_no_siret)
        .assign(
            siren=lambda x: np.int64(x["siret"] // 1e5),
            projet_md5=lambda frame: v_intmd5(frame["projet"]),
        )
        .drop_duplicates(["siret", "projet"])
    )
    assert df["projet"].nunique() == df["projet_md5"].nunique()
    logger.info("process_ademe", extra=dict(columns=sorted(df.columns), shape=df.shape))
    df.to_parquet(outfn)


def _drop_no_siret(ademe: pd.DataFrame) -> pd.DataFrame:
    """
    Drop lines for which the siret does not have at least 11 digits
    """
    small_siret = np.log10(ademe["siret"]) < 11
    return ademe[~small_siret]


if __name__ == "__main__":
    fn = Config.RAWDIR / "ademe.xlsx"
    if not fn.exists():
        save_ademe_projects(fn)
    outfn = Config.INTDIR / "ademe.parquet"
    process_ademe(fn, outfn)
