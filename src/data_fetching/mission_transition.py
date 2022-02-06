import json
import logging

import pandas as pd
import requests
from sklearn.preprocessing import MultiLabelBinarizer

from src.config import Config

logger = logging.getLogger(__name__)


def save_mission_transition_projects():
    url = "https://mission-transition-ecologique.beta.gouv.fr/api/temp/aids"
    r = requests.get(url)
    if r.status_code != 200:
        raise RuntimeError(f"API error : {r.content}")
    with open(Config.RAWDIR / "mission_transition.json", "w") as f:
        json.dump(r.json(), f)


def process_mission_transition():
    with open(Config.RAWDIR / "mission_transition.json") as f:
        raw = json.load(f)
    raw = pd.DataFrame.from_records([parse_project(project) for project in raw]).pipe(
        _process_topic
    )
    assert raw["source"].nunique() == len(raw)
    logger.info(
        "mission_transition", extra=dict(columns=sorted(raw.columns), shape=raw.shape)
    )

    raw.to_parquet(Config.INTDIR / "mission_transition.parquet")


def parse_project(api_content: dict) -> dict:
    as_is = {
        "sourceId": "source",
        "name": None,
        "perimeter": None,
        "aidDetails": "details",
        "eligibility": None,
        "fundingSourceUrl": "url",
        "applicationEndDate": "application_end_date",
        "fundingTypes": "funding_types",
        "subventionRateUpperBound": "subvention_rate_upper_bound",
        "subventionRateLowerBound": "subvention_rate_lower_bound",
        "loanAmount": "loan",
        "applicationStartDate": "start_date",
        "id": "aid_id",
    }
    out = {v or k: api_content[k] for k, v in as_is.items()}
    out["funder_name"] = api_content["funder"]["name"]
    out["topics"] = _list_names(api_content, "environmentalTopics")
    out["aid_types"] = _list_names(api_content, "types")
    out["regions"] = _list_names(api_content, "regions")
    out["source"] = int(out["source"][3:])
    return out


def _process_topic(df: pd.DataFrame) -> pd.DataFrame:
    mlb = MultiLabelBinarizer()
    features = pd.DataFrame(
        mlb.fit_transform(df["topics"]),
        columns=["topic_" + x for x in mlb.classes_],
        index=df.index,
    )
    return pd.concat([df.drop(columns=["topics"]), features], axis=1)


def _list_names(content: dict, key: str) -> list:
    return [d["name"] for d in content[key]]


if __name__ == "__main__":
    if not (Config.RAWDIR / "mission_transition.json").exists():
        save_mission_transition_projects()
    process_mission_transition()
