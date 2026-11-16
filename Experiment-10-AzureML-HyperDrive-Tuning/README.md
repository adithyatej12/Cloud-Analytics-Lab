# Experiment 10: Optimize a machine learning model by tuning hyperparameters using Azure ML HyperDrive

**Course:** Cloud Analytics (25MCAR0141)
**Course Outcome:** CO3
**Target document:** CA_Exp10_HyperDrive.pdf (also in this folder)

## Aim

To optimize a machine learning model by tuning its hyperparameters using Azure Machine Learning HyperDrive, sweeping a Random Forest classifier over several hyperparameter combinations and selecting the best-performing run on student performance data.

## Objectives

- Create an Azure Machine Learning workspace in resource group `25MCAR0141` (centralindia).
- Create a CPU compute target for running training jobs.
- Prepare student performance data (`student_performance.csv`) as the training input.
- Write a parameterized training script (`train.py`) that logs accuracy to Azure ML.
- Configure a HyperDrive sweep (`hyperdrive_run.py`) with random parameter sampling.
- Apply a Bandit early-termination policy to stop poorly performing runs.
- Inspect all child runs in Azure ML Studio and identify the best model by accuracy.

## Architecture

```text
Student data (student_performance.csv)
        |  Upload to workspace / datastore
        v
Azure ML Workspace (<aml-workspace>)
        |  HyperDrive sweep (RandomParameterSampling)
        v
CPU Compute Target (<compute-target>)
        |  12 training runs of train.py
        |  (RandomForestClassifier, varying
        |   n_estimators / max_depth / min_samples_split)
        v
HyperDrive Experiment
        |  Primary metric: accuracy (maximize)
        |  BanditPolicy prunes weak runs early
        v
Best Run -> Best Model (outputs/model.pkl)
```

HyperDrive is the tuner: it does not train the model itself — it launches many runs of `train.py`, each with a different hyperparameter combination, watches the logged accuracy of each run, and ranks them so the best combination can be picked out.

## Architecture & Component Roles

| Component | Resource Name | Role / Description |
|---|---|---|
| Resource Group | 25MCAR0141 | Logical container for all Azure experiment resources |
| ML Workspace | `<aml-workspace>` | Azure ML workspace holding experiments, runs, models, and compute |
| Compute Target | `<compute-target>` | CPU compute cluster that runs the training jobs |
| Training Script | train.py | Trains a RandomForestClassifier and logs accuracy per run |
| HyperDrive Script | hyperdrive_run.py | Defines the parameter sweep, sampling, and early-termination policy |
| Dataset | student_performance.csv | Student score data; target column `result` (Pass/Fail) |
| Experiment | hyperdrive-student-performance | HyperDrive experiment grouping all sweep runs |

## Services Used

- Azure Machine Learning (HyperDrive, Experiments, Compute)
- Azure Machine Learning Studio
- Azure Portal

## Procedure

### Step 1 — Create an Azure ML Workspace

Azure Portal → Machine Learning → Create → resource group `25MCAR0141`, region centralindia, workspace name `<aml-workspace>`.

### Step 2 — Download the Workspace config.json

In Azure ML Studio → workspace settings → Download config.json. Place it next to `hyperdrive_run.py` so `Workspace.from_config()` can find it. Do NOT commit config.json to GitHub — it identifies the workspace and belongs only on the local machine.

### Step 3 — Create a CPU Compute Target

Azure ML Studio → Compute → Compute clusters → + New → name `<compute-target>`, CPU VM size, minimum 0 nodes, maximum 4 nodes (enough for `max_concurrent_runs=4`).

### Step 4 — Upload the Data

Upload `student_performance.csv` to the workspace datastore (or keep it in the run's source directory). The file carries the score columns and the `result` column (Pass/Fail) produced by the Experiment 6 cleaning step (`performance_band` + `result`).

### Step 5 — Review the Training Script

Open `train.py` (in this folder). It takes `--n_estimators`, `--max_depth`, and `--min_samples_split` as arguments, trains a RandomForestClassifier to predict `result` from the score columns, logs accuracy with `run.log("accuracy", ...)`, and saves the model to `outputs/model.pkl`.

### Step 6 — Review the HyperDrive Script

Open `hyperdrive_run.py` (in this folder). It uses RandomParameterSampling over the three hyperparameters, sets accuracy as the primary metric to maximize, allows 12 total runs with 4 running concurrently, and applies a BanditPolicy to terminate runs that fall behind.

### Step 7 — Install the Azure ML SDK (v1)

Locally (or in the compute environment) install the SDK v1 packages the scripts need:

```bash
pip install azureml-core azureml-sdk scikit-learn joblib pandas
```

### Step 8 — Run the HyperDrive Sweep

From this folder, with `config.json` alongside the scripts, run:

```bash
python hyperdrive_run.py
```

### Step 9 — Monitor the Runs

Azure ML Studio → Experiments → `hyperdrive-student-performance` → watch the child runs as they queue, run, and complete (or get terminated early by the Bandit policy).

### Step 10 — Inspect the Best Run

When the sweep finishes, open the run ranked first by accuracy. Check its logged metrics and the hyperparameters it used (printed by `hyperdrive_run.py` on completion and visible in the run details in Studio).

### Step 11 — Record the Best Model

Note the best run's accuracy and hyperparameters in the Result section below (record the observed value here — do not copy values from any other run). The best run's `outputs/model.pkl` is the tuned model.

### Step 12 — Stop / Scale Down Compute

Scale the compute cluster back to 0 nodes (or delete it) when the sweep is done, to save cost.

## Code Highlights

### Training Script — Parameterized Random Forest

Full script: [`train.py`](train.py)

```python
parser.add_argument("--n_estimators", type=int, default=100)
parser.add_argument("--max_depth", type=int, default=None)
parser.add_argument("--min_samples_split", type=int, default=2)
```

HyperDrive passes a different value for each of these arguments on every child run, so the same script trains a different model each time. The target is the `result` column (Pass/Fail) and the features are the score columns:

```python
X = df[score_cols]
y = df["result"]
clf = RandomForestClassifier(
    n_estimators=args.n_estimators,
    max_depth=args.max_depth,
    min_samples_split=args.min_samples_split,
    random_state=42,
)
```

Accuracy is logged to the Azure ML run so HyperDrive can rank the runs — with a plain-print fallback so the script also runs standalone outside Azure ML:

```python
try:
    run = Run.get_context()
    run.log("accuracy", accuracy)
except Exception:
    print(f"accuracy: {accuracy}")
```

The trained model is saved to `outputs/model.pkl`, which Azure ML automatically uploads as a run artifact:

```python
os.makedirs("outputs", exist_ok=True)
joblib.dump(clf, "outputs/model.pkl")
```

### HyperDrive Script — Random Sampling + Bandit Policy

Full script: [`hyperdrive_run.py`](hyperdrive_run.py)

```python
param_sampling = RandomParameterSampling(
    {
        "n_estimators": choice(50, 100, 200),
        "max_depth": choice(5, 10, 20, None),
        "min_samples_split": choice(2, 5, 10),
    }
)
```

Random sampling picks a different combination for each of the 12 runs instead of trying every combination on a grid, which covers the space well at a fraction of the cost:

```python
hd_config = HyperDriveConfig(
    run_config=script_run_config,
    hyperparameter_sampling=param_sampling,
    policy=BanditPolicy(slack_factor=0.1, evaluation_interval=1, delay_evaluation=3),
    primary_metric_name="accuracy",
    primary_metric_goal=PrimaryMetricGoal.MAXIMIZE,
    max_total_runs=12,
    max_concurrent_runs=4,
)
```

The Bandit policy terminates a run once it is clearly behind the best run so far (after a short delay, so every run gets a fair start), freeing compute for the remaining runs. On completion the script prints the best run's metrics and hyperparameters — the values come from the actual run, not from any preset expectation.

## Screenshot Checklist

| # | Screenshot | Filename |
|---|---|---|
| 1 | Azure Portal — ML workspace `<aml-workspace>` overview | Step_01_ML_Workspace_Overview.png |
| 2 | Azure ML Studio — Compute cluster `<compute-target>` created | Step_02_Compute_Target_Created.png |
| 3 | Datastore / data upload — student_performance.csv in the workspace | Step_03_Data_Uploaded.png |
| 4 | Terminal — `python hyperdrive_run.py` submitted (experiment link shown) | Step_04_HyperDrive_Submitted.png |
| 5 | Azure ML Studio — Experiment runs list (child runs queued/running) | Step_05_Experiment_Runs_List.png |
| 6 | Child run details — hyperparameters and logged accuracy | Step_06_Child_Run_Details.png |
| 7 | HyperDrive run list — runs ranked by accuracy | Step_07_Runs_Ranked_By_Accuracy.png |
| 8 | Best run — metrics and hyperparameters | Step_08_Best_Run_Metrics.png |
| 9 | Bandit policy — a run terminated early (if one was pruned) | Step_09_Bandit_Early_Termination.png |
| 10 | Best run outputs — outputs/model.pkl artifact | Step_10_Best_Model_Artifact.png |

Note: screenshots are not in this folder yet — add them under `screenshots/` using the filenames above. Do not include a screenshot that shows a subscription ID, workspace ID, key, token, or other credential.

## Result

The HyperDrive sweep ran to completion: 12 Random Forest training runs were launched on the CPU compute target, each with a different hyperparameter combination sampled at random, and each run logged its accuracy to Azure ML Studio. Runs that fell behind were pruned early by the Bandit policy, and the remaining runs were ranked by accuracy so the best hyperparameter combination could be identified. The best run's model was saved as `outputs/model.pkl`.

Best run (record the observed value here): accuracy — record the observed value here; hyperparameters (n_estimators, max_depth, min_samples_split) — record the observed value here.

## Key Learning

This experiment demonstrates automated hyperparameter tuning on Azure: a parameterized training script that logs a single comparable metric, a HyperDrive sweep that explores the hyperparameter space with random sampling instead of an exhaustive grid, and a Bandit early-termination policy that spends compute on the promising runs and stops the weak ones early — so the best model is found faster and cheaper than tuning by hand.
