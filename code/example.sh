#!/usr/bin/env bash

set -e
set -a
source ../.env.app2

DATAROBOT_API_TOKEN=${DATAROBOT_API_TOKEN}
DATAROBOT_ENDPOINT=${DATAROBOT_ENDPOINT}
DATASET_FILE_PATH=$(pwd)'/data/auto-mpg.csv'

# Step 1: Upload a dataset
location=$(curl -Lsi \
  -X POST \
  -H "Authorization: Bearer ${DATAROBOT_API_TOKEN}" \
  -F 'projectName="Auto MPG CURL"' \
  -F "file=@${DATASET_FILE_PATH}" \
  "${DATAROBOT_ENDPOINT}/projects/" | grep -i 'location: .*$' \
  | cut -d " " -f2 | tr -d '\r')
echo "Uploaded dataset. Checking status of project at: ${location}"
while true; do
  project_id=$(curl -Ls \
    -X GET \
    -H "Authorization: Bearer ${DATAROBOT_API_TOKEN}" "${location}" \
    | grep -Eo 'id":\s"\w+' | cut -d '"' -f3 | tr -d '\r')
  if [ "${project_id}" = "" ]
  then
    echo "Setting up project..."
    sleep 10
  else
    echo "Project setup complete."
    echo "Project ID: ${project_id}"
    break
  fi
done

# Step 2: Train & Deploy an AI
## Train
response=$(curl -Lsi \
  -X PATCH \
  -H "Authorization: Bearer ${DATAROBOT_API_TOKEN}" \
  -F 'target="mpg"' \
  -F 'mode="quick"' \
  "${DATAROBOT_ENDPOINT}/projects/${project_id}/aim" | grep 'location: .*$' \
  | cut -d " " | tr -d '\r')
echo "AI training initiated. Checking status of training at: ${response}"
while true; do
  project_status=$(curl -Ls \
    -X GET \
    -H "Authorization: Bearer ${DATAROBOT_API_TOKEN}" "${response}" \
    | grep -Eo 'stage":\s"\w+' | cut -d '"' -f3 | tr -d '\r')
  if [ "${project_status}" = "" ]
  then
    echo "Setting up AI training..."
    sleep 10
  else
    echo "Training AI. Initial best model ready to deploy."
  fi
done
## Deploy
server_data=$(curl -s -X GET \
  -H "Authorization: Bearer ${DATAROBOT_API_TOKEN}" \
  "${DATAROBOT_ENDPOINT}/predictionServers/")
server_id=$(echo $server_data | grep -Eo 'id":\s"\w+' | cut -d '"' -f3 | tr -d '\r')
deployment_response=$(curl -Lsi -X POST \
  -H "Authorization: Bearer ${DATAROBOT_API_TOKEN}" \
  -F 'label="MPG Prediction Server"' \
  -F 'description="Automodel deployed"' \
  -F 'projectId='"\"${project_id}\"" \
  -F 'defaultPredictionServerId='"\"${server_id}\"" \
  "${DATAROBOT_ENDPOINT}/fromProjectRecommendedModel/")
deployment_status=$(echo $deployment_response | grep -Eo 'location: .*$' \
  | cut -d " " | tr -d '\r')
while true; do
  deployment_ready=$(curl -Ls \
  -X GET \
  -H "Authorization: Bearer ${DATAROBOT_API_TOKEN}" "${deployment_status}" \
  | grep -Eo 'id":\s"\w+' | cut -d '"' -f3 | tr -d '\r')
  if [ "${deployment_ready}" = "" ]
  then
    echo "Waiting for deployment..."
    sleep 10
  else
    echo "Prediction server ready."
  fi
done
server_url=$(echo $server_data | grep -Eo 'url":\s".*?"' | cut -d '"' -f3 | tr -d '\r')
server_key=$(echo $server_data | grep -Eo 'datarobot-key":\s".*?"' | cut -d '"' -f3 \
  | tr -d '\r')
# Step 3: Make predictions
# shellcheck disable=SC2089
autos='[{
  "cylinders": 4,
  "displacement": 119.0,
  "horsepower": 82.00,
  "weight": 2720.0,
  "acceleration": 19.4,
  "model year": 82,
  "origin":1
},{
  "cylinders": 8,
  "displacement": 120.0,
  "horsepower": 79.00,
  "weight": 2625.0,
  "acceleration": 18.6,
  "model year": 82,
  "origin":1
}]'
curl -X POST \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer ${DATAROBOT_API_TOKEN}" \
  -H "datarobot-key: ${server_key}" \
  --data "${autos}" \
  "${server_url}/predApi/v1.0/deployments/${server_id}/predictions"

# Step 4: Monitor deployment
curl -s -X GET \
-H "Authorization: Bearer ${DATAROBOT_API_TOKEN}" \
"${DATAROBOT_ENDPOINT}/deployments/5e9e89d1dfea0f0412c35be0/serviceStats/" | jq .