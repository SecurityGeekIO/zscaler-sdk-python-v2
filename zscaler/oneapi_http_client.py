import json
import requests
import logging
import os
import time
from zscaler.errors.http_error import HTTPError
from zscaler.errors.zscaler_api_error import ZscalerAPIError
from zscaler.exceptions import HTTPException, ZscalerAPIException
from zscaler.logger import dump_request, dump_response

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

        # Setup SSL context or handle disableHttpsCheck
        if "sslContext" in http_config:
            self._ssl_context = http_config["sslContext"]  # Use the custom SSL context
        elif "disableHttpsCheck" in http_config and http_config["disableHttpsCheck"]:
            self._ssl_context = False  # Disable SSL certificate validation if disableHttpsCheck is true
        else:
            self._ssl_context = True  # Enable SSL certificate validation by default

        self._session = None

    def _setup_proxy(self, proxy):
        return proxy if proxy else None

    def set_session(self, session):
        """Set Client Session to improve performance by reusing session.

        Session should be closed manually or within context manager.
        """
        self._session = session

    def close_session(self):
        """Closes the session if one was used."""
        if self._session:
            self._session.close()

    def send_request(self, request):
        """
        This method fires HTTP requests.

        Arguments:
            request {dict} -- This dictionary contains all information needed for the request.

        Returns:
            Tuple(requests.Response, str | Exception) -- A tuple containing the response object and the text or an error.
        """
        try:
            # Sanitize the authorization header before logging
            headers = request.get("headers", {}).copy()
            if "Authorization" in headers:
                headers["Authorization"] = "Bearer <TOKEN>"

            # Prepare request parameters
            params = {
                "method": request["method"],
                "url": request["url"],
                "headers": request.get("headers", {}),
                "timeout": self._timeout,
                "proxies": {"http": self._proxy, "https": self._proxy} if self._proxy else None,
                "verify": self._ssl_context,
            }

            # Always use 'json' for JSON payloads
            if request.get("json"):
                params["json"] = request["json"]
            elif request.get("data"):
                params["data"] = request["data"]
            elif request.get("form"):
                params["data"] = request["form"]
            if request["params"]:
                params["params"] = request["params"]

            dump_request(
                logger,
                params["url"],
                params["method"],
                params.get("json"),
                params.get("params"),
                params.get("headers"),
                request["uuid"],
                body=not ("/zscsb" in request["url"]),
            )
            start_time = time.time()  # Capture the start time before sending the request
            response = self._session.request(**params) if self._session else requests.request(**params)
            logger.info(f"Received response with status code: {response.status_code}")
            dump_response(
                logger,
                request["url"],
                request["method"],
                response,
                request.get("params"),
                request["uuid"],
                start_time,
            )
            return (response, None)

        except (requests.RequestException, requests.Timeout) as error:
            logger.error(f"Request to {request['url']} failed: {error}")
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
        # Check if response is JSON and parse it
        if "application/json" in response_details.headers.get("Content-Type", ""):
            try:
                formatted_response = json.loads(response_body)
                # logger.debug("Successfully parsed JSON response")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                return None, e
        else:
            formatted_response = response_body

        if 200 <= response_details.status_code < 300:
            return formatted_response, None

        logger.error(f"Error response from {url}: {response_details.status_code} - {formatted_response}")

        status_code = response_details.status_code

        # check if call was succesful
        if 200 <= status_code <= 299:
            return (formatted_response, None)
        else:
            # create errors
            try:
                error = ZscalerAPIError(url, response_details, formatted_response)
                if HTTPClient.raise_exception:
                    raise ZscalerAPIException(formatted_response)
            except ZscalerAPIException:
                raise
            except Exception:
                error = HTTPError(url, response_details, formatted_response)
                if HTTPClient.raise_exception:
                    logger.exception(formatted_response)
                    raise HTTPException(formatted_response)
            logger.error(error)
            return (None, error)

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
