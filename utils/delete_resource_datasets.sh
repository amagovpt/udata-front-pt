#!/bin/bash

# Script to delete a specific resource from a dataset

# Dataset and Resource IDs
dataset_id="660c3c451ee8ad9bd6b60608"
resource_id="1289e037-f8f1-44ee-8ac4-14d6bc2722ac"

# Endpoint base
base_url="https://dados.gov.pt/api/1/datasets"

# API Key (replace with your actual key)
api_key="*****"

echo "Deleting resource $resource_id from dataset $dataset_id"
curl -k -X DELETE "${base_url}/${dataset_id}/resources/${resource_id}/" \
    -H "accept: application/json" \
    -H "X-Api-Key: $api_key"

echo -e "\n