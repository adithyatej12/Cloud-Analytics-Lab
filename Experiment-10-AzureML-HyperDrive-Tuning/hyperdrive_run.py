"""Submit an Azure ML HyperDrive sweep to tune the Random Forest in train.py.

Azure ML SDK v1 style (azureml-core). The sweep samples 12 hyperparameter
combinations at random, runs up to 4 concurrently on a CPU compute target,
and prunes weak runs early with a Bandit policy. Accuracy is the primary
metric (higher is better).

Setup:
    1. Download config.json from the Azure ML workspace in the portal
       (Azure ML Studio -> workspace settings -> Download config.json)
       and place it next to this script. Do NOT commit config.json to
       GitHub -- it identifies the workspace and belongs only on the
       local machine.
    2. Replace the <compute-target> placeholder below with the name of
       the CPU compute cluster created in the workspace.
    3. Install the SDK v1 packages:
           pip install azureml-core azureml-sdk scikit-learn joblib pandas

Usage:
    python hyperdrive_run.py

On completion the script prints the best run's accuracy and the
hyperparameter values it used. Those values come from the actual run --
nothing is hardcoded here.
"""

from azureml.core import Experiment, ScriptRunConfig, Workspace
from azureml.train.hyperdrive import (
    BanditPolicy,
    HyperDriveConfig,
    PrimaryMetricGoal,
    RandomParameterSampling,
    choice,
)

# Name of the CPU compute target in the workspace.
# Replace with the actual compute cluster name created in Azure ML Studio.
COMPUTE_TARGET = "<compute-target>"

EXPERIMENT_NAME = "hyperdrive-student-performance"


def main():
    # Load the workspace from config.json in the current directory.
    # (config.json is downloaded from the Azure ML workspace in the portal
    # and must NOT be committed to the repo.)
    ws = Workspace.from_config()

    # Run train.py on the compute target. The --data argument points at the
    # student performance CSV; the hyperparameters are filled in per run by
    # HyperDrive, so they are not set here.
    script_run_config = ScriptRunConfig(
        source_directory=".",
        script="train.py",
        arguments=["--data", "student_performance.csv"],
        compute_target=COMPUTE_TARGET,
    )

    # Randomly sample one combination per run from these choices.
    param_sampling = RandomParameterSampling(
        {
            "n_estimators": choice(50, 100, 200),
            "max_depth": choice(5, 10, 20, None),
            "min_samples_split": choice(2, 5, 10),
        }
    )

    # Stop runs that fall behind the best run so far: a run is terminated
    # once its accuracy is more than 10% below the best (slack_factor),
    # checked every run interval after the first 3 runs have reported.
    early_termination_policy = BanditPolicy(
        slack_factor=0.1, evaluation_interval=1, delay_evaluation=3
    )

    hd_config = HyperDriveConfig(
        run_config=script_run_config,
        hyperparameter_sampling=param_sampling,
        policy=early_termination_policy,
        primary_metric_name="accuracy",
        primary_metric_goal=PrimaryMetricGoal.MAXIMIZE,
        max_total_runs=12,
        max_concurrent_runs=4,
    )

    experiment = Experiment(workspace=ws, name=EXPERIMENT_NAME)
    hd_run = experiment.submit(hd_config)
    print(f"HyperDrive run submitted: {hd_run.id}")
    print("Monitor progress in Azure ML Studio under Experiments -> "
          f"{EXPERIMENT_NAME}")

    # Wait for the sweep to finish (all runs complete or terminated).
    hd_run.wait_for_completion(show_output=True)

    # Report the best run. Values come from the run itself.
    best_run = hd_run.get_best_run_by_primary_metric()
    print(f"Best run ID: {best_run.id}")
    print(f"Best run metrics: {best_run.get_metrics()}")
    print("Best run hyperparameters:")
    for name, value in best_run.get_details()["runDefinition"]["arguments"]:
        print(f"  {name}: {value}")


if __name__ == "__main__":
    main()
