from locust import events
import os
import random
import time
import requests
import logging
from datetime import datetime, timedelta

MAX_ERR_PERCENT = 99
MAX_RESP90_MS = 9999

@events.quitting.add_listener
def _(environment, **kw):
    if environment.stats.total.fail_ratio > MAX_ERR_PERCENT:
        logging.error(f"PLT failed! errors > {MAX_ERR_PERCENT} %")
        environment.process_exit_code = 1
    elif environment.stats.total.get_response_time_percentile(0.90) > MAX_RESP90_MS:
        logging.error(f"PLT failed! 90%  response time > {MAX_RESP90_MS} ms")
        environment.process_exit_code = 1
    else:
        environment.process_exit_code = 0


def get_env_proxies():
    proxies = {}
    http_proxie = os.getenv('HTTP_PROXY', '')
    https_proxie = os.getenv('HTTPS_PROXY', '')
    if http_proxie:
        proxies['http'] = http_proxie
    if https_proxie:
        proxies['https'] = https_proxie
    return proxies


def get_env_percent(var_name):
    val = int(os.getenv(var_name))
    assert 0 <= val <= 100
    return val


def get_env_days(var_name):
    val = int(os.getenv(var_name))
    assert 0 <= val <= 1000
    return val


def tomorrow() -> str:
    tomorrow = datetime.now().date() + timedelta(1)
    return tomorrow.isoformat()


def rand_number(length: int) -> str:
    return str(random.randint(pow(10, length - 1), pow(10, length) - 1))


def retry(maxTries: int, sleepSeconds: int, func, *args, **kwargs):
    assert maxTries > 0, "Max retry should be greater than 0"
    for i in range(1, maxTries + 1):
        time.sleep(sleepSeconds)
        err = None
        try:
            return func(*args, **kwargs)
        except Exception as ex:
            logging.debug(f'Tried {i} - {ex}')
            err = str(ex)

    raise RuntimeError(f"{err} - exhausted {maxTries} retries")


def prepare_headers(api_version, access_token):
    return {"x-version-api": api_version,
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "accept": "application/json"}


def get_auth_token(auth_host, client_id, client_secret, scope, proxies=None):
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {"grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": scope}
    resp = requests.post(
        f"{auth_host}/connect/token", data=data, headers=headers, proxies=proxies)
    logging.debug(f'Auth response: {resp.text}')
    assert_ok(resp)
    jresp = resp.json()
    assert "access_token" in jresp, f'token missing in: {resp.text}'
    return jresp["access_token"]


def read_file_lines(fpath):
    lines = [line.strip() for line in open(fpath)
             if line.strip() and not line.startswith('#')]
    assert lines
    return lines


def extract_subpath(url, parts_count):
    subpath = ""
    url_parts = url.split('/')
    host_position = 2
    assert len(url_parts) >= host_position + parts_count + 1
    for part_num in range(parts_count):
        subpath += f"/{url_parts[host_position + part_num + 1]}"
    return subpath


def locust_report_line(endpoint, lreport_tag):
    lparams = {}
    if lreport_tag:
        lparams['name'] = f'{endpoint} :{lreport_tag}'
    return lparams


def assert_ok(response):
    assert response.ok, f"Error response: {response.status_code} {response.text}"
