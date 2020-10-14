# Performance Testing with Locust

## Setup

Download _latest Python 3.x (64 bit)_ executable (msi) installer from [python.org](https://www.python.org/downloads/release)

Verify python/pip are installed:

    python --version
    pip --version

 Create a virtual environment and install python libs (Windows CMD)

    python -m venv venv
    venv\Scripts\activate.bat
	pip install --upgrade pip
	pip install -r requirements.txt

## Run webapp

### Local machine
set local environment variables

    PLT_AZ_STORAGE_CONN_STRING

execute in CLI

    cd webapp
    pip install -r requirements.txt
    flask run

### Azure cloud

set local environment variables

    PLT_AZ_RESOURCE_GROUP
    PLT_AZ_LOCATION
    PLT_AZ_APP_SERVICE_PLAN
    PLT_AZ_WEB_APP


upload the webapp

    az login
    sh azure-create-app-service.sh
    sh azure-deploy-webapp.sh

set the following env var as Application setting in Azure portal app service Configuration

    PLT_AZ_STORAGE_CONN_STRING

navigate to the _webapp URL_ displayed in deploy script output

delete all Azure resources we created

    cd <project root>
    sh azure-teardown.sh
