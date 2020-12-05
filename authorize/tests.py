import sys
sys.path.insert(1, '../../')
import libs.utils as utils
import os, sys
import requests
from dotenv import load_dotenv, find_dotenv
from urllib.parse import urlencode
from lxml import html
import json
import jwt

load_dotenv(find_dotenv())
LOGIN_HOST = os.getenv('PLT_LOGIN_HOST')
USERNAME = os.getenv('PLT_USERNAME')
PASSWORD = os.getenv('PLT_PASSWORD')
HOST = os.getenv('PLT_TEST_HOST')
REDIRECT_URI = os.getenv('PLT_REDIRECT')
REDIRECT_URI_GUEST = os.getenv('PLT_REDIRECT_GUEST')
CLIENT_ID = os.getenv('PLT_CLIENT_ID')
CLIENT_ID_GUEST = os.getenv('PLT_CLIENT_ID_GUEST')
SCOPE = os.getenv('PLT_SCOPE')
JWT_ISSUER = os.getenv('PLT_JWT_ISSUER')
# debug only
SESS_COOKIE = os.getenv('PLT_OKTA_SID')


def test_authorize_guest(http_client=requests.Session()):
    resp = call_authorize_guest(http_client)
    validate_authorize_guest(resp)
    token = extract_url_token(resp.url)
    validate_jwt_guest(token, read_pub_keys())


def call_authorize_guest(http_client, host=HOST, client_id=CLIENT_ID_GUEST, scope=SCOPE, redirect_uri=REDIRECT_URI_GUEST):
    path = '/connect/authorize'
    rand_id = utils.rand_number(6)
    params = {
        'response_type': 'id_token token',
        'client_id': client_id,
        'scope': 'openid profile',
        'redirect_uri': redirect_uri,
        'nonce': f'test_nonce_{rand_id}',
        'acr_values': f'adtid:test_adtid_{rand_id}'
    }
    url = f"{host}{path}?{urlencode(params)}"
    lparams = add_params_for_locust(http_client, path, client_id)

    print(f'\n>>> URL ({client_id}): {url}')
    resp = http_client.get(url, **lparams)
    return resp


def validate_authorize_guest(resp):
    assert resp.ok or resp.status_code == 401, f'Err reponse={resp.text}'
    assert '>Error' not in resp.text


def test_login_for_session_cookie(http_client=requests.Session()):
    sess_token = primary_auth(http_client)
    assert sess_token
    sess_cookie = exchange_token_to_cookie(http_client, sess_token)
    assert sess_cookie
    print(f'>>> session cookie (sid): {sess_cookie}')
    return sess_cookie


def primary_auth(http_client, login_host=LOGIN_HOST, username=USERNAME, password=PASSWORD):
    url = f'{login_host}/api/v1/authn'
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    payload = {
        "username": username,
        "password": password,
        "options": {
            "warnBeforePasswordExpired": True,
            "multiOptionalFactorEnroll": True,
        },
    }
    resp = http_client.post(url, headers=headers, json=payload)
    assert resp.ok, f'resp={resp.text} url={resp.request.url} usr={username}'
    jresp = json.loads(resp.content)
    assert jresp['status'] == 'SUCCESS', f'resp={jresp}'
    return jresp['sessionToken']


def exchange_token_to_cookie(http_client, token, login_host=LOGIN_HOST, redirect_uri=REDIRECT_URI):
    url = f'{login_host}/login/sessionCookieRedirect?token={token}&redirectUrl={redirect_uri}'
    print(f'\n>>> exch URL:\n {url}')
    resp = requests.get(url)
    return resp.cookies['sid']


def test_auth_with_cookie(http_client=requests.Session(), sess_cookie=SESS_COOKIE):
    resp = call_authorize_client(http_client, sess_cookie)
    validate_authorize_client(resp)
    token = extract_url_token(resp.url)
    if not token:
        resp = submit_okta_form(http_client, resp.text)
        validate_okta_form(resp)
        token = extract_url_token(resp.url)

    validate_jwt_client(token, read_pub_keys())


def call_authorize_client(http_client, sess_cookie, host=HOST, client_id=CLIENT_ID, scope=SCOPE, redirect_uri=REDIRECT_URI):
    path = '/connect/authorize'
    rand_id = utils.rand_number(6)
    params = {
        'response_type': 'id_token token',
        'client_id': client_id,
        'scope': scope,
        'redirect_uri': redirect_uri,
        'nonce': f'testnonce{rand_id}',
    }
    cookies = {'sid': sess_cookie,}
    url = f"{host}{path}?{urlencode(params)}"
    lparams = add_params_for_locust(http_client, path, client_id)
    print(f'\n>>> URL ({client_id}): {url}')
    resp = http_client.get(url, cookies=cookies, **lparams)
    return resp


def validate_authorize_client(resp):
    assert resp.ok or resp.status_code == 404, f'Err reponse={resp.text} \nresp url={resp.url}'
    assert "Cookies are required" not in resp.text
    assert '>Error' not in resp.text, f'code={resp.status_code} response={resp.text}'


def submit_okta_form(http_client, html_form, client_id=CLIENT_ID):
    assert '<form' in html_form
    tree = html.fromstring(html_form)
    action_url = tree.xpath('//form/@action')[0]
    data = {
        "state": tree.xpath('//form/input[@name="state"]/@value')[0],
        "code": tree.xpath('//form/input[@name="code"]/@value')[0],
    }
    path = '/' + action_url.split('/')[-1]
    lparams = add_params_for_locust(http_client, path, client_id)
    print(f'\n>>> submitting {data} to {action_url}')
    resp = http_client.post(action_url, data, **lparams)
    return resp


def validate_okta_form(resp) -> None:
    assert resp.ok or resp.status_code == 404, f'Err reponse={resp.text} \nresp url={resp.url}'
    assert '>Error' not in resp.text, f'code={resp.status_code} response={resp.text}'


def add_params_for_locust(http_client, path, client_id) -> dict:
    params = {}
    if not 'requests.sessions' == http_client.__module__:
        params['name'] = f'{path} ({client_id})'
        params['catch_response'] = True
    return params


def extract_url_token(url) -> str:
    token_label = 'id_token='
    if token_label not in url:
        return None

    url_with_token = url.split('&')[0]
    token_val = url_with_token.split(token_label)[1]
    return token_val


def read_pub_keys(host=HOST):
    url = f'{host}/.well-known/openid-configuration/jwks'
    print(f'\n>>> reading public key from {url} ...')
    resp = requests.get(url)
    jwks = json.loads(resp.content)
    # print(f'\n>>> jwks={jwks}')

    pub_keys = {}
    for jwk in jwks['keys']:
        kid = jwk['kid']
        pub_keys[kid] = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))

    return pub_keys


def validate_jwt_guest(token, pub_keys):
    validate_jwt(token, pub_keys, CLIENT_ID_GUEST)

def validate_jwt_client(token, pub_keys):
    validate_jwt(token, pub_keys, CLIENT_ID)

def validate_jwt(token, pub_keys, audience, issuer=JWT_ISSUER) -> None:
    assert token, "No token to decode!"
    if not pub_keys:
        pub_keys = read_pub_keys()
    assert len(pub_keys)

    token_kid = jwt.get_unverified_header(token)['kid']
    pub_key = pub_keys[token_kid]
    payload = jwt.decode(token, pub_key, audience=audience, issuer=issuer, algorithms=['RS256'])
    # debug
    # payload = jwt.decode(token, verify=False)
    print(f'\n>>> token: {payload}')




