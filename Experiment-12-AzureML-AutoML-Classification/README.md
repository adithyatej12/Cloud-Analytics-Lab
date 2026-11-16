# Experiment 12: Use Azure AutoML to train and evaluate a classification model automatically.

**Course:** Cloud Analytics (25MCAR0141)
**Course Outcome:** CO3
**Target document:** CA_Exp12_AutoML.pdf (also in this folder)

## Aim

To use Azure Automated Machine Learning (AutoML) to automatically train, compare, and evaluate classification models on student performance data, and to identify the best model for predicting whether a student passes or fails — without manually selecting the algorithm or tuning its hyperparameters.

## Objectives

- Create an Azure Machine Learning workspace in the lab resource group.
- Prepare and upload the student performance dataset with `result` (Pass/Fail) as the label column.
- Configure an AutoML classification run with accuracy as the primary metric.
- Submit the AutoML experiment and monitor the candidate models in Azure ML Studio.
- Inspect the best model chosen by AutoML and its evaluation metrics.
- Evaluate the best model on a held-out split and register it in the workspace.

## Architecture

```text
Student performance data (student_performance, result = Pass/Fail)
        |  Upload to workspace datastore
        v
Azure ML workspace (<aml-workspace>)
        |  AutoML run (automl_run.py)
        v
Candidate models (AutoML tries several algorithms)
        |  Ranked by accuracy (3-fold cross-validation)
        v
Best model (highest accuracy)
        |  Evaluate on held-out split
        v
Evaluation (accuracy, confusion matrix, classification report)
        |
        v
Registered model (best model, ready for deployment)
```

AutoML does the model selection work: it tries a range of classification algorithms and preprocessing steps, ranks them by accuracy, and returns the best run — the experimenter only defines the task, the label, and the time budget.

## Architecture & Component Roles

| Component | Resource Name | Role / Description |
|---|---|---|
| Resource Group | 25MCAR0141 | Logical container for all Azure experiment resources |
| Azure ML Workspace | <aml-workspace> | Central workspace for the AutoML experiment, datasets, and registered models |
| Compute Target | <compute-target> | Compute used to train the AutoML candidate models |
| Dataset | student_performance | Training data; `result` (Pass/Fail) is the label column |
| AutoML Run | automl-classification | Automated experiment that trains and ranks candidate classification models |
| Registered Model | best model from the run | The winning model, registered in the workspace for later use |

## Services Used

- Azure Machine Learning (AutoML)
- Azure Machine Learning Studio (monitoring and model inspection)
- Azure Portal
- Python (Azure ML SDK v1, scikit-learn)

## Procedure

### Step 1 — Create the Azure ML Workspace

Azure Portal → Machine Learning → Create → workspace name `<aml-workspace>` in resource group `25MCAR0141`, region centralindia. Review + Create, then open the workspace.

### Step 2 — Prepare the Dataset

Use the student performance data from the earlier experiments (Experiment 6's cleaned output carries `performance_band` and `result`, where `result` is Pass when the average score is 40 or above, otherwise Fail). Confirm the file has a `result` column with Pass/Fail values and no missing label values.

### Step 3 — Upload the Dataset

In Azure ML Studio → Data → Datasets → Create dataset from local files (or register the file already stored in the workspace datastore). Note the datastore path — it goes into the `DATASTORE_PATH` placeholder in `automl_run.py`.

### Step 4 — Download config.json

In Azure ML Studio, open the workspace overview and download `config.json` into the folder where you will run the script. This file identifies the workspace — do NOT commit it to GitHub (see the comment in `automl_run.py`).

### Step 5 — Set Up the Compute Target

In Azure ML Studio → Compute → create or select a compute target for training. Note its name — it goes into the `<compute-target>` placeholder in `automl_run.py`.

### Step 6 — Configure the Script

Open `automl_run.py` (in this folder) and fill in the two placeholders: the datastore path of the uploaded dataset and the compute target name. Check that `label_column_name` is `"result"` and `primary_metric` is `"accuracy"`.

### Step 7 — Install the SDK and Run

Install the SDK locally (`pip install azureml-sdk scikit-learn pandas`) and run the script:

```text
python automl_run.py
```

The script submits the AutoML experiment, waits for it to finish, then prints the best run, evaluates the best model on the held-out split, and registers it.

### Step 8 — Monitor Candidate Models

While the run is in progress, open Azure ML Studio → Experiments → the AutoML run → Models tab. Watch the candidate models appear, each with its accuracy, algorithm, and run status, ranked best first.

### Step 9 — Inspect the Best Model

When the run completes, open the top-ranked model in Studio. Check its algorithm, its accuracy, and the metrics and charts AutoML recorded for it. Record the observed values — do not copy numbers from any example.

### Step 10 — Evaluate on the Held-Out Split

The script evaluates the best model on the held-out split and prints the accuracy, confusion matrix, and classification report. Compare these with the cross-validated accuracy shown in Studio.

### Step 11 — Verify the Registered Model

In Azure ML Studio → Models, confirm the best model is registered with the name given in the script.

### Step 12 — Stop the Compute

Stop or delete the compute target when the experiment is finished, so it does not keep running.

## Code Highlights

Full script: [`automl_run.py`](automl_run.py)

**Connect to the workspace:**

```python
ws = Workspace.from_config()
# config.json is downloaded from the Azure portal and must NOT be committed.
```

**Load the training data:**

```python
training_data = TabularDatasetFactory.from_delimited_files(
    path=[(datastore, DATASTORE_PATH)]
)
# Local fallback (commented out in the script): read the CSV with pandas
# and build the dataset from the dataframe instead.
```

**Configure the AutoML run:**

```python
automl_config = AutoMLConfig(
    task="classification",
    primary_metric="accuracy",
    label_column_name="result",
    training_data=training_data,
    compute_target=compute_target,
    experiment_timeout_minutes=30,
    enable_early_stopping=True,
    featurization="auto",
    n_cross_validations=3,
)
```

The 30-minute timeout caps the experiment, early stopping ends it once further models stop improving, and 3-fold cross-validation gives each candidate a fair accuracy score.

**Submit, wait, and take the best model:**

```python
experiment = Experiment(ws, "automl-classification")
run = experiment.submit(automl_config)
run.wait_for_completion(show_output=True)
best_run, best_model = run.get_best_child()
```

**Evaluate on the held-out split:**

```python
accuracy = accuracy_score(y_test, y_pred)
confusion_matrix(y_test, y_pred)
classification_report(y_test, y_pred)
```

All three are computed at run time from the actual run — no metric value is hardcoded in the script.

**Register the best model:**

```python
best_model.register(ws, name="student-result-classifier")
```

## Screenshot Checklist

| # | Screenshot | Filename |
|---|---|---|
| 1 | Azure Portal — ML workspace <aml-workspace> overview (resource group 25MCAR0141, centralindia) | Step_01_ML_Workspace_Overview.png |
| 2 | Azure ML Studio — dataset registered (student_performance, result column visible) | Step_02_Dataset_Registered.png |
| 3 | Compute target created / selected for training | Step_03_Compute_Target.png |
| 4 | Terminal — automl_run.py submitted, experiment running | Step_04_AutoML_Run_Submitted.png |
| 5 | Azure ML Studio — Experiments list showing the AutoML run | Step_05_Experiments_List.png |
| 6 | Models tab — candidate models ranked by accuracy | Step_06_Candidate_Models_Ranked.png |
| 7 | Best model details — algorithm and metrics | Step_07_Best_Model_Details.png |
| 8 | Terminal — held-out evaluation output (accuracy, confusion matrix, classification report) | Step_08_Held_Out_Evaluation.png |
| 9 | Azure ML Studio — Models list showing the registered best model | Step_09_Registered_Model.png |
| 10 | Compute stopped after the experiment | Step_10_Compute_Stopped.png |

Note: screenshots are not in this folder yet — add them under `screenshots/` using the filenames above. Do not include a screenshot that shows a key, token, or other credential.

## Result

A successful run demonstrates automated classification end to end: the student performance dataset was uploaded with `result` (Pass/Fail) as the label, AutoML trained and ranked several candidate classification models by accuracy, the best model was identified in Azure ML Studio, evaluated on a held-out split (accuracy, confusion matrix, and classification report printed by the script), and registered in the workspace.

Record the observed values from the actual run here:

- Best algorithm: record the observed value here.
- Best cross-validated accuracy: record the observed value here.
- Held-out accuracy: record the observed value here.
- Confusion matrix and classification report: record the observed values here.

## Key Learning

This experiment demonstrates automated machine learning on Azure: AutoML takes over algorithm selection, preprocessing, and hyperparameter tuning, ranks candidate models by a chosen metric, and returns the best one — the experimenter defines the task and the label, monitors the run, and validates the winner on held-out data before registering it for use.
