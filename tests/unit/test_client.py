import pytest
import requests_mock
import logging
logging.basicConfig(level=logging.INFO)
from zscaler.zpa.zpa_client import ZPAClientHelper

print("Running test_client.py")

BASE_URL = "https://config.private.zscaler.com"
POST_ENDPOINT = f"{BASE_URL}/post_endpoint"
PUT_ENDPOINT = f"{BASE_URL}/put_endpoint"
DELETE_ENDPOINT = f"{BASE_URL}/delete_endpoint"
LOGIN_URL = f"{BASE_URL}/signin"
TEST_ENDPOINT = f"{BASE_URL}/test_endpoint"

@pytest.fixture

def client():
    client_id = "dummy_client_id"
    client_secret = "dummy_client_secret"
    customer_id = "dummy_customer_id"
    cloud = "PRODUCTION"

    with requests_mock.Mocker() as m:
        mock_response = {"access_token": "dummy_token"}
        m.post(LOGIN_URL, json=mock_response)
        client = ZPAClientHelper(client_id, client_secret, customer_id, cloud)
        if hasattr(client, 'user_agent'):
            client._user_agent = client.user_agent  # Store the user agent to access it in tests
    return client

def test_login(client):
    print("Executing test_login...")
    assert client.access_token == "dummy_token", "Login failed or token not set correctly."

def test_get(client):
    mock_data = {"data": "sample_data"}

    with requests_mock.Mocker() as m:
        req_headers = {}

        def get_response(request, _):
            req_headers.update(request.headers)
            return mock_data

        m.get(TEST_ENDPOINT, json=get_response)
        response = client.get("/test_endpoint")

        logging.info("Request Headers: %s", req_headers)

    assert req_headers.get('User-Agent') == client._user_agent, "User Agent header not set correctly."
    assert response.json() == mock_data, "Failed to fetch data correctly."


# The rest of the tests ...

def test_post(client):
    mock_data = {"result": "post_success"}
    payload = {"key": "value"}

    with requests_mock.Mocker() as m:
        m.post(POST_ENDPOINT, json=mock_data)
        response = client.post("/post_endpoint", data=payload)
        assert 'User-Agent' in m.last_request.headers
        assert m.last_request.headers['User-Agent'] == client._user_agent, "User Agent header not set correctly."

    assert response.json() == mock_data, "Failed to post data correctly."

# Similar modifications for PUT and DELETE methods

def test_put(client):
    mock_data = {"result": "put_success"}
    payload = {"key": "value"}

    with requests_mock.Mocker() as m:
        m.put(PUT_ENDPOINT, json=mock_data)
        response = client.put("/put_endpoint", data=payload)
        assert 'User-Agent' in m.last_request.headers
        assert m.last_request.headers['User-Agent'] == client._user_agent, "User Agent header not set correctly."

    assert response.json() == mock_data, "Failed to update data correctly."

def test_delete(client):
    mock_data = {"result": "delete_success"}

    with requests_mock.Mocker() as m:
        m.delete(DELETE_ENDPOINT, json=mock_data)
        response = client.delete("/delete_endpoint")
        assert 'User-Agent' in m.last_request.headers
        assert m.last_request.headers['User-Agent'] == client._user_agent, "User Agent header not set correctly."

    assert response.json() == mock_data, "Failed to delete data correctly."
