#!/bin/bash

# Eliminar todos os datasets por ID

# Lista de IDs dos datasets a eliminar
dataset_ids=(
    "649c7006078190ea9b2176ee"
    "649c7006078190ea952176ea"
    "649f130507819027a01a8373"
    "64a30784078190279e1a8377"
    "649b1e82078190f8a2e77186"
)

# Endpoint base
base_url="https://dados.gov.pt/api/1/datasets"

# Iterar sobre os IDs e apagar cada dataset
# Inserir a Chave da API do seu User - "X-Api-Key: *****"
for id in "${dataset_ids[@]}"; do
    echo "A eliminar dataset com ID: $id"
    curl -X DELETE "${base_url}/${id}/" -H "accept: application/json" -H "X-Api-Key: *****" 
    echo -e "\n-----------------------------"
done
