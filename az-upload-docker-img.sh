#!/bin/bash

# Strict mode, fail on any error
set -euo pipefail

log=".az.log"
echo "logging to $log"
cat << EOF > $log
EOF

source ./env-load.sh
az_location=$PLT_AZ_LOCATION
az_resource_group=$PLT_AZ_RG_DOCKER
az_acr=$PLT_AZ_CONTAINER_REGISTRY
docker_image=$PLT_DOCKER_IMAGE

az_acr_host="$az_acr.azurecr.io"
docker_image_url="$az_acr_host/$docker_image:latest"

echo "create resource group: $az_resource_group" | tee -a $log
az group create \
    --name $az_resource_group \
    --location $az_location \
    -o json >> $log

echo "create container registry: $az_acr" | tee -a $log
az acr create -g $az_resource_group -n $az_acr \
    --sku Basic \
    --admin-enabled true \
    -o json >> $log

acr_usr=$(az acr credential show -g $az_resource_group -n $az_acr --query username -o tsv)
acr_pwd=$(az acr credential show -g $az_resource_group -n $az_acr --query "passwords[0].value" -o tsv)

docker login $az_acr_host --username $acr_usr --password $acr_pwd
docker tag $docker_image $docker_image_url
docker push $docker_image_url

az acr repository list -n $az_acr