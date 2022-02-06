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
```

For production run :
```
pip install -r requirements/base.txt
pre-commit install
```

Create a `.env` text file at the root of the repository to store secret environment variables.

- `INSEE_KEY` : secret key for the insee api.
- `INSEE_SECRET` : secret password for the insee api
- `NEPTUNE_API_TOKEN` : api token of neptune data science platform

## Data pipeline

To run the complete data pipeline steps :

```
python -m src.data_fetching.ademe
python -m src.data_fetching.mission_transition

# the following takes more than one hour.
# you can ask contributors for a pre-filled sqlite file.
python -m src.data_fetching.sirene

python -m src.data_processing.matching_ademe_mt
python -m src.data_processing.join_sources
python -m src.data_processing.augment
python -m src.data_processing.final_features
```

## Modelisation

To train a recommandation model :

```
python -m src.models.train_reco <config_name_without_extension> --save <0_or_1>
```

## Documentation

A sphinx documentation is available under the `docs/` directory.
First compile the documentation.

```
cd docs
make html
```

Then open the file `docs/build/html/index.html` with your browser.
