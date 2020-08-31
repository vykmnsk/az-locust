#!/bin/bash

# Strict mode, fail on any error
set -euo pipefail

echo "starting..."
LOG="azure.log"
cat << EOF > $LOG
EOF

# config
AZ_RESOURCE_GROUP=$PLT_AZ_RESOURCE_GROUP
AZ_LOCATION=$PLT_AZ_LOCATION
AZ_STORAGE_ACCOUNT=$PLT_AZ_STORAGE_ACCOUNT
AZ_FILE_SHARE=$PLT_AZ_FILE_SHARE
AZ_DEPLOYMENT=$PLT_AZ_DEPLOYMENT
HOST=$PLT_TEST_HOST # default SuT base host URL
NUM_WORKERS=$PLT_NUM_WORKERS
ARM_TEMPLATE="azure-arm.json"
TEST_SRC="locust/"

echo "create resource group: $AZ_RESOURCE_GROUP" | tee -a $LOG
az group create \
    --name $AZ_RESOURCE_GROUP \
    --location $AZ_LOCATION \
    -o json >> $LOG	

echo "create storage account: $AZ_STORAGE_ACCOUNT" | tee -a $LOG
az storage account create \
    --name $AZ_STORAGE_ACCOUNT \
    -g $AZ_RESOURCE_GROUP \
    --sku Standard_LRS \
    -o json >> $LOG

echo "get storage connection string" | tee -a $LOG
AZ_STORAGE_CONN_STRING=$(az storage account show-connection-string -g $AZ_RESOURCE_GROUP -n $AZ_STORAGE_ACCOUNT -o tsv)

echo "conn str=$AZ_STORAGE_CONN_STRING"