import logging
import os
import time
import urllib.parse
import uuid

import requests
from box import BoxList

from zscaler import __version__
from zscaler.cache.no_op_cache import NoOpCache
from zscaler.cache.zscaler_cache import ZscalerCache
from zscaler.errors.http_error import HTTPError, ZscalerAPIError
from zscaler.exceptions.exceptions import HTTPException, ZscalerAPIException
from zscaler.logger import setup_logging
from zscaler.ratelimiter.ratelimiter import RateLimiter
from zscaler.user_agent import UserAgent
from zscaler.utils import (
    convert_keys_to_snake,
    dump_request,
    dump_response,
    format_json_response,
    is_token_expired,
    retry_with_backoff,
    snake_to_camel,
)
from zscaler.zcc.client import ZCCClient

# Setup the logger
setup_logging(logger_name="zscaler-sdk-python")
logger = logging.getLogger("zscaler-sdk-python")


class ZCCClientHelper(ZCCClient):
    """A Controller to access Endpoints in the ZCC API.

    The ZCC object stores the session token and simplifies access to API interfaces within ZCC.

    Attributes:
        apikey (str): The ZCC API client ID generated from the ZCC console.
        secret_key (str): The ZCC API client secret generated from the ZCC console.
        cloud (str): The ZCC cloud.
    """

    def __init__(self, cloud=None, timeout=240, cache=None, fail_safe=False, **kw):
        # Initialize rate limiter
        self.rate_limiter = RateLimiter(
            get_limit=20,  # Adjusted to allow 20 GET requests per 10 seconds
            post_put_delete_limit=10,  # Adjusted to allow 10 POST/PUT/DELETE requests per 10 seconds
            get_freq=10,  # Adjust frequency to 10 seconds
            post_put_delete_freq=10,  # Adjust frequency to 10 seconds
        )

        self.timeout = timeout
        self.apikey = kw.get("apikey", os.getenv("ZCC_API_KEY"))
        self.secret_key = kw.get("secret_key", os.getenv("ZCC_SECRET_KEY"))
        self.cloud = os.getenv("ZCC_CLOUD") if os.getenv("ZCC_CLOUD") is not None else cloud
        self.login_url = f"https://api-mobile.{self.cloud}.net/papi/auth/v1/login"
        self.url = f"https://api-mobile.{self.cloud}.net/papi/public/v1"
        self.fail_safe = fail_safe

        cache_enabled = os.environ.get("ZSCALER_CLIENT_CACHE_ENABLED", "true").lower() == "true"
        if cache is None:
            if cache_enabled:
                ttl = int(os.environ.get("ZSCALER_CLIENT_CACHE_DEFAULT_TTL", 3600))
                tti = int(os.environ.get("ZSCALER_CLIENT_CACHE_DEFAULT_TTI", 1800))
                self.cache = ZscalerCache(ttl=ttl, tti=tti)
            else:
                self.cache = NoOpCache()
        else:
            self.cache = cache

        ua = UserAgent()
        self.user_agent = ua.get_user_agent_string()
        self.auth_token = None
        self.headers = {}
        self.refreshToken()

    def __enter__(self):
        self.refreshToken()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.debug("deauthenticating...")

    def refreshToken(self):
        if not self.auth_token or is_token_expired(self.auth_token):
            response = self.login()
            if response is None or response.status_code > 299 or not response.json():
                logger.error("Failed to login using provided credentials, response: %s", response)
                raise Exception("Failed to login using provided credentials.")
            self.auth_token = response.json().get("jwtToken")
            self.headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "auth-token": f"{self.auth_token}",
                "User-Agent": self.user_agent,
            }

    @retry_with_backoff(retries=5)
    def login(self):
        data = {"apiKey": self.apikey, "secretKey": self.secret_key}
        headers = {
            "Content-Type": "application/json",
            "Accept": "*/*",
            "User-Agent": self.user_agent,
        }
        try:
            url = self.login_url
            resp = requests.post(url, json=data, headers=headers, timeout=self.timeout)
            logger.info("Login attempt with status: %d", resp.status_code)
            return resp
        except Exception as e:
            logger.error("Login failed due to an exception: %s", str(e))
            return None

    def send(self, method, path, json=None, params=None):
        api = self.url
        if params is None:
            params = {}
        url = f"{api}/{path.lstrip('/')}"
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"

        start_time = time.time()
        headers_with_user_agent = self.headers.copy()
        headers_with_user_agent["User-Agent"] = self.user_agent
        request_uuid = str(uuid.uuid4())
        dump_request(logger, url, method, json, None, headers_with_user_agent, request_uuid)
        cache_key = self.cache.create_key(url, None)
        if method == "GET" and self.cache.contains(cache_key):
            resp = self.cache.get(cache_key)
            dump_response(
                logger=logger,
                url=url,
                method=method,
                params=None,
                resp=resp,
                request_uuid=request_uuid,
                start_time=start_time,
                from_cache=True,
            )
            return resp

        attempts = 0
        while attempts < 5:
            try:
                self.refreshToken()
                should_wait, delay = self.rate_limiter.wait(method)
                if should_wait:
                    logger.warning(f"Rate limit exceeded. Retrying in {delay} seconds.")
                    time.sleep(delay)
                resp = requests.request(
                    method,
                    url,
                    json=json,
                    params=None,
                    headers=headers_with_user_agent,
                    timeout=self.timeout,
                )
                dump_response(
                    logger=logger,
                    url=url,
                    params=None,
                    method=method,
                    resp=resp,
                    request_uuid=request_uuid,
                    start_time=start_time,
                )
                if resp.status_code == 429:
                    retry_after = resp.headers.get("Retry-After")
                    if retry_after:
                        try:
                            sleep_time = int(retry_after)
                        except ValueError:
                            sleep_time = int(retry_after[:-1])
                        logger.warning(f"Rate limit exceeded. Retrying in {sleep_time} seconds.")
                        time.sleep(sleep_time)
                    else:
                        time.sleep(60)
                    attempts += 1
                    continue
                else:
                    break
            except requests.RequestException as e:
                if attempts == 4:
                    logger.error(f"Failed to send {method} request to {url} after 5 attempts. Error: {str(e)}")
                    raise e
                else:
                    logger.warning(f"Failed to send {method} request to {url}. Retrying... Error: {str(e)}")
                    attempts += 1
                    time.sleep(5)

        if method != "GET":
            logger.info(f"Clearing cache for non-GET request: {method} {url}")
            self.cache.clear()

        try:
            response_data = resp.json()
        except ValueError:
            response_data = resp.text
        if 200 > resp.status_code or resp.status_code > 299:
            try:
                error = ZscalerAPIError(url, resp, response_data)
                if self.fail_safe:
                    raise ZscalerAPIException(response_data)
            except ZscalerAPIException:
                raise
            except Exception:
                error = HTTPError(url, resp, response_data)
                if self.fail_safe:
                    logger.error(response_data)
                    raise HTTPException(response_data)
            logger.error(error)
        if method == "GET" and resp.status_code == 200:
            self.cache.add(cache_key, resp)
        return resp

    def get(self, path, json=None, params=None):
        """
        Send a GET request to the ZCC API.

        Parameters:
        path (str): API endpoint path.
        json (dict, optional): Request payload. Defaults to None.
        params (dict, optional): Query parameters. Defaults to None.

        Returns:
        dict: Formatted JSON response from the API.
        """
        should_wait, delay = self.rate_limiter.wait("GET")
        if should_wait:
            time.sleep(delay)
        resp = self.send("GET", path, json, params)
        formatted_resp = format_json_response(resp, box_attrs=dict())
        return formatted_resp

    def put(self, path, json=None, params=None):
        """
        Send a PUT request to the ZCC API.

        Parameters:
        path (str): API endpoint path.
        json (dict, optional): Request payload. Defaults to None.
        params (dict, optional): Query parameters. Defaults to None.

        Returns:
        dict: Formatted JSON response from the API.
        """
        should_wait, delay = self.rate_limiter.wait("PUT")
        if should_wait:
            time.sleep(delay)
        resp = self.send("PUT", path, json, params)
        formatted_resp = format_json_response(resp, box_attrs=dict())
        return formatted_resp

    def post(self, path, json=None, params=None):
        """
        Send a POST request to the ZCC API.

        Parameters:
        path (str): API endpoint path.
        json (dict, optional): Request payload. Defaults to None.
        params (dict, optional): Query parameters. Defaults to None.

        Returns:
        dict: Formatted JSON response from the API.
        """
        should_wait, delay = self.rate_limiter.wait("POST")
        if should_wait:
            time.sleep(delay)
        resp = self.send("POST", path, json, params)
        formatted_resp = format_json_response(resp, box_attrs=dict())
        return formatted_resp

    def delete(self, path, json=None, params=None):
        """
        Send a DELETE request to the ZCC API.

        Parameters:
        path (str): API endpoint path.
        json (dict, optional): Request payload. Defaults to None.
        params (dict, optional): Query parameters. Defaults to None.

        Returns:
        Response: Response object from the DELETE request.
        """
        should_wait, delay = self.rate_limiter.wait("DELETE")
        if should_wait:
            time.sleep(delay)
        return self.send("DELETE", path, json, params)

    def get_paginated_data(
        self,
        path=None,
        params=None,
        search=None,
        search_field="name",
        page=None,
        pagesize=20,
    ):
        """
        Fetches paginated data from the ZCC API based on specified parameters and handles various types of API pagination.

        Args:
            path (str): The API endpoint path to send requests to.
            params (dict): Initial set of query parameters for the API request.
            search (str): Search query to filter the results based on specific conditions.
            search_field (str): The field name against which to search the query. Default is "name".
            page (int): Specific page number to fetch. Overrides automatic pagination.
            pagesize (int): Number of items per page, default is 20 as per API specification, maximum is 500.

        Returns:
            tuple: A tuple containing:
                - BoxList: A list of fetched items wrapped in a BoxList for easy access.
                - str: An error message if any occurred during the data fetching process.

        Raises:
            Logs errors and warnings through the configured logger when requests fail or if no data is found.
        """
        logger = logging.getLogger(__name__)

        ERROR_MESSAGES = {
            "UNEXPECTED_STATUS": "Unexpected status code {status_code} received for page {page}.",
            "MISSING_DATA_KEY": "The key 'list' was not found in the response for page {page}.",
            "EMPTY_RESULTS": "No results found for all requested pages.",
        }

        if params is None:
            params = {}

        params["page"] = page if page is not None else 1  # Default to page 1 if not specified
        params["pagesize"] = min(pagesize if pagesize is not None else 20, 500)  # Apply maximum constraint and handle default

        if search:
            api_search_field = snake_to_camel(search_field)
            params["search"] = f"{api_search_field} EQ {search}"

        total_collected = 0
        ret_data = []

        try:
            while True:
                should_wait, delay = self.rate_limiter.wait("GET")
                if should_wait:
                    time.sleep(delay)

                response = self.send("GET", path=path, params=params)

                if response.status_code > 299:
                    error_msg = ERROR_MESSAGES["UNEXPECTED_STATUS"].format(
                        status_code=response.status_code, page=params["page"]
                    )
                    logger.error(error_msg)
                    return BoxList([]), error_msg

                response_data = response.json()
                data = response_data.get("list", [])
                if not data and (params["page"] == 1):
                    error_msg = ERROR_MESSAGES["EMPTY_RESULTS"]
                    logger.warn(error_msg)
                    return BoxList([]), error_msg

                data = convert_keys_to_snake(data)
                ret_data.extend(data)
                total_collected += len(data)

                next_page = response_data.get("nextPage")
                if not next_page:
                    break

                params["page"] = next_page if params["page"] is None else params["page"] + 1

        finally:
            time.sleep(2)  # Ensure a delay between requests regardless of outcome

        if not ret_data:
            error_msg = ERROR_MESSAGES["EMPTY_RESULTS"]
            logger.warn(error_msg)
            return BoxList([]), error_msg

        return BoxList(ret_data), None
