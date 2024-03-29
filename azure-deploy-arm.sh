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
TEST_FILE=$PLT_TEST_FILE
TEST_SRC="locust/"
ARM_TEMPLATE="azure-arm.json"

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

echo 'create file share' | tee -a $LOG
az storage share create \
    --name $AZ_FILE_SHARE \
    --connection-string $AZ_STORAGE_CONN_STRING \
    -o json >> $LOG

echo 'upload test src files' | tee -a $LOG
az storage file upload-batch \
    --source $TEST_SRC \
    --destination $AZ_FILE_SHARE  \
    --connection-string $AZ_STORAGE_CONN_STRING \
    -o json >> $LOG

echo "deploying locust master with $NUM_WORKERS workers..." | tee -a $LOG
az deployment group create \
    -g $AZ_RESOURCE_GROUP \
    --name $AZ_DEPLOYMENT \
    --template-file $ARM_TEMPLATE \
    --parameters \
        host=$HOST \
        storageAccountName=$AZ_STORAGE_ACCOUNT \
        fileShareName=$AZ_FILE_SHARE \
        numWorkers=$NUM_WORKERS \
        testFilePath="$TEST_SRC/$TEST_FILE" \
    -o json >> $LOG

 echo "navigate to Locust monitor:"
 az deployment group show \
    -g $AZ_RESOURCE_GROUP \
    -n $AZ_DEPLOYMENT \
    --query properties.outputs.locustMonitor.value