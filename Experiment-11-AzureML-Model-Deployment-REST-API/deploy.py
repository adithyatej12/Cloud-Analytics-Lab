"""Deploy the Exp 10 Pass/Fail classifier as a REST API (Experiment 11).

Azure ML SDK v1. Run from the folder containing score.py and model.pkl:

    python deploy.py

Prerequisites:
  - pip install azureml-sdk scikit-learn joblib
  - config.json downloaded from the Azure ML workspace in this folder.
    config.json is downloaded from the portal and must NOT be committed.
"""

from azureml.core import Environment, Model, Workspace
from azureml.core.conda_dependencies import CondaDependencies
from azureml.core.model import InferenceConfig
from azureml.core.webservice import AciWebservice

# Workspace: <aml-workspace> (resource group 25MCAR0141, centralindia).
# Loaded from config.json in the current folder.
ws = Workspace.from_config()

# Register the model trained in Experiment 10 (Pass/Fail classifier on
# student_performance data).
model = Model.register(
    workspace=ws,
    model_path="model.pkl",
    model_name="student-performance-passfail",
    description="Pass/Fail classifier trained on student_performance data (Exp 10).",
)

# Environment: every package score.py imports must be listed here, since the
# container image is built from this environment.
conda_deps = CondaDependencies.create(
    pip_packages=["scikit-learn", "azureml-defaults", "joblib"]
)
env = Environment(name="passfail-env")
env.python.conda_dependencies = conda_deps

# Inference config: ties the scoring script to the environment.
inference_config = InferenceConfig(entry_script="score.py", environment=env)

# ACI deployment config: 1 CPU core, 1 GB memory, key-based auth enabled.
aci_config = AciWebservice.deploy_configuration(
    cpu_cores=1, memory_gb=1, auth_enabled=True
)

service = Model.deploy(
    workspace=ws,
    name="passfail-service",
    models=[model],
    inference_config=inference_config,
    deployment_config=aci_config,
)
service.wait_for_deployment(show_output=True)

print("Deployment state:", service.state)
print("Scoring URI:", service.scoring_uri)
print(
    "NOTE: fetch the primary key from the endpoint's Consume tab in "
    "Azure ML Studio (or via the CLI) at test time. It is never hardcoded "
    "in this script or anywhere in this folder."
)
