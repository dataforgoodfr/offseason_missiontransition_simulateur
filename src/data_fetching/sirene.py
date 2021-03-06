import sqlite3
import time
from datetime import date
from sqlite3 import Connection

import numpy as np
import pandas as pd
import requests
import urllib3
from requests.auth import HTTPBasicAuth
from tqdm import tqdm

from src.config import ROOTDIR, Config

# The INSEE API does not have security settings
# The following line remove the constant warnings
urllib3.disable_warnings()

BASE_URL = "https://api.insee.fr/entreprises/sirene/V3/"

ENT_TYPES = ["TPE", "PME", "ETI", "GE"]


class INSEEConnector:
    def __init__(self):
        self.token = None
        self.generate_token()

    def header(self):
        return {"Authorization": f"Bearer {self.token}"}

    def generate_token(self):
        """
        Generate and store a temporary token for the Sirene API
        """
        if Config.INSEE_KEY is None or Config.INSEE_SECRET is None:
            raise KeyError("Set environment variables INSEE_KEY and INSEE_SECRET")

        r = requests.post(
            "https://api.insee.fr/token",
            auth=HTTPBasicAuth(Config.INSEE_KEY, Config.INSEE_SECRET),
            data={"grant_type": "client_credentials", "validity_period": 3600 * 24},
        )
        assert r.status_code == 200
        self.token = r.json()["access_token"]


def request_insee(url: str):
    """
    Call an INSEE api with token regeneration if needed.
    """
    connector = INSEEConnector()

    response = requests.get(url, headers=connector.header())
    if response.status_code == 401:
        connector.generate_token()
        response = requests.get(url, headers=connector.header())

    if response.status_code == 401:
        raise RuntimeError("INSEE connection error")

    return response


def etab_info(siret: int) -> dict:
    """
    Get some data from INSEE API for the given siret

    :param siret:
    The siret of company site of interest
    """
    url = BASE_URL + f"siret/{str(siret).zfill(14)}"
    response = request_insee(url)

    if response.status_code in [404, 403]:
        raise RuntimeError(response.json()["header"]["message"])
    elif response.status_code != 200:
        raise RuntimeError(f"Error fetching siret {siret} : {response.text}")

    return parse_etab_info(response.json())


def parse_etab_info(content: dict) -> dict:
    """
    Extract site infos from the API output
    """
    unite_legale = parse_unite_legale(content["etablissement"]["uniteLegale"])
    etab_adresse = parse_etab_adresse(content["etablissement"]["adresseEtablissement"])
    etab_info = parse_etab_details(content["etablissement"])
    return {**etab_info, **etab_adresse, **unite_legale}


WORKFORCE_CODE = {
    "NN": None,
    "00": [0, 0],
    "01": [1, 2],
    "02": [3, 5],
    "03": [6, 9],
    "11": [10, 19],
    "12": [20, 49],
    "21": [50, 99],
    "22": [100, 199],
    "31": [200, 249],
    "32": [250, 499],
    "41": [500, 999],
    "42": [1000, 1999],
    "51": [2000, 4999],
    "52": [5000, 9999],
    "53": [10000, None],
}


def parse_unite_legale(unite_legale: dict) -> dict:
    """
    Parse data from sirene/v3 API

    :param:
    The json content of the API call

    :date_status:
    Data at which to select the time dependent properties.
    """
    return {
        "date_creation": date.fromisoformat(unite_legale["dateCreationUniteLegale"]),
        "forju": int(unite_legale["categorieJuridiqueUniteLegale"]),
        "denomination": unite_legale["denominationUniteLegale"],
        "naf": unite_legale["activitePrincipaleUniteLegale"],
        "naf_version": unite_legale["nomenclatureActivitePrincipaleUniteLegale"],
        "ess": unite_legale["economieSocialeSolidaireUniteLegale"],
        "effectifs": unite_legale["trancheEffectifsUniteLegale"],
        "effectifs_annee": unite_legale["anneeEffectifsUniteLegale"],
        "ent_type": unite_legale["categorieEntreprise"],
        "ent_type_annee": unite_legale["anneeCategorieEntreprise"],
    }


def parse_etab_adresse(etab: dict) -> dict:
    return {
        "adr_num_voie": etab["numeroVoieEtablissement"],
        "adr_type_voie": etab["typeVoieEtablissement"],
        "adr_lib_voie": etab["libelleVoieEtablissement"],
        "adr_code_postal": etab["codePostalEtablissement"],
        "adr_commune": etab["libelleCommuneEtablissement"],
        "adr_code_commune": etab["codeCommuneEtablissement"],
        "adr_code_etranger": etab["codePaysEtrangerEtablissement"],
    }


def parse_etab_details(etab: dict) -> dict:
    return {
        "siret": etab["siret"],
        "siren": etab["siren"],
        "dt_crea_etab": date.fromisoformat(etab["dateCreationEtablissement"]),
        "effectifs_etab": etab["trancheEffectifsEtablissement"],
        "etab_siege": etab["etablissementSiege"],
        "naf_etab": etab["periodesEtablissement"][0]["activitePrincipaleEtablissement"],
        "naf_version_etab": etab["periodesEtablissement"][0][
            "nomenclatureActivitePrincipaleEtablissement"
        ],
    }


def fetch_ademe_siret():
    connector = sqlite3.connect(Config.DB_URI)
    ademe_siret = pd.read_parquet(Config.INTDIR / "ademe.parquet", columns=["siret"])[
        "siret"
    ]
    to_fetch = _missing_siret(connector, ademe_siret)
    for siret in tqdm(to_fetch):
        try:
            etab_data = pd.DataFrame.from_records([etab_info(siret)])
        except RuntimeError as exc:
            if str(exc).startswith("??tablissement non diffusable"):
                etab_data = pd.DataFrame.from_records([{"siret": siret}])

        etab_data.to_sql("etab", con=connector, if_exists="append", index=False)
        # ensures that the amount of request is below the API limitation of 7/seconds
        time.sleep(0.15)


def _missing_siret(connector: Connection, ademe_siret: pd.Series) -> list:
    if "etab" not in _list_tables(connector):
        _create_etab_table(connector)
        return sorted(set(ademe_siret))
    present = pd.read_sql("select siret from etab", connector)["siret"]
    return sorted(set(ademe_siret) - set(present))


def _create_etab_table(connector: Connection):
    with open(ROOTDIR / "references" / "etab_schema.sql") as f:
        connector.cursor().execute(f.read())


def _list_tables(con: Connection) -> list:
    """
    List all created tables in a sqlite3 database
    """
    cursor = con.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return [x[0] for x in cursor.fetchall()]


def _process_naf(df: pd.DataFrame, column: str) -> pd.DataFrame:
    nafs = {
        v: k
        for k, v in pd.read_csv(Config.REFDIR / "libelles_naf.csv")["naf8"]
        .to_dict()
        .items()
    }
    features = {
        f"{column}_code": df[column]
        .str.replace(".", "", regex=False)
        .map(nafs)
        .fillna(-1)
        .astype(np.int16)
    }

    return df.assign(**features)


def _ent_type_code(df: pd.DataFrame) -> pd.DataFrame:
    matching = {k: i for i, k in enumerate(ENT_TYPES)}
    return df.assign(
        ent_type_code=lambda df: df["ent_type"].map(matching).fillna(-1).astype(np.int8)
    )


def process_siret():
    columns = [
        "adr_code_commune",
        "adr_code_etranger",
        "date_creation",
        "dt_crea_etab",
        "effectifs",
        "effectifs_etab",
        "ent_type",
        "ess",
        "forju",
        "naf",
        "naf_etab",
        "siret",
    ]
    connector = sqlite3.connect(Config.DB_URI)
    df = (
        pd.read_sql(
            "select {} from etab".format(",".join(columns)),
            connector,
        )
        .pipe(_format_siret)
        .dropna(subset=["naf"])
        .pipe(_process_naf, "naf_etab")
        .pipe(_process_naf, "naf")
        .pipe(_ent_type_code)
        .drop(columns=["naf", "naf_etab", "ent_type"])
        .astype({"forju": np.int16})
    )
    df.to_parquet(Config.INTDIR / "sirene.parquet")


def _format_siret(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pipeline to format the raw data of the sirene API
    """
    return df


if __name__ == "__main__":
    fetch_ademe_siret()
    process_siret()
