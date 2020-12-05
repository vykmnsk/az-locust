import os
import tests
from locust import HttpUser, between, task
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())
PROXIES = {'https': os.getenv('HTTPS_PROXY') }
TEST_HOST = os.getenv('PLT_TEST_HOST')
USER_GUEST_WEIGHT = int(os.getenv('PLT_USER_GUEST_WEIGHT', 1))
USER_AUTH_WEIGHT = int(os.getenv('PLT_USER_AUTH_WEIGHT', 1))
PUB_KEYS = tests.read_pub_keys()

class GuestUser(HttpUser):
    host = TEST_HOST
    weight = USER_GUEST_WEIGHT
    wait_time = between(0.1, 1)

    @task
    def authorize_guest(self):
        with tests.call_authorize_guest(self.client) as resp:
            try:
                tests.validate_authorize_guest(resp)
                token = tests.extract_url_token(resp.url)
                tests.validate_jwt_guest(token, PUB_KEYS)
            except Exception as err:
                resp.failure(err)
                return
            resp.success()


class AuthUser(HttpUser):
    host = TEST_HOST
    weight = USER_AUTH_WEIGHT
    wait_time = between(0.1, 1)
    sess_cookie = None

    def on_start(self):
        print('>>> new user login')
        self.client.proxies = PROXIES
        self.sess_cookie = tests.test_login_for_session_cookie()

    @task
    def authorize_with_session_cookie(self):
        assert self.sess_cookie, '>>> session cookie missing - login failed?'
        token = None
        with tests.call_authorize_client(self.client, self.sess_cookie) as resp:
            try:
                tests.validate_authorize_client(resp)
                token = tests.extract_url_token(resp.url)
                if token:
                    tests.validate_jwt_client(token, PUB_KEYS)
            except Exception as err:
                resp.failure(err)
                return
            resp.success()


        if not token:
            with tests.submit_okta_form(self.client, resp.text) as resp:
                try:
                    tests.validate_okta_form(resp)
                    token = tests.extract_url_token(resp.url)
                    tests.validate_jwt_client(token, PUB_KEYS)
                except Exception as err:
                    resp.failure(err)
                    return
                resp.success()



