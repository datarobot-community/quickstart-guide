#!/usr/bin/env python3
"""
This example code relies on the `requests` and `requests-toolbelt` libraries.
Install it with:
pip3 install requests requests-toolbelt
"""
import os
from pathlib import Path
from time import sleep

import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

api_key = os.getenv("DATAROBOT_API_TOKEN")
host_url = os.getenv("DATAROBOT_ENDPOINT")
dataset_path = Path('.').parent.joinpath('data', 'auto-mpg.csv')

# Step 1: Upload a dataset
form_data = {
    "file": (dataset_path.name, dataset_path.open("rb")),
    "projectName": "Auto MPG PY",
}
encoder = MultipartEncoder(fields=form_data)
headers = {}
headers.update({"Authorization": f"Bearer {api_key}"})
headers.update({"Content-Type": encoder.content_type})
response = requests.post(
    f"{host_url}/projects/", headers=headers, data=encoder.read()
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
        project_id = requests.get(
            response.headers["location"], headers=headers
        ).json().get("id", None)
        if project_id is not None:
            print(f"Project setup complete. Project ID: {project_id}")
            break
        else:
            print("Setting up project...")
            sleep(10)

