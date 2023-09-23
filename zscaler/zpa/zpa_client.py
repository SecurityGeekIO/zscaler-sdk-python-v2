import re
import json
import random
import time
import urllib.parse
import requests
import logging
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

def retry_with_backoff(retries=5, backoff_in_seconds=1):
    def decorator(f):
        def wrapper(*args, **kwargs):
            x = 0
            while True:
                resp = f(*args, **kwargs)
                if resp.status_code < 299 or resp.status_code == 400:
                    return resp
                if x == retries:
                    raise Exception("Reached max retries: %s" % (resp.json()))
                else:
                    sleep = backoff_in_seconds * 2 ** x + random.uniform(0, 1)
                    logger.info("Args: %s, retrying after %d seconds...", str(args), sleep)
                    time.sleep(sleep)
                    x += 1
        return wrapper
    return decorator


def delete_none(f):
    def wrapper(*args, **kwargs):
        _dict = f(*args, **kwargs)
        if _dict is not None:
            return deleteNone(_dict)
        return _dict
    return wrapper


def deleteNone(_dict):
    if isinstance(_dict, dict):
        for key, value in list(_dict.items()):
            if isinstance(value, (list, dict, tuple, set)):
                _dict[key] = deleteNone(value)
            elif value is None or key is None:
                del _dict[key]
    elif isinstance(_dict, (list, set, tuple)):
        _dict = type(_dict)(deleteNone(item) for item in _dict if item is not None)
    return _dict


def camelcaseToSnakeCase(obj):
    new_obj = dict()
    for key, value in obj.items():
        if value is not None:
            new_obj[re.sub(r"(?<!^)(?=[A-Z])", "_", key).lower()] = value
    return new_obj


def snakecaseToCamelcase(obj):
    new_obj = dict()
    for key, value in obj.items():
        if value is not None:
            newKey = "".join(x.capitalize() or "_" for x in key.split("_"))
            newKey = newKey[:1].lower() + newKey[1:]
            new_obj[newKey] = value
    return new_obj


class ZPAClientHelper:
    def __init__(self, cache=None):
        """
        Initialize the ZPAClientHelper with optional caching.

        Args:
            cache (Cache, optional): A caching object. Defaults to NoOpCache.
        """
        # Check the environment variable to determine if caching is enabled
        cache_enabled = os.environ.get('ZSCALER_CLIENT_CACHE_ENABLED', 'true').lower() == 'true'

        if cache is None:
            if cache_enabled:
                self.cache = ZPACache(ttl=3600, tti=1800)  # You can set your desired default TTL and TTI
            else:
                self.cache = NoOpCache()
        else:
            self.cache = cache

    def make_request(self, url, method, data=None):
        cache_key = self.cache.create_key(url)

        # Check if data is in cache before making a request
        if self.cache.contains(cache_key):
            return self.cache.get(cache_key)

        # Here, perform the actual HTTP request using your preferred method
        # For the sake of this example, let's assume the result is stored in `response`
        response = ...  # make the actual request

        # Cache the response
        self.cache.add(cache_key, response)

        return response

    def __init__(self, client_id, client_secret, customer_id, cloud):
        self.timeout = 240
        self.client_id = client_id
        self.client_secret = client_secret
        self.customer_id = customer_id
        self.cloud = cloud
        # Select the appropriate URL
        self.baseurl = BASE_URLS.get(self.cloud, BASE_URLS["PRODUCTION"])

        # login
        response = self.login()
        if response is None or response.status_code > 299 or response.json is None:
            logger.error(
                "Failed to login using provided credentials, please verify validity of API ZPA_CLIENT_ID & ZPA_CLIENT_SECRET. response: %s",
                response
            )
            self.module.fail_json(
                msg="Failed to login using provided credentials, please verify validity of API ZPA_CLIENT_ID & ZPA_CLIENT_SECRET. response: %s"
                % (response)
            )
        resp_json = response.json()

        self.access_token = resp_json.get("access_token")
        logger.info("access_token: '%s'", self.access_token)
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer %s" % (self.access_token),
        }

    @retry_with_backoff(retries=5)
    def login(self):
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
                url, str(data), resp.content
            )
            return resp
        except Exception as e:
            logger.error("Login failed: %s", str(e))
            return None

    @retry_with_backoff(retries=5)
    def send(self, method, path, data=None, fail_safe=False):
        url = f"{self.baseurl}/{path.lstrip('/')}"
        resp = requests.request(
            method, url, json=data, headers=self.headers, timeout=self.timeout
        )
        logger.info(
            "Calling: %s %s %s. Response: %s",
            method, url, str(data), str(resp.json())
        )
        if resp.status_code == 400 and fail_safe:
            logger.error("Operation failed. API response: %s", resp.json())
        return resp

    def get(self, path, data=None, fail_safe=False):
        return self.send("GET", path, data, fail_safe)

    def put(self, path, data=None):
        return self.send("PUT", path, data)

    def post(self, path, data=None):
        return self.send("POST", path, data)

    def delete(self, path, data=None):
        return self.send("DELETE", path, data)

    def get_paginated_data(self, base_url=None, data_key_name=None, data_per_page=500, expected_status_code=200):
        page = 0
        has_next = True
        ret_data = []
        status_code = None
        response = None
        while has_next or status_code != expected_status_code:
            required_url = f"{base_url}?page={page}&pagesize={data_per_page}"
            response = self.get(required_url)
            status_code = response.status_code
            if status_code != expected_status_code:
                break
            page += 1
            if response.json().get(data_key_name) is None:
                has_next = False
                continue
            ret_data.extend(response.json()[data_key_name])
            has_next = response.json().get("totalPages") is not None and int(response.json()["totalPages"]) != 0 and int(response.json()["totalPages"]) < page

        if status_code != expected_status_code:
            msg = f"Failed to fetch {data_key_name} from {base_url}"
            if response:
                msg += f" due to error : {response.json().get('message')}"
            logger.error(msg)
        return ret_data
