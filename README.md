# Performance Testing with Locust

## Setup

Download _latest Python 3.x (64 bit)_ executable (msi) installer from [python.org](https://www.python.org/downloads/release)

Verify python/pip are installed:

    python --version
    pip --version

Install python libs

	pip install --upgrade pip
	pip install -r requirements.txt

## Run

No UI, 10 users, 1 new user hatches per second, run for 10 seconds

    locust -f locust/locustfile.py --headless --host http://www.google.com -u 10 -r 1 -t 10s

with UI

    locust -f locust/locustfile.py
> navigate to http://localhost:8089/


in Docker with UI

    docker build . -t alp-py-locust
    docker run -p 8089:8089 -it alp-py-locust -f ./locust/locustfile.py
> navigate to http://localhost:8089/
