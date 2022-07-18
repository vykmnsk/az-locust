FROM locustio/locust:1.2.3

ENV PYTHONPATH /bin/python
ENV PATH $PATH:/home/locust/.local/bin

COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 5557 5558 8089
ENTRYPOINT ["locust"]
CMD ["-f", "/mnt/locust/locustfile.py", "--loglevel", "debug"]