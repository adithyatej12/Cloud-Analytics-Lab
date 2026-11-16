"""Scoring script for the student Pass/Fail classifier (Experiment 11).

Azure ML calls init() once when the container starts and run() once per
HTTP request. Expected request body:

    {"data": [[math, english, science], ...]}

Response body:

    {"predictions": [...]}
"""

import json
import os

import joblib

model = None


def init():
    """Load the registered model into memory once at container startup."""
    global model
    model_dir = os.getenv("AZUREML_MODEL_DIR")
    if not model_dir:
        raise RuntimeError(
            "AZUREML_MODEL_DIR is not set; the model directory is not available."
        )
    model_path = os.path.join(model_dir, "model.pkl")
    model = joblib.load(model_path)


def run(raw_data):
    """Run inference on one JSON request and return predictions as JSON."""
    try:
        payload = json.loads(raw_data)
    except (TypeError, ValueError):
        return json.dumps(
            {"error": "Invalid request: body must be valid JSON, e.g. "
                      '{"data": [[78, 85, 82]]}.'}
        )

    if not isinstance(payload, dict) or "data" not in payload:
        return json.dumps(
            {"error": 'Invalid request: JSON body must contain a "data" key, '
                      'e.g. {"data": [[78, 85, 82]]}.'}
        )

    data = payload["data"]
    if not isinstance(data, list) or not data:
        return json.dumps(
            {"error": 'Invalid request: "data" must be a non-empty list of '
                      'rows, e.g. {"data": [[78, 85, 82]]}.'}
        )

    for row in data:
        if (
            not isinstance(row, list)
            or len(row) != 3
            or not all(isinstance(x, (int, float)) for x in row)
        ):
            return json.dumps(
                {"error": 'Invalid request: each row in "data" must be a list '
                          'of 3 numbers [math, english, science], e.g. '
                          '{"data": [[78, 85, 82]]}.'}
            )

    try:
        predictions = model.predict(data)
    except Exception as exc:  # noqa: BLE001 - surface model errors to caller
        return json.dumps({"error": "Prediction failed: {}".format(exc)})

    return json.dumps({"predictions": predictions.tolist()})
