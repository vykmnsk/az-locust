#!/bin/bash

# Strict mode, fail on any error
set -euo pipefail

envfile=".env"
if [[ -f $envfile ]]; then
	echo "load env vars from $envfile file"
    set -o allexport
    source ./$envfile
    set +o allexport
else
    echo "No envflie=$envfile found, using local environment"
fi
