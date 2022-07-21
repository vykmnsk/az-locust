# Performance Testing with Locust

## Setup

Download _latest Python 3.x (64 bit)_ executable (msi) installer from
[python.org](https://www.python.org/downloads/release)

Verify python/pip are installed:

    python --version
    pip --version

Create python virtual environment and install libs (Windows CMD)

    python -m venv .venv
    .venv\Scripts\activate.bat
    pip install --upgrade pip
    pip install -r requirements.txt

Create local .env file (clone/edit an external environment file)

    cd tests/<test-dir>
    cp .env.uat locust/.env
    cd locust/
    vi .env

## Run without Locust

This framework is designed to be able to run tests without Locust similar to other (functional) test automation frameworks.
The automated tests will execute once and report results on the CLI screen (by default).
It is based on Python's powerful and popular unit test library 'pytest'.

When developing new PLTs it is highly recommended to start with creating pytests first and once they work call them from locustfile.
This greatly simplifies coding/debugging as well as assists future maintenance and performance issues troubleshooting

To run pytets:

    cd tests/<test-dir>
    pytest locust/tests.py
    (add --pdb for debugging in CLI)

## Run Locust

### on Local (Windows) machine

#### No UI

2 users hatching 0.5 per second, running for 10 seconds, saving report to a file
check error code (Windows)

    cd tests/<test-dir>
    locust -f locust/locustfile.py --headless -u 2 -r 0.5 -t 10s --loglevel debug --html report.html
    echo %errorlevel%

#### with UI

    cd tests/<test-dir>
    locust -f locust/locustfile.py

> navigate to <http://localhost:8089/>

### in local Docker (with UI)

    cd tests/<test-dir>
    cp ../../libs/ -r ./locust/
    docker build ../../ -t plt-locust-py-libs
    docker run -p 8089:8089 -v "/$(pwd -W)/locust:/mnt/locust" plt-locust-py-libs

    when done:
    rm ./locust/libs -rf

> navigate to <http://localhost:8089/>

### on Azure cloud (sandpit)

Create local environment variables or .env file

    PLT_TEST
    PLT_TEST_WORKERS_CNT
    PLT_TEST_DOCKER_IMAGE

    PLT_AZ_RESOURCE_GROUP
    PLT_AZ_LOCATION
    PLT_AZ_STORAGE_ACCOUNT
    PLT_AZ_FILE_SHARE
    PLT_AZ_DEPLOYMENT

Create Azure resources, upload test src, deploy locust master with workers

    az login
    bash az-upload-docker-img.sh
    bash az-deploy.sh

Read the output and navigate to the Azure generated URL

    http://xx.xx.xx.xx:8089/

Delete all Azure resource we created

    bash azure-teardown.sh
