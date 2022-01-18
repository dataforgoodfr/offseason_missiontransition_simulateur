import tempfile
from pathlib import Path

import pandas as pd

from src.data_fetching.ademe import process_ademe


def test_process_ademe():
    fn = Path(__file__).parent / "fixtures" / "test_ademe.xlsx"
    with tempfile.TemporaryDirectory() as tmpdirname:
        outfn = Path(tmpdirname) / "test_ademe.parquet"
        process_ademe(fn, outfn)
        out = pd.read_parquet(outfn)

    assert len(out) == 1
    exp = {
        "date_convention": pd.Timestamp("2021-04-30 00:00:00"),
        "denomination": "LACTEUS",
        "montant": 5000,
        "nature": "aide en numéraire",
        "project": "TREMPLIN pour la transition écologique des PME",
        "siren": 499725562,
        "siret": 49972556200023,
    }
    assert out.to_dict(orient="records")[0] == exp
