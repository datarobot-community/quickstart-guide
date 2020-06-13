#!/usr/bin/env python3
"""
This example code relies on the `datarobot` library
Install it with:
pip3 install datarobot
"""
import json
import os
from pathlib import Path
from pprint import pprint
import requests

import datarobot as dr

datarobot_api_token = os.getenv("DATAROBOT_API_TOKEN")
datarobot_endpoint = os.getenv("DATAROBOT_ENDPOINT")
dataset_file_path = Path(".").parent.joinpath("data", "auto-mpg.csv")


# Step 1: Upload a dataset
dr.Client(endpoint=datarobot_endpoint, token=datarobot_api_token)
project = dr.Project.start(
    project_name="Auto MPG DR-Client",
    sourcedata=dataset_file_path.as_posix(),
    target="mpg",
)

# Step 2: Train & Deploy an AI
# Train
# Autopilot will take a bit to complete.
# Run the following and then grab a coffee or catch up on email.
project.wait_for_autopilot()
model = dr.ModelRecommendation.get(project.id)
# Deploy
prediction_server = dr.PredictionServer.list()[0]
deployment = dr.Deployment.create_from_learning_model(
    model_id=model.model_id,
    label="MPG Prediction Server",
    description="Deployed with DataRobot client",
    default_prediction_server_id=prediction_server.id,
)

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
    "datarobot-key": prediction_server.datarobot_key,
}
predictions = requests.post(
    f"{prediction_server.url}/predApi/v1.0/deployments"
    f"/{deployment.id}/predictions",
    headers=prediction_headers,
    data=json.dumps(autos),
)
pprint(predictions.json())

# Step 4: Monitor deployment
service_stats = deployment.get_service_stats()
pprint(service_stats.metrics)
