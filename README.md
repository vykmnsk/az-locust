# Performance Testing with Locust on Azure

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

## Run Locust

### Local machine

No UI, 10 users, 1 new user hatches per second, run for 10 seconds

    locust -f locust/locustfile.py --headless --host http://www.google.com -u 10 -r 1 -t 10s

with UI

    locust -f locust/locustfile.py
> navigate to http://localhost:8089/


in Docker with UI

    docker build . -t alp-py-locust
    docker run -p 8089:8089 -it alp-py-locust -f ./locust/locustfile.py
> navigate to http://localhost:8089/

### Azure cloud

Create Azure resources, upload test src, deploy locst master with workers

    az login
    azure-deploy.sh 

Read the output and navigate to the Azure generated URL

    http://xx.xx.xx.xx:8089/

Delete all Azure resource we created

    azure-teardown.sh

## Run webapp

### Local machine
set local environment variables with Azure values 

    PLT_AZ_STORAGE_CONN_STRING 
    PLT_AZ_CONTAINER_NAME

execute in CLI

    cd webapp
    flask run

### Azure cloud

    sh azure-deploy-webapp.sh

note the _storage connection string_ and _webapp URL_ in the output

set these environment variables in Azure App Service configuration 

    PLT_AZ_STORAGE_CONN_STRING
    PLT_AZ_CONTAINER_NAME

restart the webapp (Azure portal does it automatically)

navigate to the _webapp URL_ displayed in deploy script output