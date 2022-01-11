import json
from datetime import date
from pathlib import Path
from unittest.mock import patch

import pytest

from src.data_fetching.sirene import BASE_URL, company_info, parse_company_info


@pytest.fixture(autouse=True)
def token_generation_mock():
    with patch("src.data_fetching.sirene.INSEEConnector.generate_token") as api_mock:
        api_mock.return_value = None
        yield api_mock


class TestINSEESiren:
    def test_error_error_unknown_company(self, requests_mock):
        with open(
            Path(__file__).parent / "fixtures" / "sirene" / "unknown_ent.json"
        ) as f:
            requests_mock.get(f"{BASE_URL}siren/2", status_code=404, json=json.load(f))
        with pytest.raises(RuntimeError) as excinfo:
            company_info(2)
        assert str(excinfo.value) == "Aucun élément trouvé pour le siren 999999998"

    def test_siret_found(self, requests_mock):
        with open(
            Path(__file__).parent / "fixtures" / "sirene" / "ent_exist.json"
        ) as f:
            requests_mock.get(
                f"{BASE_URL}siren/482755741", status_code=200, json=json.load(f)
            )

        assert company_info("482755741")["siren"] == "482755741"


class TestParseCompanyInfo:
    def test_complete_company(self):
        with open(
            Path(__file__).parent / "fixtures" / "sirene" / "ent_exist.json"
        ) as f:
            api_content = json.load(f)

        out = parse_company_info(api_content)

        assert out == {
            "siren": "482755741",
            "date_creation": date(2005, 6, 6),
            "effectifs": "32",
            "effectifs_annee": 2019,
            "ent_type": "ETI",
            "ent_type_annee": 2019,
            "forju": 5710,
            "naf": "82.91Z",
            "naf_version": "NAFRev2",
            "ess": "N",
        }

    def test_complete_company_in_the_past(self):
        with open(
            Path(__file__).parent / "fixtures" / "sirene" / "ent_exist.json"
        ) as f:
            api_content = json.load(f)

        out = parse_company_info(api_content, date(2005, 7, 1))

        assert out == {
            "siren": "482755741",
            "date_creation": date(2005, 6, 6),
            "effectifs": "32",
            "effectifs_annee": 2019,
            "ent_type": "ETI",
            "ent_type_annee": 2019,
            "forju": 5599,
            "naf": "72.3Z",
            "naf_version": "NAFRev1",
            "ess": None,
        }
