# offseason_missiontransition_simulateur

## Setting up

Create and activate a virtual environment.
```
virtualenv venv -p python3.9
. venv/bin/activate
```

Install the required libraries.
For development purposes, run :
```
pip install -r requirements/dev.txt
pre-commit install
jupyter nbextension install https://github.com/drillan/jupyter-black/archive/master.zip --user
jupyter nbextension enable jupyter-black-master/jupyter-black
python -m spacy download fr_core_news_sm
```

For production run :
```
pip install -r requirements/base.txt
python -m spacy download fr_core_news_sm
```

Create a `.env` text file at the root of the repository to store secret environment variables.

- `INSEE_KEY` : secret key for the insee api.
- `INSEE_SECRET` : secret password for the insee api

## Data pipeline

To run the complete data pipeline steps :

```
python -m src.data_fetching.ademe
python -m src.data_fetching.mission_transition
python -m src.data_processing.matching_ademe_mt
```
