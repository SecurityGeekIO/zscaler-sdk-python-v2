import re
import random
import time
import requests
import logging
import urllib.parse
import os
from zscaler.cache.no_op_cache import NoOpCache
from zscaler.cache.zscaler_cache import ZPACache

# Setup the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Endpoint configuration from Go
BASE_URLS = {
    "PRODUCTION": "https://config.private.zscaler.com",
    "BETA": "https://config.zpabeta.net",
    "GOV": "https://config.zpagov.net",
    "GOVUS": "https://config.zpagov.us",
    "PREVIEW": "https://config.zpapreview.net",
    "DEV": "https://public-api.dev.zpath.net",
    "QA": "https://config.qa.zpath.net",
    "QA2": "https://pdx2-zpa-config.qa2.zpath.net",
}

def retry_with_backoff(method_type="GET", retries=5, backoff_in_seconds=0.5):

    """
    Decorator to retry a function in case of an unsuccessful response.

    Parameters:
    - method_type (str): The HTTP method. Defaults to "GET".
    - retries (int): Number of retries before giving up. Defaults to 5.
    - backoff_in_seconds (float): Initial wait time (in seconds) before retry. Defaults to 0.5.

    Returns:
    - function: Decorated function with retry and backoff logic.
    """

    if method_type != "GET":
        retries = min(retries, 3)  # more conservative retry count for non-GET

    def decorator(f):
        def wrapper(*args, **kwargs):
            x = 0
            while True:
                resp = f(*args, **kwargs)

                # Check if it's a rate limit status code or other criteria
                if 299 >= resp.status_code >= 200 or resp.status_code == 400:
                    return resp

                if x == retries:
                    try:
                        error_msg = resp.json()
                    except Exception as e:
                        error_msg = str(e)
                    raise Exception(f"Reached max retries. Response: {error_msg}")
                else:
                    sleep = backoff_in_seconds * 2 ** x + random.uniform(0, 1)
                    logger.info("Args: %s, retrying after %d seconds...", str(args), sleep)
                    time.sleep(sleep)
                    x += 1
        return wrapper
    return decorator



def delete_none(f):
    """
    Decorator to remove None values from a dictionary.

    Parameters:
    - f (function): The function to be decorated.

    Returns:
    - function: Decorated function.
    """

    def wrapper(*args, **kwargs):
        _dict = f(*args, **kwargs)
        if _dict is not None:
            return delete_none_values(_dict)
        return _dict
    return wrapper

def delete_none_values(_dict):
    """
    Recursively removes None values from a dictionary or list.

    Parameters:
    - _dict (Union[dict, list]): The dictionary or list to process.

    Returns:
    - Union[dict, list]: Processed dictionary or list without None values.
    """

    if isinstance(_dict, dict):
        for key, value in list(_dict.items()):
            if isinstance(value, (list, dict, tuple, set)):
                _dict[key] = delete_none_values(value)
            elif value is None or key is None:
                del _dict[key]
    elif isinstance(_dict, (list, set, tuple)):
        _dict = type(_dict)(delete_none_values(item) for item in _dict if item is not None)
    return _dict


def camelcaseToSnakeCase(obj):
    """
    Converts keys of a dictionary from camelCase to snake_case.

    Parameters:
    - obj (dict): Dictionary with camelCase keys.

    Returns:
    - dict: Dictionary with snake_case keys.
    """

    new_obj = dict()
    for key, value in obj.items():
        if value is not None:
            new_obj[re.sub(r"(?<!^)(?=[A-Z])", "_", key).lower()] = value
    return new_obj


def snakecaseToCamelcase(obj):
    """
    Converts keys of a dictionary from snake_case to camelCase.

    Parameters:
    - obj (dict): Dictionary with snake_case keys.

    Returns:
    - dict: Dictionary with camelCase keys.
    """

    new_obj = dict()
    for key, value in obj.items():
        if value is not None:
            newKey = "".join(x.capitalize() or "_" for x in key.split("_"))
            newKey = newKey[:1].lower() + newKey[1:]
            new_obj[newKey] = value
    return new_obj


class ZPAClientHelper:
    """
    Client helper for ZPA operations.

    Attributes:
    - client_id (str): The client ID.
    - client_secret (str): The client secret.
    - customer_id (str): The customer ID.
    - cloud (str): The cloud endpoint to be used.
    - timeout (int): Request timeout duration in seconds.
    - cache (object): Cache object to be used.
    - baseurl (str): Base URL for API requests.
    - access_token (str): Access token for API requests.
    - headers (dict): Headers for API requests.
    """

    def __init__(self, client_id, client_secret, customer_id, cloud, timeout=240, cache=None):
        """
        Initialize ZPAClientHelper.

        Parameters:
        - client_id (str): The client ID.
        - client_secret (str): The client secret.
        - customer_id (str): The customer ID.
        - cloud (str): The cloud endpoint to be used.
        - cache (object, optional): Cache object. Defaults to None.
        """
        # Validate cloud value
        if cloud not in BASE_URLS:
            valid_clouds = ", ".join(BASE_URLS.keys())
            raise ValueError(
                f"The provided ZPA_CLOUD value '{cloud}' is not supported. "
                f"Please use one of the following supported values: {valid_clouds}"
            )

        # Continue with existing initialization...
        # Select the appropriate URL
        self.baseurl = BASE_URLS.get(cloud, BASE_URLS["PRODUCTION"])

        self.timeout = timeout
        self.client_id = client_id
        self.client_secret = client_secret
        self.customer_id = customer_id
        self.cloud = cloud

        # Cache setup
        cache_enabled = os.environ.get('ZSCALER_CLIENT_CACHE_ENABLED', 'true').lower() == 'true'
        if cache is None:
            if cache_enabled:
                self.cache = ZPACache(ttl=3600, tti=1800)
            else:
                self.cache = NoOpCache()
        else:
            self.cache = cache

        # login
        response = self.login()
        if response is None or response.status_code > 299 or not response.json():
            logger.error("Failed to login using provided credentials, response: %s", response)
            raise Exception("Failed to login using provided credentials.")
        self.access_token = response.json().get("access_token")
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }

    @retry_with_backoff(retries=5)
    def login(self):
        """Log in to the ZPA API and set the access token for subsequent requests."""
        data = urllib.parse.urlencode(
            {"client_id": self.client_id, "client_secret": self.client_secret}
        )
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }
        try:
            url = f"{self.baseurl}/signin"
            resp = requests.post(url, data=data, headers=headers, timeout=self.timeout)
            logger.info(
                "Calling: POST %s %s. Response: %s",
                url, str(data), str(resp.json())
            )
            return resp
        except Exception as e:
            logger.error("Login failed: %s", str(e))
            return None

    @retry_with_backoff(retries=5)
    def send(self, method, path, data=None, fail_safe=False):
        """
        Send a request to the ZPA API.

        Parameters:
        - method (str): The HTTP method.
        - path (str): API endpoint path.
        - data (dict, optional): Request payload. Defaults to None.
        - fail_safe (bool, optional): Log an error and continue on failure. Defaults to False.

        Returns:
        - Response: Response object from the request.
        """
        url = f"{self.baseurl}/{path.lstrip('/')}"

        # Check cache before sending request
        cache_key = self.cache.create_key(url)
        if method == "GET" and self.cache.contains(cache_key):
            return self.cache.get(cache_key)

        resp = requests.request(
            method, url, json=data, headers=self.headers, timeout=self.timeout
        )

        # If Non-GET call, clear the cache
        if method != "GET":
            self.cache.clear()

        # Cache the response if it's a successful GET request
        if method == "GET" and resp.status_code == 200:
            self.cache.add(cache_key, resp)

        # Detailed logging for request and response
        try:
            response_data = resp.json()
        except Exception:
            response_data = resp.text
        logger.info(
            "Calling: %s %s. Data sent: %s. Response: %s",
            method, url, str(data), str(response_data)
        )

        if resp.status_code == 400 and fail_safe:
            error_msg = f"Operation failed. API response: {response_data}"
            logger.error(error_msg)
            raise Exception(error_msg)

        return resp

    def get(self, path, data=None, fail_safe=False):
        """
        Send a GET request to the ZPA API.

        Parameters:
        - path (str): API endpoint path.
        - data (dict, optional): Request payload. Defaults to None.
        - fail_safe (bool, optional): Log an error and continue on failure. Defaults to False.

        Returns:
        - Response: Response object from the request.
        """
        return self.send("GET", path, data, fail_safe)

    def put(self, path, data=None):
        """
        Send a PUT request to the ZPA API.

        Parameters:
        - path (str): API endpoint path.
        - data (dict, optional): Request payload. Defaults to None.

        Returns:
        - Response: Response object from the request.
        """
        return self.send("PUT", path, data)

    def post(self, path, data=None):
        """
        Send a POST request to the ZPA API.

        Parameters:
        - path (str): API endpoint path.
        - data (dict, optional): Request payload. Defaults to None.

        Returns:
        - Response: Response object from the request.
        """
        return self.send("POST", path, data)

    def delete(self, path, data=None):
        """
        Send a DELETE request to the ZPA API.

        Parameters:
        - path (str): API endpoint path.
        - data (dict, optional): Request payload. Defaults to None.

        Returns:
        - Response: Response object from the request.
        """

        return self.send("DELETE", path, data)

def get_paginated_data(self, base_url=None, data_key_name=None, data_per_page=500, expected_status_code=200):
    """
    Fetch paginated data from the ZPA API.

    Parameters:
    - base_url (str, optional): Base API URL. Defaults to None.
    - data_key_name (str, optional): Key name in the response containing the data. Defaults to None.
    - data_per_page (int, optional): Number of items to fetch per page. Defaults to 500.
    - expected_status_code (int, optional): Expected HTTP status code for a successful response. Defaults to 200.

    Returns:
    - list: List of fetched items.
    - str: Error message, if any occurred.
    """

    page = 0
    ret_data = []
    error_message = None

    while True:
        required_url = f"{base_url}?page={page}&pagesize={data_per_page}"
        response = self.get(required_url)

        if response.status_code != expected_status_code:
            error_message = f"Unexpected status code {response.status_code} on page {page}."
            logger.error(error_message)
            break

        if response.json().get(data_key_name) is None:
            error_message = f"Missing data key '{data_key_name}' in response on page {page}."
            logger.error(error_message)
            break

        ret_data.extend(response.json()[data_key_name])

        # Check for more pages
        if response.json().get("totalPages") is None or int(response.json().get("totalPages")) <= page + 1:
            break

        page += 1

    return ret_data, error_message