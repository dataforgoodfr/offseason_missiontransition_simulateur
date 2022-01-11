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
    return out


def _list_names(content: dict, key: str) -> list:
    return [d["name"] for d in content[key]]
