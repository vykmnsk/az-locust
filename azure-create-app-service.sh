#!/bin/bash

# Strict mode, fail on any error
set -euo pipefail

log=".azure.log"
echo "logging to $log"
cat << EOF > $log
EOF

source ./env-load.sh
resource_group=$PLT_AZ_RESOURCE_GROUP
location=$PLT_AZ_LOCATION
app_service_plan=$PLT_AZ_APP_SERVICE_PLAN

echo "create resource group: $resource_group" | tee -a $log
az group create \
    -n $resource_group --location $location \
    -o json >> $log	

echo "create app service plan: $app_service_plan" | tee -a $log
az appservice plan create \
    -g $resource_group -n $app_service_plan \
    --is-linux --sku F1 \
    -o json >> $log
