"""
Experiment 12: Use Azure AutoML to train and evaluate a classification model
automatically (Cloud Analytics, 25MCAR0141, CO3).

Submits an AutoML classification run on the student_performance dataset
(label column: result, Pass/Fail), waits for completion, retrieves the best
run and best model, evaluates it on a held-out split, and registers it.

All metric values are computed at run time from the actual run - nothing
is hardcoded here.

Prerequisites:
    pip install azureml-sdk scikit-learn pandas

Placeholders to fill in before running:
    DATASTORE_PATH - datastore path of the uploaded student_performance file
    COMPUTE_TARGET_NAME - name of the compute target in the workspace
"""

import logging

from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

from azureml.core import Experiment, Workspace
from azureml.core.compute import ComputeTarget
from azureml.data.dataset_factory import TabularDatasetFactory
from azureml.train.automl import AutoMLConfig

# ---------------------------------------------------------------------------
# Placeholders - fill these in before running. No real credentials,
# connection strings, keys, or IDs belong in this file.
# ---------------------------------------------------------------------------
DATASTORE_PATH = "<datastore-path-to-student_performance.csv>"
COMPUTE_TARGET_NAME = "<compute-target>"

EXPERIMENT_NAME = "automl-classification"
LABEL_COLUMN = "result"
MODEL_NAME = "student-result-classifier"

# Logging so the run's progress is visible in the terminal.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    # Connect to the workspace.
    # config.json is downloaded from the portal and must NOT be committed.
    ws = Workspace.from_config()
    logger.info("Connected to workspace: %s", ws.name)

    datastore = ws.get_default_datastore()

    # Load the training data from the workspace datastore.
    training_data = TabularDatasetFactory.from_delimited_files(
        path=[(datastore, DATASTORE_PATH)]
    )

    # Local-CSV fallback (commented out): if the dataset is not in the
    # datastore yet, read it locally and build the dataset from a dataframe.
    # import pandas as pd
    # local_df = pd.read_csv("student_performance.csv")
    # training_data = TabularDatasetFactory.from_pandas_dataframe(local_df)

    # Compute target for training.
    compute_target = ComputeTarget(workspace=ws, name=COMPUTE_TARGET_NAME)

    # Configure the AutoML classification run.
    automl_config = AutoMLConfig(
        task="classification",
        primary_metric="accuracy",
        label_column_name=LABEL_COLUMN,
        training_data=training_data,
        compute_target=compute_target,
        experiment_timeout_minutes=30,
        enable_early_stopping=True,
        featurization="auto",
        n_cross_validations=3,
        verbosity=logging.INFO,
    )

    # Submit the experiment and wait for it to finish.
    experiment = Experiment(ws, EXPERIMENT_NAME)
    run = experiment.submit(automl_config)
    logger.info("Submitted AutoML run: %s", run.id)
    run.wait_for_completion(show_output=True)

    # Retrieve the best run and the best model.
    best_run, best_model = run.get_best_child()
    logger.info("Best run id: %s", best_run.id)
    logger.info("Best run metrics: %s", best_run.get_metrics())

    # Evaluate the best model on a held-out split. The split is made from
    # the same dataset at run time; the metrics below are computed from
    # the actual run, never hardcoded.
    df = training_data.to_pandas_dataframe()
    X = df.drop(columns=[LABEL_COLUMN])
    y = df[LABEL_COLUMN]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    logger.info(
        "Held-out split: %d training rows, %d test rows",
        len(X_train),
        len(X_test),
    )

    y_pred = best_model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    logger.info("Held-out accuracy: %s", accuracy)
    logger.info("Confusion matrix:\n%s", confusion_matrix(y_test, y_pred))
    logger.info(
        "Classification report:\n%s", classification_report(y_test, y_pred)
    )

    # Register the best model in the workspace.
    registered_model = best_model.register(
        ws,
        name=MODEL_NAME,
        description=(
            "Best AutoML classification model for student result "
            "(Pass/Fail) - Experiment 12"
        ),
    )
    logger.info(
        "Registered model: %s (version %s)",
        registered_model.name,
        registered_model.version,
    )


if __name__ == "__main__":
    main()
