from datetime import date

import requests
from requests.auth import HTTPBasicAuth

from src.config import Config

BASE_URL = "https://api.insee.fr/entreprises/sirene/V3/"


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
            verify=False,
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
        response = requests.get(url, headers=connector.header(), verify=True)

    if response.status_code == 401:
        raise RuntimeError("INSEE connection error")

    return response


def company_info(siren, date_status: date = None) -> dict:
    """
    Get some data from INSEE API for the given company

    :param siren:
    The siren of company of interest
    """

    url = BASE_URL + f"siren/{siren}"
    response = request_insee(url)
    if response.status_code == 404:
        raise RuntimeError(response.json()["header"]["message"])
    elif response.status_code != 200:
        raise RuntimeError(f"Error fetching siren {siren} : {response.text}")

    return parse_company_info(response.json(), date_status)


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


def parse_company_info(content: dict, date_status: date = None) -> dict:
    """
    Parse data from sirene/v3 API

    :param:
    The json content of the API call

    :date_status:
    Data at which to select the time dependent properties.
    """
    common = content["uniteLegale"]
    time_dependent = _get_time_dependent_info(common, date_status)
    return {
        "siren": common["siren"],
        "date_creation": date.fromisoformat(common["dateCreationUniteLegale"]),
        "effectifs": common["trancheEffectifsUniteLegale"],
        "effectifs_annee": int(common["anneeEffectifsUniteLegale"]),
        "ent_type": common["categorieEntreprise"],
        "ent_type_annee": int(common["anneeCategorieEntreprise"]),
        "forju": int(time_dependent["categorieJuridiqueUniteLegale"]),
        "naf": time_dependent["activitePrincipaleUniteLegale"],
        "naf_version": time_dependent["nomenclatureActivitePrincipaleUniteLegale"],
        "ess": time_dependent["economieSocialeSolidaireUniteLegale"],
    }


def _get_time_dependent_info(content: dict, date_status: date = None):
    """
    Identify the time period corresponding to the input date_satus
    """
    history = content["periodesUniteLegale"]
    for past in history:
        if date_status is None:
            return past
        if date_status >= date.fromisoformat(past["dateDebut"]):
            return past
    return past
