import json
import time
from pathlib import Path

import click
import pandas as pd
from cgoudetcore.learning import fit_params, init_model, pred_params
from cgoudetcore.utils import diffl, git_hash
from sklearn.metrics import roc_auc_score

from src.config import Config


@click.command()
@click.argument("model_name")
@click.option("--save", default=False, type=bool, help="Number of greetings.")
@click.option(
    "--configdir",
    default=str(Config.MODELCONFDIR),
    type=str,
    help="Directory of configuration files",
)
def main(model_name, save, configdir):
    train_model(model_name, save, Path(configdir))


def train_model(model_name: str, save: bool, configdir: Path):
    """
    Apply a pickle and prepare a submission file.
    """
    configdir = Path(configdir)
    model_name = Path(model_name).stem
    with open(configdir / f"{model_name}.json") as f:
        model_config = json.load(f)
    features = model_config["features"]
    sample_weight = model_config.get("sample_weight")
    model_config["git_hash"] = git_hash()

    fn = Config.PROCDIR / "financed_projects.parquet"
    frame = pd.read_parquet(fn)

    common_mask = ~frame[features].isnull().any(axis=1)
    scores = []
    for fold in range(5):
        metrics = {"fold": fold}

        mask_train = common_mask & (frame["valid_fold"] != fold)
        X_train = frame.loc[mask_train, features]
        y_train = frame.loc[mask_train, "target"]
        weight_train = (
            None if sample_weight is None else frame.loc[mask_train, sample_weight]
        )

        mask_valid = common_mask & (frame.valid_fold == fold)
        X_valid = frame.loc[mask_valid, features]
        y_valid = frame.loc[mask_valid, "target"]
        weight_valid = (
            None if sample_weight is None else frame.loc[mask_valid, sample_weight]
        )

        reg = init_model(model_config["model_type"], model_config.get("model_opt", {}))
        start = time.time()
        reg.fit(
            X_train,
            y_train,
            sample_weight=weight_train,
            **fit_params(
                features,
                reg,
                X_valid,
                y_valid,
                w_valid=weight_valid,
                categories=Config.CATEGORIES,
            ),
        )
        metrics["time"] = time.time() - start
        print("time", metrics["time"])
        preds_valid = reg.predict_proba(X_valid, **pred_params(reg))[:, 1]
        metrics["roc"] = roc_auc_score(y_valid, preds_valid, sample_weight=weight_valid)
        print("ROC fold{} : {}".format(fold, metrics["roc"]))
        scores.append(metrics)

    scores = pd.DataFrame(scores)
    print(scores)
    if save:
        model_config["metrics"] = scores.to_dict(orient="records")
        with open(configdir / f"{model_name}.json", "w") as f:
            json.dump(model_config, f, indent=4, sort_keys=True)
        _save_mlflow(model_config, model_name)


def _save_mlflow(model_config, model_name):
    last_metrics = model_config["metrics"][-1]
    mean_metrics = pd.DataFrame(model_config["metrics"]).mean()
    metrics_name = diffl(mean_metrics.index.values, ["fold"])
    with mlflow.start_run(run_name=model_config.get("name")):
        for c in metrics_name:
            mlflow.log_metric(c, last_metrics[c])
            mlflow.log_metric(f"{c}_mean", mean_metrics[c])
        mlflow.log_param("model", model_name)
        mlflow.log_param("params", model_config["model_opt"])
        mlflow.log_param("features", model_config["features"])
        mlflow.log_param("git_hash", git_hash())
        mlflow.set_tags(model_config.get("tags", {}))


def _perfs_to_dict(df):
    return (
        df.describe()
        .loc[["mean", "std"]]
        .reset_index()
        .rename(columns={"index": "agg"})
        .melt(id_vars=["agg"])
        .to_dict(orient="records")
    )


if __name__ == "__main__":
    main()
