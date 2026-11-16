# Experiment 11: Deploy a trained machine learning model as a REST API for real-world use.

**Course:** Cloud Analytics (25MCAR0141)
**Course Outcome:** CO3
**Target document:** CA_Exp11_Model_Deployment.pdf (also in this folder)

## Aim

To deploy a trained machine learning model as a REST API on Azure using Azure Machine Learning, so that real-world applications can send data to a web service endpoint and receive predictions over HTTP.

## Objectives

- Register the Pass/Fail classifier trained on student_performance data in Experiment 10 in an Azure Machine Learning workspace.
- Write a scoring script (score.py) that loads the registered model and serves predictions.
- Build an inference configuration and environment with the dependencies the model needs.
- Deploy the model as a web service on Azure Container Instances.
- Test the deployed endpoint with a curl request and record the observed response.
- Monitor the endpoint's health and logs in the Azure portal.

## Architecture

```text
Trained model (Exp 10 Pass/Fail classifier, student_performance data)
        |  Model.register
        v
Azure Machine Learning workspace (<aml-workspace>)
        |  InferenceConfig (score.py + environment)
        v
Azure Container Instances endpoint
        |  scoring URI + primary key (key-based auth)
        v
REST client (curl / any HTTP client)
        |  POST {"data": [[math, english, science], ...]}
        v
JSON response {"predictions": [...]}
```

The model itself never leaves Azure ML: the workspace holds the registered model, ACI runs it behind a scoring script, and any client that can make an HTTP request can use it — no Python or Azure SDK needed on the client side.

## Architecture & Component Roles

| Component | Resource Name | Role / Description |
|---|---|---|
| Resource Group | 25MCAR0141 | Logical container for all Azure experiment resources |
| ML Workspace | <aml-workspace> | Azure Machine Learning workspace holding the registered model and the deployment |
| Registered Model | student-performance-passfail | Pass/Fail classifier trained in Experiment 10 on student_performance data |
| Scoring Script | score.py | Loads the model at startup and serves predictions per request |
| Inference Config | score.py + environment | Ties the scoring script to the Python environment the model needs |
| Compute | Azure Container Instances | Serverless container host running the deployed web service |
| REST Client | curl / HTTP client | Sends JSON input to the scoring URI and receives predictions |

## Services Used

- Azure Machine Learning (model registry, deployment)
- Azure Container Instances
- Azure Portal / Azure ML Studio
- Python (scikit-learn, joblib, azureml-sdk)

## Procedure

### Step 1 — Open Azure ML Studio

Azure Portal → `<aml-workspace>` (resource group `25MCAR0141`, centralindia) → Launch Studio.

### Step 2 — Register the Trained Model

Run `deploy.py` (in this folder), or register from the portal: Models → Register model → upload the model file trained in Experiment 10 → name `student-performance-passfail`. This makes the model a versioned, reusable artifact in the workspace instead of a file on a local machine.

### Step 3 — Write the Scoring Script

Use `score.py` (in this folder): `init()` loads the model once at container startup, and `run(raw_data)` parses each incoming JSON request and returns predictions.

### Step 4 — Build the Inference Config and Environment

In `deploy.py`, the `InferenceConfig` pairs `score.py` with an `Environment` built from `CondaDependencies` (scikit-learn, azureml-defaults). The environment is what the container image is built from, so it must list every package the scoring script imports.

### Step 5 — Deploy to Azure Container Instances

`deploy.py` calls `Model.deploy` with an ACI deployment configuration (1 CPU core, 1 GB memory, key-based authentication enabled) and waits for the deployment to finish. The script prints the scoring URI when the service is healthy.

### Step 6 — Fetch the Primary Key

In Azure ML Studio → Endpoints → the deployed service → Consume tab, copy the primary key. The key is fetched at test time from the portal or CLI — it is never hardcoded in any file in this folder.

### Step 7 — Test the Endpoint with curl

Run `test_endpoint.sh` (in this folder) after filling in the `<scoring-uri>` and `<primary-key>` placeholders. It sends a POST request with a sample student's marks and prints the JSON response. Record the observed response in the Result section of the lab record.

### Step 8 — Monitor the Endpoint

In Azure ML Studio → Endpoints → the service → Logs, check the container logs for startup and request entries, and confirm the service state is Healthy.

### Step 9 — Clean Up (Optional)

When the demo is done, delete the ACI web service from Endpoints to stop incurring container charges. The registered model stays in the workspace and can be redeployed at any time.

## Code Highlights

### Scoring Script — Load Once, Predict per Request

Full script: [`score.py`](score.py)

```python
def init():
    global model
    model_path = os.path.join(os.getenv("AZUREML_MODEL_DIR"), "model.pkl")
    model = joblib.load(model_path)

def run(raw_data):
    data = json.loads(raw_data)
    predictions = model.predict(data["data"])
    return json.dumps({"predictions": predictions.tolist()})
```

`init()` runs once when the container starts, so the model is loaded into memory a single time; `run()` is called once per HTTP request. The script validates the input shape and returns a clear error message for malformed input instead of crashing the request.

### Deployment Script — Register, Configure, Deploy

Full script: [`deploy.py`](deploy.py)

```python
model = Model.register(workspace=ws, model_path="model.pkl",
                       model_name="student-performance-passfail")

inference_config = InferenceConfig(entry_script="score.py", environment=env)

aci_config = AciWebservice.deploy_configuration(cpu_cores=1, memory_gb=1,
                                                auth_enabled=True)

service = Model.deploy(workspace=ws, name="passfail-service",
                       models=[model], inference_config=inference_config,
                       deployment_config=aci_config)
service.wait_for_deployment(show_output=True)
```

Authentication is enabled on the endpoint, so every request must carry the primary key as a Bearer token. The scoring URI is printed after deployment; the key itself is fetched from the portal or CLI at test time.

### Test Request — curl

Full script: [`test_endpoint.sh`](test_endpoint.sh)

```bash
curl -X POST "<scoring-uri>" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <primary-key>" \
  -d '{"data": [[78, 85, 82]]}'
```

Replace `<scoring-uri>` with the scoring URI printed by `deploy.py` (or shown on the endpoint's Consume tab) and `<primary-key>` with the primary key from the same tab.

## Screenshot Checklist

| # | Screenshot | Filename |
|---|---|---|
| 1 | Azure ML Studio — workspace overview (<aml-workspace>) | Step_01_AML_Workspace_Overview.png |
| 2 | Registered model student-performance-passfail (Models list) | Step_02_Registered_Model.png |
| 3 | score.py open in the editor / file list | Step_03_Scoring_Script.png |
| 4 | deploy.py running — deployment in progress | Step_04_Deploy_Script_Running.png |
| 5 | Endpoint created — service state Healthy | Step_05_Endpoint_Healthy.png |
| 6 | Endpoint Consume tab — scoring URI shown | Step_06_Endpoint_Consume_Tab.png |
| 7 | curl test request and JSON response in terminal | Step_07_Curl_Test_Response.png |
| 8 | Endpoint logs showing startup and request entries | Step_08_Endpoint_Logs.png |
| 9 | Azure portal — ACI container instance for the service | Step_09_ACI_Container_Instance.png |
| 10 | Endpoint deleted after demo (optional cleanup) | Step_10_Endpoint_Deleted.png |

Note: screenshots are not in this folder yet — add them under `screenshots/` using the filenames above. Do not include a screenshot that shows the primary key, a token, or any other credential.

## Result

The Pass/Fail classifier trained in Experiment 10 was registered in the Azure Machine Learning workspace and deployed as a REST API on Azure Container Instances. A curl POST request carrying a sample student's marks returned a JSON response with the model's prediction, demonstrating that the model is usable by any HTTP client without the client needing Python or the Azure SDK. Record the observed response from the test run here: ________.

## Key Learning

This experiment demonstrates model deployment on Azure: a trained model becomes a real-world service only when it is registered, wrapped in a scoring script and environment, deployed behind a secured endpoint, and tested end to end from an ordinary HTTP client — with authentication and monitoring as part of the deployment, not an afterthought.
