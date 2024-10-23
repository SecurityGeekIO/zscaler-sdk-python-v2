import logging
import time
import uuid
from zscaler.oneapi_http_client import HTTPClient
from zscaler.oneapi_response import ZscalerAPIResponse
from zscaler.oneapi_oauth_client import OAuth
from zscaler.user_agent import UserAgent
from zscaler.utils import convert_date_time_to_seconds
from zscaler.error_messages import ERROR_MESSAGE_429_MISSING_DATE_X_RESET
from http import HTTPStatus
from zscaler.helpers import convert_keys_to_snake_case, to_lower_camel_case

logger = logging.getLogger(__name__)


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
        logger.info("Initializing RequestExecutor with provided configuration.")

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

        # Retrieve cloud, service, and customer ID (optional)
        self.cloud = self._config["client"].get("cloud", "production").lower()
        self.service = self._config["client"].get("service", "zia")  # Default to ZIA
        self.customer_id = self._config["client"].get("customerId")  # Optional for ZIA/ZCC
        self.microtenant_id = self._config["client"].get("microtenantId")  # Optional for ZIA/ZCC

        # Initialize base URL based on the cloud setting
        self._base_url = self.get_base_url(self.cloud)
        logger.debug(f"Base URL set to: {self._base_url}")

        # OAuth2 setup
        self._oauth = OAuth(self, self._config)
        self._access_token = None

        # Set default headers from config
        self._default_headers = {
            "User-Agent": UserAgent(config["client"].get("userAgent", None)).get_user_agent_string(),
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
        logger.debug(f"Determining base URL for cloud: {cloud}")
        if cloud and cloud != "production":
            return f"https://api.{cloud}.zsapi.net"
        return self.BASE_URL

    def get_service_type(self, url):
        logger.debug(f"Determining service type for URL: {url}")
        if "/zia" in url:
            return "zia"
        elif "/zcc" in url:
            return "zcc"
        elif "/zpa" in url:
            return "zpa"
        else:
            raise ValueError(f"Unsupported service: {url}")

    def create_request(
        self,
        method: str,
        endpoint: str,
        body: dict = None,
        headers: dict = {},
        params: dict = {},
    ):
        logger.info(f"Creating request for endpoint: {endpoint} with method: {method}")
        # Get the appropriate base URL based on the service and cloud environment
        base_url = self.get_base_url(self.cloud)

        # Ensure the final URL is constructed by appending the base URL
        final_url = f"{base_url}/{endpoint.lstrip('/')}"

        logger.debug(f"Final URL after service detection and version handling: {final_url}")

        # OAuth
        self._oauth = OAuth(self, self._config)

        # Set headers, including OAuth token if required
        headers = {**self._default_headers, **headers}
        headers["Authorization"] = f"Bearer {self._oauth._get_access_token()}"

        # Convert body and params to camelCase before sending
        if body:
            body = {to_lower_camel_case(k): v for k, v in body.items()}

        if params:
            params = {to_lower_camel_case(k): v for k, v in params.items()}
        if "/zpa/" in endpoint:
            # Check for microtenantId in body, params, and config (in that order)
            microtenant_id = None
            if body and "microtenantId" in body and body["microtenantId"]:
                microtenant_id = body["microtenantId"]
            elif params and "microtenantId" in params and params["microtenantId"]:
                microtenant_id = params["microtenantId"]
            elif self.microtenant_id:
                microtenant_id = self.microtenant_id

            # Set microtenantId in params if found
            if microtenant_id:
                params["microtenantId"] = microtenant_id
        else:
            if params.get("microtenantId") is not None:
                del params["microtenantId"]

        # Construct the request dictionary
        request = {
            "method": method,
            "url": final_url,
            "json": body,  # Always use 'json' for JSON payloads
            "params": params,
            "headers": headers,
            "uuid": uuid.uuid4(),
        }

        logger.debug(f"Request created: {request}")
        return request, None

    def execute(self, request, response_type=None):
        """
        High-level request execution method.

        Args:
            request (dict): Dictionary object containing request details.
            response_type (type): The data type to return (e.g., RuleLabels).

        Returns:
            ZscalerAPIResponse or error
        """
        logger.info(f"Executing request to URL: {request['url']}")
        logger.debug(f"Request details: {request}")

        # Fire the request
        try:
            request, response, response_body, error = self.fire_request(request)
        except Exception as ex:
            logger.error(f"Exception during HTTP request: {ex}")
            return None, ex

        # Check for an error during execution
        if error is not None:
            logger.error(f"Error during request execution: {error}")
            return None, error

        # Handle 204 No Content case globally
        if response.status_code == 204:
            logger.debug(f"Received 204 No Content from {request['url']}")
            # Return None for the object, as there's no content to parse
            return None, None

        # Check for any errors in the HTTP response
        try:
            response_data, error = self._http_client.check_response_for_error(request["url"], response, response_body)
        except Exception as ex:
            logger.error(f"Exception while checking response for errors: {ex}")
            return None, ex

        # If there was an error in the response, return it
        if error:
            logger.error(f"Error in HTTP response: {error}")
            return None, error

        logger.info(f"Successful response from {request['url']}")
        logger.debug(f"Response Data: {response_data}")

        # Convert response body keys from camelCase to snake_case if response_data is a dict or list
        if isinstance(response_data, (dict, list)):
            response_data = convert_keys_to_snake_case(response_data)

        # Return the ZscalerAPIResponse object (this will handle pagination)
        return (
            ZscalerAPIResponse(
                request_executor=self,
                req=request,
                res_details=response,
                response_body=response_body,
                data_type=response_type,
                service_type=self.get_service_type(request["url"]),
            ),
            None,
        )

    def fire_request(self, request):
        """
        Send request using HTTP client.

        Args:
            request (dict): HTTP request in dictionary format.

        Returns:
            request, response, response_body, error
        """
        logger.info(f"Sending request to URL: {request['url']}")
        logger.debug(f"Request details: {request}")

        # Pass both URL and params to create_key
        url_cache_key = self._cache.create_key(request["url"], request["params"])

        # Remove cache entry if not a GET call
        if request["method"].upper() != "GET":
            self._cache.delete(url_cache_key)

        # Check if response exists in cache
        if self._cache.contains(url_cache_key):
            logger.info(f"Cache hit for URL: {request['url']}")
            return self._cache.get(url_cache_key), None

        # Send actual request
        request, response, response_body, error = self.fire_request_helper(request, 0, time.time())

        if error is None and request["method"].upper() == "GET" and 200 <= response.status_code < 300:
            logger.info(f"Caching response for URL: {request['url']}")
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
        logger.debug(f"Attempting request to URL: {request['url']}, attempt {attempts + 1}")
        current_req_start_time = time.time()
        max_retries = self._max_retries
        req_timeout = self._request_timeout

        if req_timeout > 0 and (current_req_start_time - request_start_time) > req_timeout:
            logger.error("Request Timeout exceeded.")
            return None, None, None, Exception("Request Timeout exceeded.")

        response, error = self._http_client.send_request(request)

        if error:
            logger.error(f"Error sending request: {error}")
            return None, None, None, error

        headers = response.headers

        if attempts < max_retries and self.is_retryable_status(response.status_code):
            date_time = headers.get("Date", "")
            if date_time:
                date_time = convert_date_time_to_seconds(date_time)

            # Extract the x-ratelimit-reset value and convert it to float
            retry_limit_reset_header = headers.get("x-ratelimit-reset")  # Get the value for x-ratelimit-reset
            if retry_limit_reset_header is not None:  # Check if the header exists
                retry_limit_reset_headers = [float(retry_limit_reset_header)]  # Convert to float
            else:
                retry_limit_reset_headers = []  # Default to an empty list if not present

            retry_after = headers.get("Retry-After") or headers.get("retry-after")
            if retry_after:
                retry_after = int(retry_after.strip("s"))

            if not date_time or not retry_limit_reset_headers:
                logger.error("Missing Date or X-Rate-Limit-Reset headers.")
                return None, response, response.text, Exception(ERROR_MESSAGE_429_MISSING_DATE_X_RESET)
            # x-ratelimit-reset: The time (in seconds) remaining in the current window after which the rate limit resets.
            # so no need to substract the date unix time
            backoff_seconds = retry_limit_reset_headers[0]
            logger.info(f"Hit rate limit. Retrying request in {backoff_seconds} seconds.")
            time.sleep(backoff_seconds)
            attempts += 1
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
        logger.debug(f"Setting custom headers: {headers}")
        self._custom_headers.update(headers)

    def set_session(self, session):
        logger.debug("Setting HTTP client session.")
        self._http_client.set_session(session)

    def clear_custom_headers(self):
        """
        Clear custom headers set for future requests.
        """
        logger.debug("Clearing custom headers.")
        self._custom_headers.clear()

    def get_custom_headers(self):
        """
        Get the current custom headers.
        """
        logger.debug("Getting custom headers.")
        return self._custom_headers
