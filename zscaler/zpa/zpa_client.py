import re
import random
import time
import requests
import logging
import urllib.parse
from time import sleep
import os
from zscaler.cache.no_op_cache import NoOpCache
from zscaler.cache.zscaler_cache import ZPACache
from zscaler.ratelimiter.ratelimiter import RateLimiter
from zscaler.user_agent import UserAgent
from zscaler.utils import format_json_response, convert_keys_to_snake
from . import ZPAClient
from zscaler.zpa.app_segments import ApplicationSegmentService

# from zscaler.zpa.app_segments_pra import AppSegmentsPRAService
# from zscaler.zpa.app_segments_inspection import AppSegmentsInspectionService
from zscaler.zpa.certificates import BrowserCertificateService

# from zscaler.zpa.client_types import ClientTypesService
from zscaler.zpa.cloud_connector_groups import CloudConnectorGroupService
from zscaler.zpa.connector_groups import AppConnectorGroupService
from zscaler.zpa.connectors import AppConnectorControllerService
from zscaler.zpa.idp import IDPControllerService

# from zscaler.zpa.inspection import InspectionControllerService
# from zscaler.zpa.isolation_profile import IsolationProfileService
# from zscaler.zpa.lss import LSSConfigControllerService
from zscaler.zpa.machine_groups import MachineGroupService

# from zscaler.zpa.platforms import PlatformsService
# from zscaler.zpa.policies import PolicySetsService
from zscaler.zpa.posture_profile import PostureProfileService
from zscaler.zpa.provisioning import ProvisioningKeyService
from zscaler.zpa.saml_attributes import SamlAttributeService
from zscaler.zpa.scim_attributes import ScimAttributeHeaderService
from zscaler.zpa.scim_groups import ScimGroupService
from zscaler.zpa.segment_groups import SegmentGroupService
from zscaler.zpa.server_groups import ServerGroupService
from zscaler.zpa.servers import ApplicationServerService
from zscaler.zpa.service_edges import ServiceEdgeGroupService
from zscaler.zpa.trusted_networks import TrustedNetworksService


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

RETRYABLE_STATUS_CODES = {500, 502, 503, 504}  # Add or remove status codes as needed


def should_retry(status_code):
    """Determine if a given status code should be retried."""
    return status_code in RETRYABLE_STATUS_CODES


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

                # Check if it's a successful status code, 400, or if it shouldn't be retried
                if 299 >= resp.status_code >= 200 or resp.status_code == 400 or not should_retry(resp.status_code):
                    return resp

                if x == retries:
                    try:
                        error_msg = resp.json()
                    except Exception as e:
                        error_msg = str(e)
                    raise Exception(f"Reached max retries. Response: {error_msg}")
                else:
                    sleep = backoff_in_seconds * 2**x + random.uniform(0, 1)
                    logger.info("Args: %s, retrying after %d seconds...", str(args), sleep)
                    time.sleep(sleep)
                    x += 1

        return wrapper

    return decorator


# def delete_none(f):
#     """
#     Decorator to remove None values from a dictionary.

#     Parameters:
#     - f (function): The function to be decorated.

#     Returns:
#     - function: Decorated function.
#     """

#     def wrapper(*args, **kwargs):
#         _dict = f(*args, **kwargs)
#         if _dict is not None:
#             return delete_none_values(_dict)
#         return _dict

#     return wrapper


# def delete_none_values(_dict):
#     """
#     Recursively removes None values from a dictionary or list.

#     Parameters:
#     - _dict (Union[dict, list]): The dictionary or list to process.

#     Returns:
#     - Union[dict, list]: Processed dictionary or list without None values.
#     """

#     if isinstance(_dict, dict):
#         for key, value in list(_dict.items()):
#             if isinstance(value, (list, dict, tuple, set)):
#                 _dict[key] = delete_none_values(value)
#             elif value is None or key is None:
#                 del _dict[key]
#     elif isinstance(_dict, (list, set, tuple)):
#         _dict = type(_dict)(delete_none_values(item) for item in _dict if item is not None)
#     return _dict


# def camelcaseToSnakeCase(obj):
#     """
#     Converts keys of a dictionary from camelCase to snake_case.

#     Parameters:
#     - obj (dict): Dictionary with camelCase keys.

#     Returns:
#     - dict: Dictionary with snake_case keys.
#     """

#     new_obj = dict()
#     for key, value in obj.items():
#         if value is not None:
#             new_obj[re.sub(r"(?<!^)(?=[A-Z])", "_", key).lower()] = value
#     return new_obj


# def snakecaseToCamelcase(obj):
#     """
#     Converts keys of a dictionary from snake_case to camelCase.

#     Parameters:
#     - obj (dict): Dictionary with snake_case keys.

#     Returns:
#     - dict: Dictionary with camelCase keys.
#     """

#     new_obj = dict()
#     for key, value in obj.items():
#         if value is not None:
#             newKey = "".join(x.capitalize() or "_" for x in key.split("_"))
#             newKey = newKey[:1].lower() + newKey[1:]
#             new_obj[newKey] = value
#     return new_obj


class ZPAClientHelper(ZPAClient):
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

        # Initialize rate limiter
        # You may want to adjust these parameters as per your rate limit configuration
        self.rate_limiter = RateLimiter(
            get_limit=10,  # Adjust as per actual limit
            post_put_delete_limit=5,  # Adjust as per actual limit
            get_freq=1,  # Adjust as per actual frequency (in seconds)
            post_put_delete_freq=1,  # Adjust as per actual frequency (in seconds)
        )

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
        cache_enabled = os.environ.get("ZSCALER_CLIENT_CACHE_ENABLED", "true").lower() == "true"
        if cache is None:
            if cache_enabled:
                self.cache = ZPACache(ttl=3600, tti=1800)
            else:
                self.cache = NoOpCache()
        else:
            self.cache = cache

        # Initialize user-agent
        ua = UserAgent()
        self.user_agent = ua.get_user_agent_string()

        # login
        response = self.login()
        if response is None or response.status_code > 299 or not response.json():
            logger.error("Failed to login using provided credentials, response: %s", response)
            raise Exception("Failed to login using provided credentials.")
        self.access_token = response.json().get("access_token")
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.access_token}",
            "User-Agent": self.user_agent,
        }

    @retry_with_backoff(retries=5)
    def login(self):
        """Log in to the ZPA API and set the access token for subsequent requests."""
        data = urllib.parse.urlencode({"client_id": self.client_id, "client_secret": self.client_secret})
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "User-Agent": self.user_agent,
        }
        try:
            url = f"{self.baseurl}/signin"
            resp = requests.post(url, data=data, headers=headers, timeout=self.timeout)
            # Avoid logging all data from the response, focus on the status and a summary instead
            logger.info("Login attempt with status: %d", resp.status_code)
            return resp
        except Exception as e:
            logger.error("Login failed due to an exception: %s", str(e))
            return None

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

        # Update headers to include the user agent
        headers_with_user_agent = self.headers.copy()
        headers_with_user_agent["User-Agent"] = self.user_agent

        # Check cache before sending request
        cache_key = self.cache.create_key(url)
        if method == "GET" and self.cache.contains(cache_key):
            return self.cache.get(cache_key)

        attempts = 0
        while attempts < 5:  # Trying a maximum of 5 times
            try:
                resp = requests.request(method, url, json=data, headers=headers_with_user_agent, timeout=self.timeout)

                if resp.status_code == 429:  # HTTP Status code 429 indicates "Too Many Requests"
                    sleep_time = int(
                        resp.headers.get("Retry-After", 2)
                    )  # Default to 60 seconds if 'Retry-After' header is missing
                    logger.warning(f"Rate limit exceeded. Retrying in {sleep_time} seconds.")
                    sleep(sleep_time)
                    attempts += 1
                    continue
                else:
                    break
            except requests.RequestException as e:
                if attempts == 4:  # If it's the last attempt, raise the exception
                    logger.error(f"Failed to send {method} request to {url} after 5 attempts. Error: {str(e)}")
                    raise e
                else:
                    logger.warning(f"Failed to send {method} request to {url}. Retrying... Error: {str(e)}")
                    attempts += 1
                    sleep(5)  # Sleep for 5 seconds before retrying

        # If Non-GET call, clear the
        if method != "GET":
            self.cache.delete(cache_key)

        if resp.status_code == 400 and fail_safe:
            error_msg = f"Operation failed. API response code: {resp.status_code}"
            logger.error(error_msg)
            raise Exception(error_msg)
        # Detailed logging for request and response
        try:
            response_data = resp.json()
        except ValueError:  # Using ValueError for JSON decoding errors
            response_data = resp.text
        logger.info("Calling: %s %s. Status code: %d. Response data: %s", method, url, resp.status_code, response_data)
        # Cache the response if it's a successful GET request
        if method == "GET" and resp.status_code == 200:
            self.cache.add(cache_key, resp)
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

        # Use rate limiter before making a request
        should_wait, delay = self.rate_limiter.wait("GET")
        if should_wait:
            time.sleep(delay)

        # Now proceed with sending the request
        resp = self.send("GET", path, data, fail_safe)
        formatted_resp = format_json_response(resp, box_attrs=dict())
        return formatted_resp

    def put(self, path, data=None):
        should_wait, delay = self.rate_limiter.wait("PUT")
        if should_wait:
            time.sleep(delay)
        resp = self.send("PUT", path, data)
        formatted_resp = format_json_response(resp, box_attrs=dict())
        return formatted_resp

    def post(self, path, data=None):
        should_wait, delay = self.rate_limiter.wait("POST")
        if should_wait:
            time.sleep(delay)
        resp = self.send("POST", path, data)
        formatted_resp = format_json_response(resp, box_attrs=dict())
        return formatted_resp

    def delete(self, path, data=None):
        should_wait, delay = self.rate_limiter.wait("DELETE")
        if should_wait:
            time.sleep(delay)
        return self.send("DELETE", path, data)

    ERROR_MESSAGES = {
        "UNEXPECTED_STATUS": "Unexpected status code {status_code} received for page {page}.",
        "MISSING_DATA_KEY": "The key '{data_key_name}' was not found in the response for page {page}.",
        "EMPTY_RESULTS": "No results found for page {page}.",
    }

    def get_paginated_data(self, base_url=None, data_key_name=None, data_per_page=500, expected_status_code=200):
        """
        Fetch paginated data from the ZPA API.
        ...

        Returns:
        - list: List of fetched items.
        - str: Error message, if any occurred.
        """

        page = 1
        ret_data = []
        error_message = None

        while True:
            required_url = f"{base_url}?page={page}&pagesize={data_per_page}"
            should_wait, delay = self.rate_limiter.wait("GET")
            if should_wait:
                time.sleep(delay)

            # Now proceed with sending the request
            response = self.send("GET", required_url)

            if response.status_code != expected_status_code:
                error_message = self.ERROR_MESSAGES["UNEXPECTED_STATUS"].format(status_code=response.status_code, page=page)
                logger.error(error_message)
                break

            data = response.json().get(data_key_name)

            if data is None:
                error_message = self.ERROR_MESSAGES["MISSING_DATA_KEY"].format(data_key_name=data_key_name, page=page)
                logger.error(error_message)
                break

            if not data:  # Checks for empty data
                logger.info(self.ERROR_MESSAGES["EMPTY_RESULTS"].format(page=page))
                break

            ret_data.extend(convert_keys_to_snake(data))

            # Check for more pages
            if response.json().get("totalPages") is None or int(response.json().get("totalPages")) <= page + 1:
                break

            page += 1

        return ret_data, error_message

    @property
    def app_segments(self):
        """
        The interface object for the :ref:`ZPA Application Segments interface <zpa-app_segments>`.

        """
        return ApplicationSegmentService(self)

    # @property
    # def app_segments_pra(self):
    #     """
    #     The interface object for the :ref:`ZPA Application Segments PRA interface <zpa-app_segments_pra>`.

    #     """
    #     return AppSegmentsPRAService(self)

    # @property
    # def app_segments_inspection(self):
    #     """
    #     The interface object for the :ref:`ZPA Application Segments PRA interface <zpa-app_segments_inspection>`.

    #     """
    #     return AppSegmentsInspectionService(self)

    @property
    def certificates(self):
        """
        The interface object for the :ref:`ZPA Browser Access Certificates interface <zpa-certificates>`.

        """
        return BrowserCertificateService(self)

    # @property
    # def platforms(self):
    #     """
    #     The interface object for the :ref:`ZPA Access Policy platform interface <zpa-platforms>`.

    #     """
    #     return PlatformsService(self)

    # @property
    # def client_types(self):
    #     """
    #     The interface object for the :ref:`ZPA Access Policy client types interface <zpa-client_types>`.

    #     """
    #     return ClientTypesService(self)

    # @property
    # def isolation_profile(self):
    #     """
    #     The interface object for the :ref:`ZPA Isolation Profiles <zpa-isolation_profile>`.

    #     """
    #     return IsolationProfileService(self)

    @property
    def cloud_connector_groups(self):
        """
        The interface object for the :ref:`ZPA Cloud Connector Groups interface <zpa-cloud_connector_groups>`.

        """
        return CloudConnectorGroupService(self)

    @property
    def connector_groups(self):
        """
        The interface object for the :ref:`ZPA Connector Groups interface <zpa-connector_groups>`.

        """
        return AppConnectorGroupService(self)

    @property
    def connectors(self):
        """
        The interface object for the :ref:`ZPA Connectors interface <zpa-connectors>`.

        """
        return AppConnectorControllerService(self)

    @property
    def idp(self):
        """
        The interface object for the :ref:`ZPA IDP interface <zpa-idp>`.

        """
        return IDPControllerService(self)

    # @property
    # def inspection(self):
    #     """
    #     The interface object for the :ref:`ZPA Inspection interface <zpa-inspection>`.

    #     """
    #     return InspectionControllerService(self)

    # @property
    # def lss(self):
    #     """
    #     The interface object for the :ref:`ZIA Log Streaming Service Config interface <zpa-lss>`.

    #     """
    #     return LSSConfigControllerService(self)

    @property
    def machine_groups(self):
        """
        The interface object for the :ref:`ZPA Machine Groups interface <zpa-machine_groups>`.

        """
        return MachineGroupService(self)

    # @property
    # def policies(self):
    #     """
    #     The interface object for the :ref:`ZPA Policy Sets interface <zpa-policies>`.

    #     """
    #     return PolicySetsService(self)

    @property
    def posture_profiles(self):
        """
        The interface object for the :ref:`ZPA Posture Profiles interface <zpa-posture_profiles>`.

        """
        return PostureProfileService(self)

    @property
    def provisioning(self):
        """
        The interface object for the :ref:`ZPA Provisioning interface <zpa-provisioning>`.

        """
        return ProvisioningKeyService(self)

    @property
    def saml_attributes(self):
        """
        The interface object for the :ref:`ZPA SAML Attributes interface <zpa-saml_attributes>`.

        """
        return SamlAttributeService(self)

    @property
    def scim_attributes(self):
        """
        The interface object for the :ref:`ZPA SCIM Attributes interface <zpa-scim_attributes>`.

        """
        return ScimAttributeHeaderService(self)

    @property
    def scim_groups(self):
        """
        The interface object for the :ref:`ZPA SCIM Groups interface <zpa-scim_groups>`.

        """
        return ScimGroupService(self)

    @property
    def segment_groups(self):
        """
        The interface object for the :ref:`ZPA Segment Groups interface <zpa-segment_groups>`.

        """
        return SegmentGroupService(self)

    @property
    def server_groups(self):
        """
        The interface object for the :ref:`ZPA Server Groups interface <zpa-server_groups>`.

        """
        return ServerGroupService(self)

    @property
    def servers(self):
        """
        The interface object for the :ref:`ZPA Application Servers interface <zpa-app_servers>`.

        """
        return ApplicationServerService(self)

    @property
    def service_edges(self):
        """
        The interface object for the :ref:`ZPA Service Edges interface <zpa-service_edges>`.

        """
        return ServiceEdgeGroupService(self)

    @property
    def trusted_networks(self):
        """
        The interface object for the :ref:`ZPA Trusted Networks interface <zpa-trusted_networks>`.

        """
        return TrustedNetworksService(self)
