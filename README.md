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
```

For production run :
```
pip install -r requirements/base.txt
pre-commit install
```

You will need the `env.yml` file at the root of the project, containing API url and keys, ask the team for that.
