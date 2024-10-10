import aiohttp
import requests
import json
import logging
import os
import xmltodict
from zscaler.errors.http_error import HTTPError
from zscaler.errors.zscaler_api_error import ZscalerAPIError
from zscaler.exceptions import HTTPException, ZscalerAPIException

logger = logging.getLogger("zscaler-sdk-python")


import aiohttp
import json
import logging

logger = logging.getLogger(__name__)

import aiohttp
import json
import logging

logger = logging.getLogger(__name__)


class HTTPClient:
    """
    This class is the basic HTTPClient for the Zscaler Client.
    Custom HTTP clients should inherit from this class.
    """

    raise_exception = False

    def __init__(self, http_config={}):
        # Get headers from Request Executor
        self._default_headers = http_config.get("headers", {})

        # Set timeout for all HTTP requests
        request_timeout = http_config.get("requestTimeout", None)
        self._timeout = request_timeout if request_timeout and request_timeout > 0 else None

        if "proxy" in http_config:
            self._proxy = self._setup_proxy(http_config["proxy"])
        else:
            self._proxy = None
        if "sslContext" in http_config:
            self._ssl_context = http_config["sslContext"]
        else:
            self._ssl_context = None
        self._session = None

    def _setup_proxy(self, proxy):
        return proxy if proxy else None

    def set_session(self, session):
        """Set Client Session to improve performance by reusing session.

        Session should be closed manually or within context manager.
        """
        self._session = session

    def close_session(self):
        """Closes the aiohttp session"""
        if self._session:
            self._session.close()

    def send_request(self, request):
        """
        This method fires HTTP requests

        Arguments:
            request {dict} -- This dictionary contains all information needed
            for the request.
            - HTTP method (as str)
            - Headers (as dict)
            - Request body (as dict)

        Returns:
            Tuple(requests.Response, str | Exception)
            -- A tuple containing the response object and the text or an error.
        """
        try:
            logger.debug(f"Request: {request}")
            # Set headers
            headers = self._default_headers.copy()
            headers.update(request.get("headers", {}))

            # Prepare request parameters
            params = {
                "method": request["method"],
                "url": request["url"],
                "headers": headers,
                "timeout": self._timeout,
                "proxies": self._proxy,
                "verify": self._ssl_context if self._ssl_context is not None else True,
            }

            if request.get("data"):
                params["data"] = json.dumps(request["data"])
            elif request.get("form"):
                params["data"] = request["form"]

            json_data = request.get("json")
            if json_data:
                params["json"] = json_data

            # Fire request
            if self._session:
                logger.debug("Request with re-usable session.")
                response = self._session.request(**params)
            else:
                logger.debug("Request without re-usable session.")
                response = requests.request(**params)

            # Return only two values: the response and the response text
            return (response, response.text)

        except (requests.RequestException, requests.Timeout) as error:
            # Return the error as the second value
            logger.exception(error)
            return (None, error)

    @staticmethod
    def check_response_for_error(url, response_details, response_body):
        """
        Checks HTTP response for errors in the response body.

        Args:
            url (str): URL of the response
            response_details (requests.Response): Response object with details
            response_body (str): Response body in JSON format

        Returns:
            Tuple(dict repr of response (if no error), any error found)
        """
        # Log and print headers and status code
        print(f"Response Status Code: {response_details.status_code}")
        print(f"Response Headers: {response_details.headers}")
        print(f"Response Body: {response_body}")

        # Retrieve dictionary representation and response status code
        if response_details.headers.get("Content-Type") == "application/json" or response_details.headers.get("Content-Type", "").startswith("application/json"):
            try:
                formatted_response = json.loads(response_body)
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON response: {e}")
                return None, e
        else:
            formatted_response = response_body

        status_code = response_details.status_code

        # Check if the call was successful (2xx codes, including 201 for creation)
        if 200 <= status_code <= 299:
            print(f"Successful response received from {url}")
            return formatted_response, None

        # If it's not a success status code, print and treat it as an error
        print(f"Error response from URL {url}: Status {status_code}, Body {formatted_response}")

        # Handle errors if status code is not 2xx
        try:
            error = ZscalerAPIError(url, response_details, formatted_response)
            if HTTPClient.raise_exception:
                raise ZscalerAPIException(formatted_response)
        except ZscalerAPIException:
            raise
        except Exception:
            error = HTTPError(url, response_details, formatted_response)
            if HTTPClient.raise_exception:
                print(formatted_response)
                raise HTTPException(formatted_response)

        print(f"Error: {error}")
        return None, error

    @staticmethod
    def format_binary_data(data):
        """Formats binary data for multipart uploads."""
        return data  # Requests will handle this directly, no need for aiohttp-specific formatting

    def _setup_proxy(self, proxy):
        """Sets up the proxy string from the configuration or environment variables."""
        proxy_string = ""

        if proxy is None:
            if "HTTP_PROXY" in os.environ:
                proxy_string = os.environ["HTTP_PROXY"]
            if "HTTPS_PROXY" in os.environ:
                proxy_string = os.environ["HTTPS_PROXY"]
            return proxy_string if proxy_string != "" else None

        host = proxy["host"]
        port = int(proxy["port"]) if "port" in proxy else ""

        if "username" in proxy and "password" in proxy:
            username = proxy["username"]
            password = proxy["password"]
            proxy_string = f"http://{username}:{password}@{host}"
        else:
            proxy_string = f"http://{host}"

        if port:
            proxy_string += f":{port}/"

        return proxy_string if proxy_string != "" else None
