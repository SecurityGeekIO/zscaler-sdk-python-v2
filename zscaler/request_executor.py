import logging
import time
from zscaler.oneapi_http_client import HTTPClient
from zscaler.oneapi_oauth_client import OAuth
from zscaler.user_agent import UserAgent
from zscaler.oneapi_oauth_client import OAuth
from zscaler.utils import convert_date_time_to_seconds
from zscaler.error_messages import ERROR_MESSAGE_429_MISSING_DATE_X_RESET
from http import HTTPStatus

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


class RequestExecutor:
    """
    This class handles all of the requests sent by the Zscaler SDK Client (ZIA, ZPA, ZCC, etc.).
    """

    BASE_URL = "https://api.zsapi.net"  # Default base URL for API calls

    def __init__(self, config, cache, http_client=None):
        """
        Constructor for Request Executor object for Zscaler SDK Client.

        Args:
            config (dict): This dictionary contains the configuration of the Request Executor.
            cache (object): Cache object for storing request responses.
            http_client (object, optional): Custom HTTP client for making requests.
        """
        # Validate and set request timeout
        self._request_timeout = config["client"].get("requestTimeout", 240)  # Default to 240 seconds
        if self._request_timeout < 0:
            raise ValueError(f"Invalid request timeout: {self._request_timeout}. Must be greater than zero.")

        # Validate and set max retries for rate limiting
        self._max_retries = config["client"]["rateLimit"].get("maxRetries", 2)
        if self._max_retries < 0:
            raise ValueError(f"Invalid max retries: {self._max_retries}. Must be 0 or greater.")

        # Set configuration and cache
        self._config = config
        self._cache = cache

        # Retrieve the cloud and customer ID
        self.cloud = self._config["client"].get("cloud", "production").lower()
        self.customer_id = self._config["client"].get("customerId")
        if not self.customer_id:
            raise ValueError("Missing 'customerId' in the configuration. Ensure it is provided.")

        # Initialize base URL based on the cloud setting
        self._base_url = self.get_base_url(self.cloud)

        # OAuth2 setup
        self._oauth = OAuth(self, self._config)
        self._access_token = None

        # Set default headers from config
        self._default_headers = {
            "User-Agent": config["client"].get("userAgent", UserAgent),
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        # Initialize the HTTP client, considering proxy and SSL context from config
        http_client_impl = http_client or HTTPClient
        self._http_client = http_client_impl(
            {
                "requestTimeout": self._request_timeout,
                "headers": self._default_headers,
                "proxy": self._config["client"].get("proxy"),
                "sslContext": self._config["client"].get("sslContext"),
            }
        )

        # Initialize custom headers as an empty dictionary
        self._custom_headers = {}

    def get_base_url(self, cloud: str) -> str:
        """
        Gets the appropriate base URL based on the cloud value.

        Args:
            cloud (str): The cloud environment (e.g., "beta", "production").

        Returns:
            str: The constructed base URL for API requests.
        """
        if cloud and cloud != "production":
            return f"https://api.{cloud}.zsapi.net"
        return self.BASE_URL

    def detect_service_type(self, endpoint: str) -> str:
        """
        Detects the service type (ZPA, ZIA, ZCC) based on the endpoint prefix.

        Args:
            endpoint (str): The API endpoint being accessed.

        Returns:
            str: The service type ('zpa', 'zia', 'zcc').
        """
        path = endpoint.lstrip("/")

        # Logic to detect the service type based on the path
        if "zia" in path:
            return "zia"
        elif "zpa" in path:
            return "zpa"
        elif "zcc" in path:
            return "zcc"
        else:
            raise ValueError(f"Unsupported service detected in the endpoint: {endpoint}")

    def get_service_base_url(self, service: str, cloud: str = "production") -> str:
        """
        Returns the appropriate base URL for the service.

        Args:
            service (str): The service type (zpa, zia, zcc).
            cloud (str): The cloud environment (production, beta, etc.).

        Returns:
            str: The constructed base URL for the service.
        """
        if cloud != "production":
            return f"https://api.{cloud}.zsapi.net"
        return self.BASE_URL

    def create_request(
        self,
        method: str,
        endpoint: str,
        api_version: str = None,  # Optional API version for ZPA services
        body: dict = None,
        headers: dict = {},
        params: dict = {},
        oauth: bool = False,
        keep_empty_params: bool = False,
    ):
        """
        Creates and sends the HTTP request with proper service detection and API version handling.

        Args:
            method (str): HTTP Method (GET, POST, PUT, DELETE).
            endpoint (str): Full URL or endpoint of the request.
            api_version (str): Optional API version for ZPA services.
            body (dict, optional): Request body.
            headers (dict, optional): Request headers.
            params (dict, optional): Query parameters.
            oauth (bool, optional): Should use OAuth2 authentication.
            keep_empty_params (bool, optional): Whether to include empty parameters in the body.

        Returns:
            dict: Prepared request or exception raised during execution.
        """
        logger.debug(f"Initial endpoint before modification: {endpoint}")

        # Detect the service type from the relative endpoint (before constructing the full URL)
        service_type = self.detect_service_type(endpoint)
        logger.debug(f"Service type detected: {service_type}")

        # Get the appropriate base URL based on the service and cloud environment
        base_url = self.get_base_url(self.cloud)

        # Handle customer ID and API version for ZPA
        if service_type == "zpa":
            customer_id = self._config["client"].get("customerId")
            if not customer_id:
                raise ValueError("ZPA customer ID is required but not provided in the configuration.")

            # Append the customer ID and API version to the ZPA endpoint
            if api_version:
                endpoint = f"/zpa/{api_version}/admin/customers/{customer_id}/{endpoint.lstrip('/')}"
            else:
                endpoint = f"/zpa/mgmtconfig/v1/admin/customers/{customer_id}/{endpoint.lstrip('/')}"

        # Ensure the final URL is constructed by appending the base URL
        final_url = f"{base_url}/{endpoint.lstrip('/')}"

        logger.debug(f"Final URL after service detection and version handling: {final_url}")

        # OAuth
        self._oauth = OAuth(self, self._config)
            
        # Set headers, including OAuth token if required
        headers = {**self._default_headers, **headers}
        if oauth:
            headers["Authorization"] = f"Bearer {self._oauth._get_access_token()}"

        logger.debug(f"Final Request Headers: {headers}")

        # Clean empty parameters from the request body if required
        if body and not keep_empty_params:
            body = self._clean_empty_params(body)

        logger.debug(f"Request body after cleaning empty params: {body}")

        # Construct the request
        request = {
            "method": method,
            "url": final_url,  # Use the fully constructed URL
            "headers": headers,
            "data": body,
            "params": params,
        }

        return request, None

    def clear_empty_params(self, body: dict):
        """
        Removes all key-value pairs where value is empty, i.e. empty string, list or dict.

        Args:
            body (dict): request body to be cleared

        Returns:
            dict: body without empty values.
        """
        if isinstance(body, dict):
            return {
                k: v
                for k, v in ((k, self.clear_empty_params(v)) for k, v in body.items())
                if v or v == 0 or v is False
            }
        if isinstance(body, list):
            return [v for v in map(self.clear_empty_params, body) if v or v == 0 or v is False]
        return body

    def clear_empty_params(self, body: dict):
        """
        Removes all key-value pairs where value is empty (i.e., empty string, list, or dict).

        Args:
            body (dict): Request body to be cleared.

        Returns:
            dict: Body without empty values.
        """
        if isinstance(body, dict):
            return {k: v for k, v in ((k, self.clear_empty_params(v)) for k, v in body.items()) if v or v == 0 or v is False}
        if isinstance(body, list):
            return [v for v in map(self.clear_empty_params, body) if v or v == 0 or v is False]
        return body

    def execute(self, request):
        """
        High-level request execution method. Performs the API call and handles rate limits.

        Args:
            request (dict): Dictionary object containing request details.

        Returns:
            Response object or raises an error.
        """
        print(f"Executing request: {request}")

        # Fire the request
        request, response, response_body, error = self.fire_request(request)

        # Check for an error during execution
        if error is not None:
            print(f"Error during request execution: {error}")
            return None, error

        # Check for any errors in the HTTP response
        response_data, error = self._http_client.check_response_for_error(request["url"], response, response_body)

        # If there was an error in the response, print it
        if error:
            print(f"Error in response: {error}")
            return None, error

        # Print successful response
        print(f"Successful response from {request['url']}")
        print(f"Response Data: {response_data}")

        return response_data, None

    def fire_request(self, request):
        """
        Send request using HTTP client.

        Args:
            request (dict): HTTP request in dictionary format.

        Returns:
            request, response, response_body, error
        """
        # Log the full request details before sending it
        logger.debug(f"Sending request: {request}")

        # Explicitly print the request before it is fired
        print(f"Sending request: {request}")

        # Pass both URL and params to create_key
        url_cache_key = self._cache.create_key(request["url"], request["params"])

        # Remove cache entry if not a GET call
        if request["method"].upper() != "GET":
            self._cache.delete(url_cache_key)

        # Check if response exists in cache
        if self._cache.contains(url_cache_key):
            return self._cache.get(url_cache_key), None

        # Send actual request
        request, response, response_body, error = self.fire_request_helper(request, 0, time.time())

        if error is None and request["method"].upper() == "GET" and 200 <= response.status_code < 300:
            self._cache.add(url_cache_key, (response, response_body))

        return request, response, response_body, error

    def fire_request_helper(self, request, attempts, request_start_time):
        """
        Helper method to perform HTTP call with retries if needed.

        Args:
            request (dict): HTTP request representation.
            attempts (int): Number of attempted HTTP calls so far.
            request_start_time (float): Original start time of request.

        Returns:
            Tuple of request, response object, response body, and error.
        """
        # Get start request time
        current_req_start_time = time.time()
        max_retries = self._max_retries
        req_timeout = self._request_timeout

        if req_timeout > 0 and (current_req_start_time - request_start_time) > req_timeout:
            # Timeout is hit for request
            return None, None, None, Exception("Request Timeout exceeded.")

        response, error = self._http_client.send_request(request)

        if error:
            return None, None, None, error

        headers = response.headers

        if attempts < max_retries and self.is_retryable_status(response.status_code):
            date_time = headers.get("Date", "")
            if date_time:
                date_time = convert_date_time_to_seconds(date_time)

            # Get X-Rate-Limit-Reset header
            retry_limit_reset_headers = list(map(float, headers.getall("X-Rate-Limit-Reset", [])))
            retry_limit_reset_headers.extend(list(map(float, headers.getall("x-rate-limit-reset", []))))
            retry_limit_reset = min(retry_limit_reset_headers) if len(retry_limit_reset_headers) > 0 else None

            # Retry based on Retry-After header
            retry_after = headers.get("Retry-After") or headers.get("retry-after")
            if retry_after:
                retry_after = int(retry_after.strip("s"))

            # Check for rate limit error and calculate backoff
            if not date_time or not retry_limit_reset:
                return None, response, response.text, Exception(ERROR_MESSAGE_429_MISSING_DATE_X_RESET)

            check_429 = self.is_too_many_requests(response.status_code, response.text)
            if check_429:
                backoff_seconds = self.calculate_backoff(retry_limit_reset, date_time)
                logger.info(f"Hit rate limit. Retrying request in {backoff_seconds} seconds.")
                logger.debug(f"Value of retry_limit_reset: {retry_limit_reset}")
                logger.debug(f"Value of date_time: {date_time}")
                self.pause_for_backoff(backoff_seconds)
                if (current_req_start_time + backoff_seconds) - request_start_time > req_timeout and req_timeout > 0:
                    return None, response, response.text, Exception("Request Timeout exceeded.")

            # Retry the request
            attempts += 1
            request["headers"].update({"X-Transaction-Id": headers.get("X-Transaction-Id", "")})

            return self.fire_request_helper(request, attempts, request_start_time)

        return request, response, response.text, None

    def is_retryable_status(self, status):
        """
        Checks if HTTP status is retryable.

        Retryable statuses: 429, 503, 504
        """
        return status is not None and status in (
            HTTPStatus.TOO_MANY_REQUESTS,
            HTTPStatus.SERVICE_UNAVAILABLE,
            HTTPStatus.GATEWAY_TIMEOUT,
        )

    def is_too_many_requests(self, status, response):
        """
        Determines if HTTP request has been made too many times

        Args:
            status (int): HTTP response status code
            response (json): Response Body

        Returns:
            bool: Returns True if this request has been called too many times
        """
        return response is not None and status == HTTPStatus.TOO_MANY_REQUESTS

    def calculate_backoff(self, retry_limit_reset, date_time):
        """
        Calculate the backoff time based on rate limit reset and date time.

        Args:
            retry_limit_reset: The reset time from X-Rate-Limit-Reset header.
            date_time: The current time from the Date header.

        Returns:
            int: The number of seconds to backoff.
        """
        return retry_limit_reset - date_time + 1

    def pause_for_backoff(self, backoff_time):
        """
        Pauses the execution for the backoff period.

        Args:
            backoff_time (int): Number of seconds to pause.
        """
        time.sleep(float(backoff_time))

    def set_custom_headers(self, headers):
        """
        Set custom headers for all future requests.
        """
        self._custom_headers.update(headers)

    def clear_custom_headers(self):
        """
        Clear custom headers set for future requests.
        """
        self._custom_headers.clear()

    def get_custom_headers(self):
        """
        Get the current custom headers.
        """
        return self._custom_headers

    # --- CRUD FUNCTIONS (For ZIA and ZPA) ---

    def get(self, url, params=None):
        """
        Send a GET request.

        Args:
            url (str): Full URL for the request.
            params (dict, optional): Query parameters.

        Returns:
            dict: Response.
        """
        return self.create_request("GET", url, params=params)

    def post(self, url, body=None, params=None):
        """
        Send a POST request.

        Args:
            url (str): Full URL for the request.
            body (dict, optional): Request body.
            params (dict, optional): Query parameters.

        Returns:
            dict: Response.
        """
        return self.create_request("POST", url, body=body, params=params)

    def put(self, url, body=None, params=None):
        """
        Send a PUT request.

        Args:
            url (str): Full URL for the request.
            body (dict, optional): Request body.
            params (dict, optional): Query parameters.

        Returns:
            dict: Response.
        """
        return self.create_request("PUT", url, body=body, params=params)

    def delete(self, url, params=None):
        """
        Send a DELETE request.

        Args:
            url (str): Full URL for the request.
            params (dict, optional): Query parameters.

        Returns:
            dict: Response.
        """
        return self.create_request("DELETE", url, params=params)
