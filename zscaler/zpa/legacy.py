import logging
import os
import time
import urllib.parse

import requests

from zscaler import __version__
from zscaler.cache.no_op_cache import NoOpCache
from zscaler.cache.zscaler_cache import ZscalerCache
from zscaler.constants import ZPA_BASE_URLS, DEV_AUTH_URL, MAX_RETRIES
from zscaler.errors.http_error import HTTPError, ZscalerAPIError
from zscaler.exceptions.exceptions import HTTPException, ZscalerAPIException
from zscaler.logger import setup_logging
from zscaler.ratelimiter.ratelimiter import RateLimiter
from zscaler.user_agent import UserAgent
from zscaler.utils import (
    is_token_expired,
    retry_with_backoff,
)

# Setup the logger
setup_logging(logger_name="zscaler-sdk-python")
logger = logging.getLogger("zscaler-sdk-python")

# -*- coding: utf-8 -*-

# Copyright (c) 2023, Zscaler Inc.
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.


class LegacyZPAClientHelper():
    """A Controller to access Endpoints in the Zscaler Private Access (ZPA) API.

    The ZPA object stores the session token and simplifies access to API interfaces within ZPA.

    Attributes:
        client_id (str): The ZPA API client ID generated from the ZPA console.
        client_secret (str): The ZPA API client secret generated from the ZPA console.
        customer_id (str): The ZPA tenant ID found in the Administration > Company menu in the ZPA console.
        cloud (str): The Zscaler cloud for your tenancy, accepted values are:

            * ``production``
            * ``beta``
            * ``gov``
            * ``govus``
            * ``zpatwo``
    """

    def __init__(
        self,
        client_id,
        client_secret,
        customer_id,
        cloud,
        microtenant_id=None,
        timeout=240,
        cache=None,
        fail_safe=False,
    ):
        # Initialize rate limiter
        self.rate_limiter = RateLimiter(
            get_limit=20,  # Adjusted to allow 20 GET requests per 10 seconds
            post_put_delete_limit=
            10,  # Adjusted to allow 10 POST/PUT/DELETE requests per 10 seconds
            get_freq=10,  # Adjust frequency to 10 seconds
            post_put_delete_freq=10,  # Adjust frequency to 10 seconds
        )

        if cloud not in ZPA_BASE_URLS:
            valid_clouds = ", ".join(ZPA_BASE_URLS.keys())
            raise ValueError(
                f"The provided ZPA_CLOUD value '{cloud}' is not supported. "
                f"Please use one of the following supported values: {valid_clouds}"
            )

        self.baseurl = ZPA_BASE_URLS.get(cloud, ZPA_BASE_URLS["PRODUCTION"])
        self.timeout = timeout
        self.client_id = client_id
        self.client_secret = client_secret
        self.customer_id = customer_id
        self.cloud = cloud
        self.microtenant_id = microtenant_id or os.getenv("ZPA_MICROTENANT_ID")
        self.fail_safe = fail_safe

        cache_enabled = os.environ.get("ZSCALER_CLIENT_CACHE_ENABLED",
                                       "true").lower() == "true"
        if cache is None:
            if cache_enabled:
                ttl = int(
                    os.environ.get("ZSCALER_CLIENT_CACHE_DEFAULT_TTL", 3600))
                tti = int(
                    os.environ.get("ZSCALER_CLIENT_CACHE_DEFAULT_TTI", 1800))
                self.cache = ZscalerCache(ttl=ttl, tti=tti)
            else:
                self.cache = NoOpCache()
        else:
            self.cache = cache

        ua = UserAgent()
        self.user_agent = ua.get_user_agent_string()
        self.access_token = None
        self.headers = {}
        self.refreshToken()

    def refreshToken(self):
        if not self.access_token or is_token_expired(self.access_token):
            response = self.login()
            if response is None or response.status_code > 299 or not response.json(
            ):
                logger.error(
                    "Failed to login using provided credentials, response: %s",
                    response)
                raise Exception("Failed to login using provided credentials.")
            self.access_token = response.json().get("access_token")
            self.headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {self.access_token}",
                "User-Agent": self.user_agent,
            }

    @retry_with_backoff(MAX_RETRIES)
    def login(self):
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "User-Agent": self.user_agent,
        }
        try:
            url = f"{self.baseurl}/signin"
            if self.cloud == "DEV":
                url = DEV_AUTH_URL + "?grant_type=CLIENT_CREDENTIALS"
            data = urllib.parse.urlencode(params)
            resp = requests.post(url,
                                 data=data,
                                 headers=headers,
                                 timeout=self.timeout)
            logger.info("Login attempt with status: %d", resp.status_code)
            return resp
        except Exception as e:
            logger.error("Login failed due to an exception: %s", str(e))
            return None

    def send(
        self,
        method,
        path,
        json=None,
        params=None,
    ):
        api = self.baseurl
        if params is None:
            params = {}

        if json and "microtenant_id" in json:
            microtenant_id = json.pop("microtenant_id")
        else:
            microtenant_id = self.microtenant_id

        if microtenant_id:
            params["microtenantId"] = microtenant_id
        base_url = f"{api}/{path.lstrip('/')}"
        url = base_url
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"
        headers_with_user_agent = self.headers.copy()
        headers_with_user_agent["User-Agent"] = self.user_agent
        cache_key = self.cache.create_key(url, None)
        request = {
            "method": method,
            "url": base_url,
            "json": json,
            "params": params,
            "headers": headers_with_user_agent,
        }
        if method == "GET" and self.cache.contains(cache_key):
            resp = self.cache.get(cache_key)
            return resp, request

        attempts = 0
        while attempts < 5:
            try:
                self.refreshToken()
                should_wait, delay = self.rate_limiter.wait(method)
                if should_wait:
                    logger.warning(
                        f"Rate limit exceeded. Retrying in {delay} seconds.")
                    time.sleep(delay)
                resp = requests.request(
                    method,
                    url,
                    json=json,
                    params=None,
                    headers=headers_with_user_agent,
                    timeout=self.timeout,
                )
                if resp.status_code == 429:
                    retry_after = resp.headers.get("Retry-After")
                    if retry_after:
                        try:
                            sleep_time = int(retry_after)
                        except ValueError:
                            sleep_time = int(retry_after[:-1])
                        logger.warning(
                            f"Rate limit exceeded. Retrying in {sleep_time} seconds."
                        )
                        time.sleep(sleep_time)
                    else:
                        time.sleep(60)
                    attempts += 1
                    continue
                else:
                    break
            except requests.RequestException as e:
                if attempts == 4:
                    logger.error(
                        f"Failed to send {method} request to {url} after 5 attempts. Error: {str(e)}"
                    )
                    raise e
                else:
                    logger.warning(
                        f"Failed to send {method} request to {url}. Retrying... Error: {str(e)}"
                    )
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
        return resp, request
