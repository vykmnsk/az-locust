FROM locustio/locust:1.2.3

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 5557 5558 8089
ENTRYPOINT ["locust"]
CMD ["-f",  "/mnt/locust/locustfile.py"]