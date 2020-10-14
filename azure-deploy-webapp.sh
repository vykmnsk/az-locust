#!/bin/bash

# Strict mode, fail on any error
set -euo pipefail

log=".azure.log"
echo "logging to $log"
cat << EOF > $log
EOF

source ./env-load.sh
resource_group=$PLT_AZ_RESOURCE_GROUP
app_service_plan=$PLT_AZ_APP_SERVICE_PLAN
web_app=$PLT_AZ_WEB_APP
storage_conn_str=$PLT_AZ_STORAGE_CONN_STRING
storage_out_conn_str=$PLT_AZ_STORAGE_OUT_CONN_STRING
app_src_dir="webapp"

echo "prepare src $app_src_dir.zip"
rm -rf $app_src_dir/__pycache__
7z a $app_src_dir.zip -r ./$app_src_dir/* > $log

echo "create azure webapp" | tee -a $log
az webapp create \
    -g $resource_group -p $app_service_plan -n $web_app \
    --runtime "python|3.6" \
    -o json >> $log

echo "configure webapp"
az webapp config appsettings set \
    -g $resource_group -n $web_app \
    --settings SCM_DO_BUILD_DURING_DEPLOYMENT=true \
                PLT_AZ_STORAGE_CONN_STRING="$storage_conn_str" \
                PLT_AZ_STORAGE_OUT_CONN_STRING="$storage_out_conn_str" \
    -o json >> $log

echo "upload src $app_src_dir.zip"
az webapp deployment source config-zip \
    -g $resource_group -n $web_app \
    --src ./$app_src_dir.zip \
    -o json >> $log


echo "Webapp deployed at:" | tee -a $log
echo "http://$web_app.azurewebsites.net" | tee -a $log