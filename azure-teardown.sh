#!/bin/bash

# Strict mode, fail on any error
set -euo pipefail

# config
AZ_RESOURCE_GROUP="plt-poc"

az group delete --name $AZ_RESOURCE_GROUP