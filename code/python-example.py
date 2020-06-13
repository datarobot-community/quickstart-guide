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
headers = {}
headers.update(
    {
        "Authorization": f"Bearer {datarobot_api_token}",
        "Content-Type": "application/json",
    }
)
form_data = {"target": "mpg", "mode": "quick"}
train_response = requests.patch(
    f"{datarobot_endpoint}/projects/{project_id}/aim",
    headers=headers,
    json=form_data,
)
try:
    assert train_response.status_code == 202
except AssertionError:
    print(
        f"Status code: {train_response.status_code}, "
        f"Reason: {train_response.reason}, "
        f"Details: {train_response.content}"
    )
else:
    while True:
        training_status = (
            requests.get(train_response.headers["location"], headers=headers)
            .json()
            .get("stage", None)
        )
        if training_status is not None:
            print(
                "Training AI. This will take a bit. "
                "Grab a coffee or catch up on email."
            )
            break
        else:
            print("Setting up AI training...")
            sleep(10)
while True:
    try:
        project_status = requests.get(
            f"{datarobot_endpoint}/projects/{project_id}/status",
            headers=headers,
        )
        assert project_status.status_code == 200
    except AssertionError:
        print(
            f"Something went wrong. Status code: {project_status.status_code}, "
            f"Reason: {project_status.reason}"
        )
        exit()
    else:
        if project_status.json()["autopilotDone"]:
            print("Autopilot training complete. AI ready to deploy.")
            break
        else:
            print("Autopilot training in progress...")
            sleep(60)
# Deploy
recommended_model = requests.get(
    f"{datarobot_endpoint}/projects/{project_id}/recommendedModels/"
    f"recommendedModel/",
    headers=headers,
)
model_id = recommended_model.json()["modelId"]

server_response = requests.get(
    f"{datarobot_endpoint}/predictionServers/", headers=headers
)
server_data = server_response.json()["data"][0]
default_server_id = server_data["id"]
default_server_url = server_data["url"]
default_server_key = server_data["datarobot-key"]

request_data = {
    "defaultPredictionServerId": default_server_id,
    "modelId": model_id,
    "description": "Deployed with python",
    "label": "MPG Prediction Server",
}
deploy_response = requests.post(
    f"{datarobot_endpoint}/deployments/fromLearningModel",
    headers=headers,
    json=request_data,
)
if deploy_response.status_code == 202:
    deployment_status = deploy_response.headers["location"]
    while True:
        deployment_status = requests.get(deployment_status)
        if deployment_status.json().get("id", None) is not None:
            print(f"Prediction server ready.")
            deployment_id = deployment_status.json()["id"]
            break
        else:
            print("Waiting for deployment...")
            sleep(10)
elif deploy_response.status_code != 200:
    print(
        f"Something went wrong. Status code: {deploy_response.status_code}, "
        f"Reason: {deploy_response.reason}"
    )
else:
    deployment_id = deploy_response.json()["id"]
    print(f"Prediction server ready.")

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
    "datarobot-key": default_server_key,
}
predictions = requests.post(
    f"{default_server_url}/predApi/v1.0/deployments/{deployment_id}"
    f"/predictions",
    headers=prediction_headers,
    data=json.dumps(autos),
)
pprint(predictions.json())

# Step 4: Monitor deployment
service_health_headers = {
    "Authorization": f"Bearer {datarobot_api_token}",
    "Content-Type": "application/json",
}
service_health = requests.get(
    f"{datarobot_endpoint}/deployments/{deployment_id}/serviceStats/",
    headers=service_health_headers,
)
pprint(service_health.json())
