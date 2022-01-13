import json
from datetime import date
from pathlib import Path
from unittest.mock import patch

import pytest

from src.data_fetching.sirene import BASE_URL, etab_info, parse_etab_info


@pytest.fixture(autouse=True)
def token_generation_mock():
    with patch("src.data_fetching.sirene.INSEEConnector.generate_token") as api_mock:
        api_mock.return_value = None
        yield api_mock


class TestINSEESiren:
    def test_error_unknown_company(self, requests_mock):
        with open(
            Path(__file__).parent / "fixtures" / "sirene" / "unknown_ent.json"
        ) as f:
            requests_mock.get(
                f"{BASE_URL}siret/00000000000002", status_code=404, json=json.load(f)
            )
        with pytest.raises(RuntimeError) as excinfo:
            etab_info(2)
        assert str(excinfo.value) == "Aucun élément trouvé pour le siren 999999998"

    def test_error_non_diffusable(self, requests_mock):
        requests_mock.get(
            f"{BASE_URL}siret/00000000000003",
            status_code=404,
            json={
                "header": {
                    "statut": 403,
                    "message": "Établissement non diffusable (51456080400023)",
                }
            },
        )
        with pytest.raises(RuntimeError) as excinfo:
            etab_info(3)
        assert str(excinfo.value) == "Établissement non diffusable (51456080400023)"

    def test_siret_found(self, requests_mock):
        with open(
            Path(__file__).parent / "fixtures" / "sirene" / "site_exist.json"
        ) as f:
            requests_mock.get(
                f"{BASE_URL}siret/20000982700037", status_code=200, json=json.load(f)
            )

        assert etab_info("20000982700037")["siret"] == "20000982700037"


class TestParseEtabInfo:
    def test_complete_siret(self):
        with open(
            Path(__file__).parent / "fixtures" / "sirene" / "site_exist.json"
        ) as f:
            api_content = json.load(f)

        out = parse_etab_info(api_content)

        assert out == {
            "siren": "200009827",
            "date_creation": date(2007, 7, 13),
            "effectifs": "22",
            "effectifs_annee": "2019",
            "ent_type": "PME",
            "ent_type_annee": "2019",
            "forju": 7354,
            "naf": "38.21Z",
            "naf_version": "NAFRev2",
            "ess": None,
            "adr_code_commune": "2B096",
            "adr_code_etranger": None,
            "adr_code_postal": "20250",
            "adr_commune": "CORTE",
            "adr_lib_voie": "VC ZONE ARTISANALE",
            "adr_num_voie": None,
            "adr_type_voie": None,
            "denomination": "SYNDICAT MIXTE POUR LA VALORISATION DES DECHETS DE CORSE",
            "dt_crea_etab": date(2018, 1, 15),
            "effectifs_etab": "22",
            "etab_siege": True,
            "naf_etab": "38.21Z",
            "naf_version_etab": "NAFRev2",
            "siret": "20000982700037",
        }
