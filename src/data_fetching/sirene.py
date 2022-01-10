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
    connector = INSEEConnector()

    response = requests.get(url, headers=connector.header())
    if response.status_code == 401:
        connector.generate_token()
        response = requests.get(url, headers=connector.header(), verify=True)

    if response.status_code == 401:
        raise RuntimeError("INSEE connection error")

    return response


def company_info(siren):
    """
    Get some data from INSEE API for the given company
    :param siren: the company's siren to search for
    """

    url = BASE_URL + f"siren/{siren}"
    response = request_insee(url)
    if response.status_code == 404:
        raise RuntimeError(response.json()["header"]["message"])
    elif response.status_code != 200:
        raise RuntimeError(f"Error fetching siren {siren} : {response.text}")

    return _parse_company_info(response.json())


def _parse_company_info(content: dict) -> dict:
    return {"siren": content["uniteLegale"]["siren"]}


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

#
# def call_sirene(company_name: str, token_key: str) -> dict:
#     """
#     Calls SIRENE API from a company name and token key
#
#     Args:
#         company_name: name of the company (exact matching)
#         token_key: Bearer authorization key
#
#     Returns:
#         json body of the SIRENE API response
#
#     Raises:
#         RuntimeError: if there is an error with the request
#
#     """
#     params = dict(q=f'periode(denominationUniteLegale:"{company_name}")')
#     headers = dict(Authorization=f"Bearer {token_key}")
#     response = requests.get(env["sirene"]["url"], params=params, headers=headers)
#     if response.ok:
#         return response.json()
#     else:
#         raise RuntimeError(f"Error calling SIRENE API: {response.json()['header']}")
#
#
# def parse_company(company_output: dict) -> Generator:
#     """
#     Parse the data about a company given the SIRENE API response
#
#     Args:
#         company_output: output of the SIRENE API call on the company
#
#     Returns:
#         generator of the pairs (key, value) with the data from SIRENE
#
#     """
#     yield "siren", company_output["siren"]
#     yield "creation_date", company_output["dateCreationUniteLegale"]
#     yield "workforce", {
#         "code": company_output["trancheEffectifsUniteLegale"],
#         "date": company_output["anneeEffectifsUniteLegale"],
#     }
#     yield "category", {
#         "code": company_output["categorieEntreprise"],
#         "date": company_output["anneeCategorieEntreprise"],
#     }  # PME/EI/GE
#     yield "activity", {
#         "code": company_output["periodesUniteLegale"][0][
#             "activitePrincipaleUniteLegale"
#         ],
#         "date": company_output["periodesUniteLegale"][0][
#             "nomenclatureActivitePrincipaleUniteLegale"
#         ],
#     }
#     yield "ess", company_output["periodesUniteLegale"][0][
#         "economieSocialeSolidaireUniteLegale"
#     ]
#
#
# def get_company_info(company_name: str, token_key: str = None) -> dict:
#     """
#     Wrapper function able to return the data of the company from its name
#
#     Args:
#         company_name: name of the company (exact matching)
#         token_key: Bearer authorization key
#
#     Returns:
#         Dictionnary of the company's data with following keys
#         - siren: SIREN of the company
#         - creation_date: creation date of the company
#         - workforce:
#             - code: INSEE code of the workforce
#             - date: date of declaration of the workforce
#             - value: value of the workforce
#         - category:
#             - code: category (PME, ...)
#             - date: date of declaration of the category
#         - activity:
#             - code: NAF code
#             - date: NAF system
#         -ess: if the company is from the ESS ecosystem
#
#     """
#     company_output = call_sirene(company_name, token_key)["unitesLegales"][0]
#     company_info = dict(parse_company(company_output))
#     company_info["workforce"]["value"] = WORKFORCE_CODE.get(
#         company_info["workforce"]["code"]
#     )
#     return company_info
