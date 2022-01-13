import pandas as pd
import requests

from src.config import Config


def save_ademe_projects():
    url = "https://koumoul.com/data-fair/api/v1/datasets/les-aides-financieres-de-l%27ademe/raw"
    r = requests.get(url)
    if r.status_code != 200:
        raise RuntimeError(f"API error : {r.content}")
    with open(Config.RAWDIR / "ademe.xlsx", "bw") as f:
        f.write(r.content)


def process_ademe():
    columns = {
        "idBeneficiaire": "siren",
        "nomBeneficiaire": "denomination",
        "dateConvention": "date_convention",
        "montant": None,
        "nature": None,
        "objet": "project",
    }
    types = {"idBeneficiaire": int}
    df = (
        pd.read_excel(Config.RAWDIR / "ademe.xlsx", usecols=columns.keys())
        .dropna(subset=["idBeneficiaire"])
        .astype(types)
        .rename(columns={k: v for k, v in columns.items() if v})
    )
    df.to_parquet(Config.INTDIR / "ademe.parquet")


if __name__ == "__main__":
    if not (Config.RAWDIR / "ademe.xlsx").exists():
        save_ademe_projects()
    process_ademe()
