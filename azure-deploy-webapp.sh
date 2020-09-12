#!/bin/bash

# Strict mode, fail on any error
set -euo pipefail

echo "starting..."
log="azure.log"
cat << EOF > $log
EOF

# config
resource_group=$PLT_AZ_RESOURCE_GROUP
location=$PLT_AZ_LOCATION
storage_account=$PLT_AZ_STORAGE_ACCOUNT
app_src_dir="webapp"
app_service_plan=$PLT_AZ_APP_SERVICE_PLAN
web_app=$PLT_AZ_WEB_APP

echo "prepare app src zip"
7z a $app_src_dir.zip ./$app_src_dir/*.* > $log  # use zip for *nix

echo "create resource group: $resource_group" | tee -a $log
az group create \
    -n $resource_group --location $location \
    -o json >> $log	

echo "create storage account: $storage_account" | tee -a $log
az storage account create \
    -g $resource_group -n $storage_account \
    --sku Standard_LRS \
    -o json >> $log

echo "get storage connection string" | tee -a $log
storage_conn_string=$(az storage account show-connection-string -g $resource_group -n $storage_account -o tsv)
echo "conn str=$storage_conn_string"

echo "creating app service plan" | tee -a $log
az appservice plan create \
    -g $resource_group -n $app_service_plan \
    --is-linux --sku F1 \
    -o json >> $log

echo "deploying web app" | tee -a $log
az webapp create \
    -g $resource_group -p $app_service_plan -n $web_app \
    --runtime "python|3.6" \
    -o json >> $log

az webapp config appsettings set \
    -g $resource_group -n $web_app \
    --settings SCM_DO_BUILD_DURING_DEPLOYMENT=true \
    -o json >> $log

az webapp deployment source config-zip \
    -g $resource_group -n $web_app \
    --src ./$app_src_dir.zip \
    -o json >> $log


echo "Go to:" | tee -a $log
echo "http://$web_app.azurewebsites.net" | tee -a $log