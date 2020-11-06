#!/bin/bash

# Strict mode, fail on any error
set -euo pipefail

log=".az.log"
echo "logging to $log"
cat << EOF > $log
EOF

source ./env-load.sh

echo "deploy test=$PLT_TEST"
test_src="tests/$PLT_TEST/locust/"
test_libs="libs"
test_workers_cnt=$PLT_TEST_WORKERS_CNT

az_location=$PLT_AZ_LOCATION

az_rg_docker=$PLT_AZ_RG_DOCKER
az_acr=$PLT_AZ_CONTAINER_REGISTRY
docker_image=$PLT_DOCKER_IMAGE
az_acr_host="$az_acr.azurecr.io"
docker_image_url="$az_acr_host/$docker_image:latest"

az_rg_infra=$PLT_AZ_RG_INFRA
az_storage_account=$PLT_AZ_STORAGE_ACCOUNT
az_file_share=$PLT_AZ_FILE_SHARE
az_container_master='locust-master-0'
az_container_worker='locust-worker'

echo "create resource group: $az_rg_infra" | tee -a $log
az group create \
    --name $az_rg_infra \
    --location $az_location \
    -o json >> $log

echo "create storage account: $az_storage_account" | tee -a $log
az storage account create \
    --name $az_storage_account \
    -g $az_rg_infra \
    --sku Standard_LRS \
    -o json >> $log

echo "get storage connection string" | tee -a $log
az_storage_conn_string=$(az storage account show-connection-string -g $az_rg_infra -n $az_storage_account -o tsv)

echo 'create file share' | tee -a $log
az storage share create \
    --name $az_file_share \
    --connection-string $az_storage_conn_string \
    -o json >> $log

echo 'upload test src files' | tee -a $log
az storage file upload-batch \
    --source $test_src \
    --pattern "*[!p][!y][!c]" \
    --destination $az_file_share  \
    --connection-string $az_storage_conn_string \
    -o json >> $log

echo 'upload test libs files' | tee -a $log
az storage file upload-batch \
    --source $test_libs \
    --pattern "*[!p][!y][!c]" \
    --destination $az_file_share  \
    --destination-path $test_libs \
    --connection-string $az_storage_conn_string \
    -o json >> $log

echo "get storage key for account=$az_storage_account" | tee -a $log
storage_key=$(az storage account keys list -g $az_rg_infra --account-name $az_storage_account --query "[0].value" -o tsv)

echo "get docker registry credentials" | tee -a $log
acr_usr=$(az acr credential show -g $az_rg_docker -n $az_acr --query username -o tsv)
acr_pwd=$(az acr credential show -g $az_rg_docker -n $az_acr --query "passwords[0].value" -o tsv)

echo "create master container with $docker_image" | tee -a $log
az container create -g $az_rg_infra -n $az_container_master \
    --image "$docker_image_url" \
    --registry-username $acr_usr \
    --registry-password $acr_pwd \
    --ip-address Public --ports 8089 5557 \
    --memory 2 --restart-policy OnFailure \
    --azure-file-volume-account-name $az_storage_account \
    --azure-file-volume-account-key $storage_key \
    --azure-file-volume-share-name $az_file_share \
    --azure-file-volume-mount-path "//mnt/locust" \
    --command-line "locust -f /mnt/locust/locustfile.py --master --expect-workers $test_workers_cnt" \
    -o json >> $log

master_ip=$(az container show -g $az_rg_infra --name $az_container_master --query ipAddress.ip -o tsv)
echo "locust master ip=$master_ip"

for (( i=1; i<=$test_workers_cnt; i++ ))
do
echo "create worker container $i with $docker_image" | tee -a $log
az container create -g $az_rg_infra -n "$az_container_worker-$i" \
    --image "$docker_image_url" \
    --registry-username $acr_usr \
    --registry-password $acr_pwd \
    --ip-address Public --ports 8089 5557 \
    --memory 2 --restart-policy OnFailure \
    --azure-file-volume-account-name $az_storage_account \
    --azure-file-volume-account-key $storage_key \
    --azure-file-volume-share-name $az_file_share \
    --azure-file-volume-mount-path "//mnt/locust" \
    --command-line "locust -f /mnt/locust/locustfile.py --worker --master-host $master_ip" \
    -o json >> $log
done

echo "locust URL:" | tee -a $log
echo "$master_ip:8089" | tee -a $log