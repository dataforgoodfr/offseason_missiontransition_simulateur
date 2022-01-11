import json
from pathlib import Path

from src.data_fetching.mission_transition import parse_project


class TestParseAPIContent:
    def test_parse_standard_mission(self):
        with open(
            Path(__file__).parent / "fixtures" / "mission_transition" / "project.json"
        ) as f:
            inp = json.load(f)

        out = parse_project(inp)

        assert out == {
            "source": "at_94683",
            "name": "Financer les études et tests préalables aux investissements servant à incorporer des matières premières issues du recyclage",
            "perimeter": "NATIONAL",
            "details": "<p>\n <strong>\n  Aide - « Études et tests préalables aux investissements pour incorporer des matières premières issues du recyclage », mis en place par l'ADEME\n </strong>\n</p>\n<p>\n Objectif : vous souhaitez étudier ou tester une unité de production intégrant des Matières premières de recyclage (MPR), ou alors adapter une unité existante ? L'ADEME peut vous aider à financer les études et les tests nécessaires à l'expérimentation.\n</p>\n<p>\n Bénéficiaires :\r\nEntreprises de production susceptibles d'utiliser des MPR dans les secteurs de des métaux, du textile, du bâtiment, de l'industrie du papier-carton, du bois...\n <br/>\n <br/>\n Accompagnement : subvention. Taux d'aide maximum : 70 % des dépenses éligibles.\n <br/>\n</p>",
            "eligibility": "<p>\n Critères d'éligibilité\n <br/>\n</p>\n<ul>\n <li>\n  Pertinence du projet vis-à-vis de la filière pour la matière étudiée,\n  <br/>\n </li>\n <li>\n  Pertinence du projet sur le territoire\n  <br/>\n </li>\n <li>\n  Choix du process : caractéristiques et performances,\n  <br/>\n </li>\n <li>\n  Sécurité d'approvisionnement à partir de l'étude des gisements de MPR mobilisables,\n  <br/>\n </li>\n <li>\n  Pérennité des débouchés des flux produits,\n  <br/>\n </li>\n <li>\n  Coûts d'investissement et de fonctionnement,\n  <br/>\n </li>\n <li>\n  Impacts environnementaux et impacts en terme d'emplois,\n  <br/>\n </li>\n <li>\n  Part de MPR incorporée en remplacement de matière vierge.\n  <br/>\n </li>\n</ul>",
            "url": "https://agirpourlatransition.ademe.fr/entreprises/dispositif-aide/etudes-tests-prealables-investissements-incorporer-matieres-premieres-issues",
            "application_end_date": None,
            "funding_types": ["Subvention"],
            "regions": ["France"],
            "subvention_rate_upper_bound": 70,
            "subvention_rate_lower_bound": None,
            "loan": None,
            "start_date": "2021-11-09T15:42:42+00:00",
            "aid_types": ["Aide financière"],
            "aid_id": 189,
            "funder_name": "ADEME",
            "topics": ["Incorporation de produits recyclés"],
        }
