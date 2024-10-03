import aiohttp
import logging
import os

from zscaler.config.config_setter import ConfigSetter
from zscaler.config.config_validator import ConfigValidator
from zscaler.request_executor import RequestExecutor
from zscaler.cache.no_op_cache import NoOpCache
from zscaler.cache.zscaler_cache import ZscalerCache
from zscaler.oneapi_oauth_client import OAuth
from zscaler.logger import setup_logging

# Zscaler Private Access APIs
from zscaler.zpa.application_segment import ApplicationSegmentAPI
from zscaler.zpa.application_segment_inspection import AppSegmentsInspectionAPI
from zscaler.zpa.application_segment_pra import AppSegmentsPRAAPI
from zscaler.zpa.app_connector_schedule import AppConnectorScheduleAPI
from zscaler.zpa.app_connector_groups import AppConnectorGroupAPI
from zscaler.zpa.app_connectors import AppConnectorControllerAPI
from zscaler.zpa.authdomains import AuthDomainsAPI
from zscaler.zpa.certificates import CertificatesAPI
from zscaler.zpa.cloudbrowserisolation import CloudBrowserIsolationAPI
from zscaler.zpa.cloud_connector_groups import CloudConnectorGroupsAPI
from zscaler.zpa.emergency_access import EmergencyAccessAPI
from zscaler.zpa.idp import IDPControllerAPI
from zscaler.zpa.inspection import InspectionControllerAPI
from zscaler.zpa.lss import LSSConfigControllerAPI
from zscaler.zpa.machine_groups import MachineGroupsAPI
from zscaler.zpa.microtenants import MicrotenantsAPI
from zscaler.zpa.policies import PolicySetControllerAPI
from zscaler.zpa.posture_profiles import PostureProfilesAPI
from zscaler.zpa.privileged_remote_access import PrivilegedRemoteAccessAPI
from zscaler.zpa.provisioning import ProvisioningKeyAPI
from zscaler.zpa.saml_attributes import SAMLAttributesAPI
from zscaler.zpa.scim_attributes import ScimAttributeHeaderAPI
from zscaler.zpa.scim_groups import SCIMGroupsAPI
from zscaler.zpa.segment_groups import SegmentGroupsAPI
from zscaler.zpa.server_groups import ServerGroupsAPI
from zscaler.zpa.servers import AppServersAPI
from zscaler.zpa.service_edges import ServiceEdgeControllerAPI
from zscaler.zpa.service_edge_groups import ServiceEdgeGroupAPI
from zscaler.zpa.service_edge_schedule import ServiceEdgeSchedule
from zscaler.zpa.trusted_networks import TrustedNetworksAPI


class Client(
    ApplicationSegmentAPI,
    AppSegmentsInspectionAPI,
    AppSegmentsPRAAPI,
    AppConnectorGroupAPI,
    AppConnectorControllerAPI,
    AppConnectorScheduleAPI,
    AuthDomainsAPI,
    CertificatesAPI,
    CloudConnectorGroupsAPI,
    EmergencyAccessAPI,
    IDPControllerAPI,
    InspectionControllerAPI,
    CloudBrowserIsolationAPI,
    LSSConfigControllerAPI,
    MachineGroupsAPI,
    MicrotenantsAPI,
    PolicySetControllerAPI,
    PostureProfilesAPI,
    PrivilegedRemoteAccessAPI,
    ProvisioningKeyAPI,
    SAMLAttributesAPI,
    ScimAttributeHeaderAPI,
    SCIMGroupsAPI,
    SegmentGroupsAPI,
    ServerGroupsAPI,
    AppServersAPI,
    ServiceEdgeControllerAPI,
    ServiceEdgeGroupAPI,
    ServiceEdgeSchedule,
    TrustedNetworksAPI,
):
    """A Zscaler client object"""

    def __init__(self, user_config: dict = {}):
        super().__init__()

        # Initialize Config Setter and apply user config
        client_config_setter = ConfigSetter()
        client_config_setter._apply_config({"client": user_config})
        self._config = client_config_setter.get_config()

        # Ensure 'customerId' is either in the config or retrieved from the environment variable
        self._customer_id = self._config["client"].get("customerId", os.getenv("ZSCALER_CUSTOMER_ID"))

        if not self._customer_id:
            raise ValueError(
                "Missing 'customerId'. It should be either provided in the config or set as 'ZSCALER_CUSTOMER_ID' in environment variables."
            )

        # Prune unnecessary configuration fields
        self._config = client_config_setter._prune_config(self._config)

        # Validate configuration
        ConfigValidator(self._config)

        self._client_id = self._config["client"]["clientId"]
        self._client_secret = self._config["client"].get("clientSecret", None)
        self._private_key = self._config["client"].get("privateKey", None)
        self._vanity_domain = self._config["client"]["vanityDomain"]
        self._cloud = self._config["client"].get("cloud", "PRODUCTION")
        self._auth_token = None
        self._service = self._config["client"].get("service", "zpa")
        self._api_version = self._config["client"].get("api_version", "v1")  # Default to v1 for ZPA

        # Set the base URL based on cloud and vanity domain
        # self._base_url = self._build_base_url(self._vanity_domain, self._cloud)
        
        # Set base URL based on service, cloud, and API version
        self._base_url = self._build_service_base_url()
        
        # Handle cache
        cache = NoOpCache()
        if self._config["client"]["cache"]["enabled"]:
            if user_config.get("cacheManager") is None:
                time_to_idle = self._config["client"]["cache"]["defaultTti"]
                time_to_live = self._config["client"]["cache"]["defaultTtl"]
                cache = ZscalerCache(time_to_live, time_to_idle)
            else:
                cache = user_config.get("cacheManager")

        # Set request executor
        self._request_executor = user_config.get("requestExecutor", RequestExecutor)(
            self._config, cache, user_config.get("httpClient", None)
        )

        # Setup logging
        setup_logging()

        if self._config["client"]["logging"]["enabled"]:
            logger = logging.getLogger("zscaler-sdk-python")
            logger.disabled = False

    def _build_service_base_url(self):
        """
        Builds the base URL based on the service (ZPA, ZIA, ZCC).
        This will be used for all API calls after authentication.
        """
        # Start with cloud handling
        if self._cloud.upper() != "PRODUCTION":
            base_url = f"https://api.{self._cloud.lower()}.zsapi.net"
        else:
            base_url = "https://api.zsapi.net"

        # Handle service-specific base URLs
        if self._service == "zpa":
            base_url += f"/zpa/mgmtconfig/{self._api_version}/admin/customers/{self._customer_id}"
        elif self._service == "zia":
            base_url += "/zia/api/v1"
        elif self._service == "zcc":
            base_url += "/zcc/papi/public"
        else:
            raise ValueError(f"Unsupported service: {self._service}")
        
        return base_url
    
    def __aenter__(self):
        """Automatically create and set session within context manager."""
        self._session = aiohttp.ClientSession()
        self._request_executor.set_session(self._session)
        return self

    def __aexit__(self, exc_type, exc_val, exc_tb):
        """Automatically close session within context manager."""
        self._session.close()

    def authenticate(self):
        """
        Handles authentication by using either client_secret or private_key.
        """
        oauth_client = OAuth(self._request_executor, self._config)
        self._auth_token = oauth_client._get_access_token()

        # Update the default headers directly by setting the Authorization Bearer token
        self._request_executor._default_headers.update({"Authorization": f"Bearer {self._auth_token}"})

    """
    Getters
    """

    def get_config(self):
        return self._config

    def get_base_url(self):
        """
        Returns the base URL for the API requests.
        """
        return self._base_url

    def get_request_executor(self):
        return self._request_executor

    """
    Misc
    """

    def set_custom_headers(self, headers):
        self._request_executor.set_custom_headers(headers)

    def clear_custom_headers(self):
        self._request_executor.clear_custom_headers()

    def get_custom_headers(self):
        return self._request_executor.get_custom_headers()

    def get_default_headers(self):
        return self._request_executor.get_default_headers()

    """
    Private methods
    """

    def _build_base_url(self, vanity_domain, cloud):
        """
        Constructs the base URL based on the vanity domain and cloud environment.

        Args:
            vanity_domain (str): The vanity domain for the Zscaler instance.
            cloud (str): The cloud environment (e.g., "PRODUCTION", "BETA").

        Returns:
            str: The base URL.
        """
        base_url = f"https://{vanity_domain}.zslogin.net/oauth2/v1/token"

        # Adjust the base URL based on cloud, if it's not "PRODUCTION"
        if cloud and cloud.upper() != "PRODUCTION":
            base_url = f"https://api.{cloud.lower()}.zsapi.net"

        return base_url
