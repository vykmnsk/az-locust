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

## Run

No UI, 10 users, 1 new user hatches per second, run for 10 seconds

    locust -f locust/locustfile.py --headless --host http://www.google.com -u 10 -r 1 -t 10s

### Locally with UI

    locust -f locust/locustfile.py
> navigate to http://localhost:8089/


### in local Docker with UI

    docker build . -t alp-py-locust
    docker run -p 8089:8089 -it alp-py-locust -f ./locust/locustfile.py
> navigate to http://localhost:8089/

## Run webapp

    flask run

### on AZURE with UI

Create Azure resources, upload test src, deploy locst master with workers

    az login
    azure-deploy.sh 

Read the output and navigate to the Azure generated URL

    http://xx.xx.xx.xx:8089/

Delete all Azure resource we created

    azure-teardown.sh