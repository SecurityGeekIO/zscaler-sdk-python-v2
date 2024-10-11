import requests
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

# Zscaler Internet Access APIs
from zscaler.zia.activate import ActivationAPI
from zscaler.zia.admin_roles import AdminRolesAPI
from zscaler.zia.admin_users import AdminUsersAPI
from zscaler.zia.apptotal import AppTotalAPI
from zscaler.zia.audit_logs import AuditLogsAPI
from zscaler.zia.authentication_settings import AuthenticationSettingsAPI
from zscaler.zia.cloud_apps import CloudAppsAPI
from zscaler.zia.cloudappcontrol import CloudAppControlAPI
from zscaler.zia.device_management import DeviceManagementAPI
from zscaler.zia.dlp_dictionary import DLPDictionaryAPI
from zscaler.zia.dlp_engine import DLPEngineAPI
from zscaler.zia.dlp_resources import DLPResourcesAPI
from zscaler.zia.dlp_templates import DLPTemplatesAPI
from zscaler.zia.firewall import FirewallPolicyAPI
from zscaler.zia.forwarding_control import ForwardingControlAPI
from zscaler.zia.isolation_profile import CBIProfileAPI
from zscaler.zia.locations import LocationsAPI
from zscaler.zia.rule_labels import RuleLabelsAPI
from zscaler.zia.sandbox import CloudSandboxAPI
from zscaler.zia.security_policy_settings import SecurityPolicyAPI
from zscaler.zia.ssl_inspection import SSLInspectionAPI
from zscaler.zia.traffic import TrafficForwardingAPI
from zscaler.zia.url_categories import URLCategoriesAPI
from zscaler.zia.url_filtering import URLFilteringAPI
from zscaler.zia.user_management import UserManagementAPI
from zscaler.zia.workload_groups import WorkloadGroupsAPI
from zscaler.zia.zpa_gateway import ZPAGatewayAPI


# Zscaler Client Connector APIs
class Client(
    # ZPA API Resources
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
    # ZIA API Resources
    ActivationAPI,
    AdminRolesAPI,
    AdminUsersAPI,
    AppTotalAPI,
    AuditLogsAPI,
    AuthenticationSettingsAPI,
    CloudAppsAPI,
    CloudAppControlAPI,
    DeviceManagementAPI,
    DLPDictionaryAPI,
    DLPEngineAPI,
    DLPResourcesAPI,
    DLPTemplatesAPI,
    FirewallPolicyAPI,
    ForwardingControlAPI,
    CBIProfileAPI,
    LocationsAPI,
    RuleLabelsAPI,
    CloudSandboxAPI,
    SecurityPolicyAPI,
    SSLInspectionAPI,
    TrafficForwardingAPI,
    URLCategoriesAPI,
    URLFilteringAPI,
    UserManagementAPI,
    WorkloadGroupsAPI,
    ZPAGatewayAPI,
):
    """A Zscaler client object"""

    def __init__(self, user_config: dict = {}):
        client_config_setter = ConfigSetter()
        client_config_setter._apply_config({"client": user_config})
        self._config = client_config_setter.get_config()

        # Retrieve optional customerId from config or environment
        self._customer_id = self._config["client"].get("customerId", os.getenv("ZSCALER_CUSTOMER_ID"))

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
        self._api_version = self._config["client"].get("api_version", "v1")

        # Handle cache
        cache = NoOpCache()
        if self._config["client"]["cache"]["enabled"]:
            if user_config.get("cacheManager") is None:
                time_to_idle = self._config["client"]["cache"]["defaultTti"]
                time_to_live = self._config["client"]["cache"]["defaultTtl"]
                cache = ZscalerCache(time_to_live, time_to_idle)
            else:
                cache = user_config.get("cacheManager")

        self._request_executor = user_config.get("requestExecutor", RequestExecutor)(
            self._config, cache, user_config.get("httpClient", None)
        )

        # Setup logging
        setup_logging()

        if self._config["client"]["logging"]["enabled"]:
            logger = logging.getLogger("zscaler-sdk-python")
            logger.disabled = False
        super().__init__()

    def authenticate(self):
        """
        Handles authentication by using either client_secret or private_key.
        """
        oauth_client = OAuth(self._request_executor, self._config)
        self._auth_token = oauth_client._get_access_token()

        # Update the default headers by setting the Authorization Bearer token
        self._request_executor._default_headers.update({"Authorization": f"Bearer {self._auth_token}"})
        print(f"Authentication complete. Token set: {self._auth_token}")

    def __enter__(self):
        """
        Automatically create and set session within context manager.
        """
        # Create and set up a session using 'requests' library for sync.
        self._session = requests.Session()
        self._request_executor.set_session(self._session)
        self.authenticate()  # Authenticate when entering the context
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Automatically close session within context manager."""
        self._session.close()
        
    """
    Getters
    """

    def get_config(self):
        return self._config

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
