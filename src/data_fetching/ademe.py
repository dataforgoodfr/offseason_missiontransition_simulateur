import numpy as np
import pandas as pd
import requests

from src.config import Config

from .common import vect_preproc_text


def save_ademe_projects():
    url = "https://koumoul.com/data-fair/api/v1/datasets/les-aides-financieres-de-l%27ademe/raw"
    r = requests.get(url)
    if r.status_code != 200:
        raise RuntimeError(f"API error : {r.content}")
    with open(Config.RAWDIR / "ademe.xlsx", "bw") as f:
        f.write(r.content)


def process_ademe():
    columns = {
        "idBeneficiaire": "siret",
        "nomBeneficiaire": "denomination",
        "dateConvention": "date_convention",
        "montant": None,
        "nature": None,
        "objet": "projet",
        "referenceDecision": "reference",
    }
    types = {"idBeneficiaire": int}
    df = (
        pd.read_excel(Config.RAWDIR / "ademe.xlsx", usecols=columns.keys())
        .dropna(subset=["idBeneficiaire"])
        .astype(types)
        .rename(columns={k: v for k, v in columns.items() if v})
        .pipe(_drop_no_siret)
        .assign(
            siren=lambda x: np.int64(x["siret"] // 1e5),
            projet_preproc=lambda df: vect_preproc_text(df["projet"]),
        )
    )
    df.to_parquet(Config.INTDIR / "ademe.parquet")


def _drop_no_siret(ademe: pd.DataFrame) -> pd.DataFrame:
    """
    Drop lines for which the siret does not have at least 11 digits
    """
    small_siret = np.log10(ademe["siret"]) < 11
    return ademe[~small_siret]


if __name__ == "__main__":
    if not (Config.RAWDIR / "ademe.xlsx").exists():
        save_ademe_projects()
    process_ademe()
