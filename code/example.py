#!/usr/bin/env python3
"""
This example code relies on the `requests` and `requests-toolbelt` libraries.
Install it with:
pip3 install requests requests-toolbelt
"""
import json
import os
from pathlib import Path
from pprint import pprint
from time import sleep

import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

datarobot_api_token = os.getenv("DATAROBOT_API_TOKEN")
datarobot_endpoint = os.getenv("DATAROBOT_ENDPOINT")
dataset_file_path = Path(".").parent.joinpath("data", "auto-mpg.csv")

# Step 1: Upload a dataset
form_data = {
    "file": (dataset_file_path.name, dataset_file_path.open("rb")),
    "projectName": "Auto MPG PY",
}
encoder = MultipartEncoder(fields=form_data)
headers = {}
headers.update({"Authorization": f"Bearer {datarobot_api_token}"})
headers.update({"Content-Type": encoder.content_type})
response = requests.post(
    f"{datarobot_endpoint}/projects/", headers=headers, data=encoder.read()
)
try:
    assert response.status_code == 202
except AssertionError:
    print(
        f"Status code: {response.status_code}, Reason: {response.reason}, "
        f"Details: {response.content}"
    )
else:
    # if you are not using app2.datatrobot.com endpoints
    # change `location` to `Location`
    while True:
        project_id = (
            requests.get(response.headers["location"], headers=headers)
            .json()
            .get("id", None)
        )
        if project_id is not None:
            print(f"Project setup complete. Project ID: {project_id}")
            break
        else:
            print("Setting up project...")
            sleep(10)

# Step 2: Train & Deploy an AI
# Train
form_data = {"target": "mpg", "mode": "quick"}
encoder = MultipartEncoder(fields=form_data)
train_response = requests.patch(
    f"{datarobot_endpoint}/projects/{project_id}/aim",
    headers=headers,
    data=encoder.read(),
)
try:
    assert train_response.status_code == 202
except AssertionError:
    print(
        f"Status code: {train_response.status_code}, Reason: {train_response.reason}, "
        f"Details: {train_response.content}"
    )
else:
    while True:
        project_status = (
            requests.get(train_response.headers["location"], headers=headers)
            .json()
            .get("stage", None)
        )
        if project_status is not None:
            print("Training AI. Initial best model ready to deploy.")
            break
        else:
            print("Setting up AI training...")
            sleep(10)
# Deploy
server_data = requests.get(
    f"{datarobot_endpoint}/predictionServers/", headers=headers
)
default_server_id = server_data.json()["data"][0]["id"]
request_data = {
    "label": "MPG Prediction Server",
    "description": "Automodel deployed with python",
    "projectId": project_id,
    "defaultPredictionServerId": default_server_id,
}
deploy_response = requests.post(
    f"{datarobot_endpoint}/fromProjectRecommendedModel/",
    headers=headers,
    json=request_data,
)
deployment_status = deploy_response.headers["location"]
while True:
    deployment_status = requests.get(deployment_status)
    if deployment_status.json().get("id", None) is not None:
        print(f"Prediction server ready.")
        break
    else:
        print("Waiting for deployment...")
        sleep(10)
server_id = deployment_status.json()["defaultPredictionServer"]["id"]
server_url = deployment_status.json()["defaultPredictionServer"]["url"]
server_key = deployment_status.json()["defaultPredictionServer"][
    "datarobot-key"
]
# Step 3: Make predictions
autos = [
    {
        "cylinders": 4,
        "displacement": 119.0,
        "horsepower": 82.00,
        "weight": 2720.0,
        "acceleration": 19.4,
        "model year": 82,
        "origin": 1,
    },
    {
        "cylinders": 8,
        "displacement": 120.0,
        "horsepower": 79.00,
        "weight": 2625.0,
        "acceleration": 18.6,
        "model year": 82,
        "origin": 1,
    },
]
prediction_headers = {
    "Authorization": f"Bearer {datarobot_api_token}",
    "Content-Type": "application/json",
    "datarobot-key": server_key,
}
predictions = requests.post(
    f"{server_url}/predApi/v1.0/deployments/{server_id}/predictions",
    headers=prediction_headers,
    data=json.dumps(autos),
)
pprint(predictions.json())

# Step 4: Monitor deployment
service_health_headers = {"Authorization": f"Bearer {datarobot_api_token}"}
service_health = requests.get(
    f"{datarobot_api_token}/deployments/{server_id}/serviceStats/",
    headers=service_health_headers,
)
pprint(service_health.json())
