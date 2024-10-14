from zscaler.zpa.application_segment import ApplicationSegmentAPI
from zscaler.zpa.server_groups import ServerGroupsAPI
from zscaler.zpa.service_edge_groups import ServiceEdgeGroupAPI
from zscaler.zpa.app_connector_groups import AppConnectorGroupAPI
from zscaler.zpa.posture_profiles import PostureProfilesAPI
from zscaler.zpa.cloudbrowserisolation import CloudBrowserIsolationAPI
from zscaler.zpa.microtenants import MicrotenantsAPI
from zscaler.zpa.certificates import CertificatesAPI
from zscaler.zpa.scim_groups import SCIMGroupsAPI
from zscaler.zpa.authdomains import AuthDomainsAPI
from zscaler.zpa.inspection import InspectionControllerAPI
from zscaler.zpa.segment_groups import SegmentGroupsAPI
from zscaler.zpa.app_connectors import AppConnectorControllerAPI
from zscaler.zpa.service_edges import ServiceEdgeControllerAPI
from zscaler.zpa.machine_groups import MachineGroupsAPI
from zscaler.zpa.app_connector_schedule import AppConnectorScheduleAPI
from zscaler.zpa.service_edge_schedule import ServiceEdgeScheduleAPI
from zscaler.zpa.cloud_connector_groups import CloudConnectorGroupsAPI
from zscaler.zpa.application_segment_inspection import AppSegmentsInspectionAPI
from zscaler.zpa.application_segment_pra import AppSegmentsPRAAPI
from zscaler.zpa.emergency_access import EmergencyAccessAPI
from zscaler.zpa.enrollment_certificates import EnrollmentCertificateAPI
from zscaler.zpa.idp import IDPControllerAPI
from zscaler.zpa.lss import LSSConfigControllerAPI
from zscaler.zpa.policies import PolicySetControllerAPI
from zscaler.zpa.privileged_remote_access import PrivilegedRemoteAccessAPI
from zscaler.zpa.provisioning import ProvisioningKeyAPI
from zscaler.zpa.saml_attributes import SAMLAttributesAPI
from zscaler.zpa.scim_attributes import ScimAttributeHeaderAPI
from zscaler.zpa.servers import AppServersAPI
from zscaler.zpa.trusted_networks import TrustedNetworksAPI


class ZPAService:
    """ZPA Service client, exposing various ZPA APIs."""

    def __init__(self, client):
        self._request_executor = client._request_executor
        self._config = client._config
        self._app_segments = None
        self._server_groups = None
        self._service_edge_groups = None
        self._app_connector_groups = None
        self._posture_profiles = None
        self._cloud_browser_isolation = None
        self._microtenants = None
        self._certificates = None
        self._scim_groups = None
        self._auth_domain = None
        self._inspection = None
        self._segment_groups = None
        self._app_connectors = None
        self._service_edges = None
        self._machine_groups = None
        self._app_connector_schedule = None
        self._service_edge_schedule = None
        self._cloud_connector_groups = None
        self._app_segments_inspection = None
        self._app_segments_pra = None
        self._emergency_access = None
        self._enrollment_certificate = None
        self._idp_controller = None
        self._lss_config_controller = None
        self._policy_set_controller = None
        self._privileged_remote_access = None
        self._provisioning_key = None
        self._saml_attributes = None
        self._scim_attribute_header = None
        self._app_servers = None
        self._trusted_networks = None

    @property
    def app_segments(self):
        """Lazy load ApplicationSegmentAPI."""
        if self._app_segments is None:
            self._app_segments = ApplicationSegmentAPI(self._request_executor, self._config)
        return self._app_segments

    @property
    def server_groups(self):
        """Lazy load ServerGroupsAPI."""
        if self._server_groups is None:
            self._server_groups = ServerGroupsAPI(self._request_executor, self._config)
        return self._server_groups

    @property
    def service_edge_groups(self):
        """Lazy load ServiceEdgeGroupAPI."""
        if self._service_edge_groups is None:
            self._service_edge_groups = ServiceEdgeGroupAPI(self._request_executor, self._config)
        return self._service_edge_groups

    @property
    def app_connector_groups(self):
        """Lazy load AppConnectorGroupAPI."""
        if self._app_connector_groups is None:
            self._app_connector_groups = AppConnectorGroupAPI(self._request_executor, self._config)
        return self._app_connector_groups

    @property
    def posture_profiles(self):
        """Lazy load PostureProfilesAPI."""
        if self._posture_profiles is None:
            self._posture_profiles = PostureProfilesAPI(self._request_executor, self._config)
        return self._posture_profiles

    @property
    def cloud_browser_isolation(self):
        """Lazy load CloudBrowserIsolationAPI."""
        if self._cloud_browser_isolation is None:
            self._cloud_browser_isolation = CloudBrowserIsolationAPI(self._request_executor, self._config)
        return self._cloud_browser_isolation

    @property
    def microtenants(self):
        """Lazy load MicrotenantsAPI."""
        if self._microtenants is None:
            self._microtenants = MicrotenantsAPI(self._request_executor, self._config)
        return self._microtenants

    @property
    def certificates(self):
        """Lazy load CertificatesAPI."""
        if self._certificates is None:
            self._certificates = CertificatesAPI(self._request_executor, self._config)
        return self._certificates

    @property
    def scim_groups(self):
        """Lazy load SCIMGroupsAPI."""
        if self._scim_groups is None:
            self._scim_groups = SCIMGroupsAPI(self._request_executor, self._config)
        return self._scim_groups

    @property
    def auth_domain(self):
        """Lazy load AuthDomainsAPI."""
        if self._auth_domain is None:
            self._auth_domain = AuthDomainsAPI(self._request_executor, self._config)
        return self._auth_domain

    @property
    def inspection(self):
        """Lazy load InspectionControllerAPI."""
        if self._inspection is None:
            self._inspection = InspectionControllerAPI(self._request_executor, self._config)
        return self._inspection

    @property
    def segment_groups(self):
        """Lazy load SegmentGroupsAPI."""
        if self._segment_groups is None:
            self._segment_groups = SegmentGroupsAPI(self._request_executor, self._config)
        return self._segment_groups

    @property
    def app_connectors(self):
        """Lazy load AppConnectorControllerAPI."""
        if self._app_connectors is None:
            self._app_connectors = AppConnectorControllerAPI(self._request_executor, self._config)
        return self._app_connectors

    @property
    def service_edges(self):
        """Lazy load ServiceEdgeControllerAPI."""
        if self._service_edges is None:
            self._service_edges = ServiceEdgeControllerAPI(self._request_executor, self._config)
        return self._service_edges

    @property
    def machine_groups(self):
        """Lazy load MachineGroupsAPI."""
        if self._machine_groups is None:
            self._machine_groups = MachineGroupsAPI(self._request_executor, self._config)
        return self._machine_groups

    @property
    def app_connector_schedule(self):
        """Lazy load AppConnectorScheduleAPI."""
        if self._app_connector_schedule is None:
            self._app_connector_schedule = AppConnectorScheduleAPI(self._request_executor, self._config)
        return self._app_connector_schedule

    @property
    def service_edge_schedule(self):
        """Lazy load ServiceEdgeScheduleAPI."""
        if self._service_edge_schedule is None:
            self._service_edge_schedule = ServiceEdgeScheduleAPI(self._request_executor, self._config)
        return self._service_edge_schedule

    @property
    def cloud_connector_groups(self):
        """Lazy load CloudConnectorGroupsAPI."""
        if self._cloud_connector_groups is None:
            self._cloud_connector_groups = CloudConnectorGroupsAPI(self._request_executor, self._config)
        return self._cloud_connector_groups

    @property
    def app_segments_inspection(self):
        """Lazy load AppSegmentsInspectionAPI."""
        if self._app_segments_inspection is None:
            self._app_segments_inspection = AppSegmentsInspectionAPI(self._request_executor, self._config)
        return self._app_segments_inspection

    @property
    def app_segments_pra(self):
        """Lazy load AppSegmentsPRAAPI."""
        if self._app_segments_pra is None:
            self._app_segments_pra = AppSegmentsPRAAPI(self._request_executor, self._config)
        return self._app_segments_pra

    @property
    def emergency_access(self):
        """Lazy load EmergencyAccessAPI."""
        if self._emergency_access is None:
            self._emergency_access = EmergencyAccessAPI(self._request_executor, self._config)
        return self._emergency_access

    @property
    def enrollment_certificate(self):
        """Lazy load EnrollmentCertificateAPI."""
        if self._enrollment_certificate is None:
            self._enrollment_certificate = EnrollmentCertificateAPI(self._request_executor, self._config)
        return self._enrollment_certificate

    @property
    def idp_controller(self):
        """Lazy load IDPControllerAPI."""
        if self._idp_controller is None:
            self._idp_controller = IDPControllerAPI(self._request_executor, self._config)
        return self._idp_controller

    @property
    def lss_config_controller(self):
        """Lazy load LSSConfigControllerAPI."""
        if self._lss_config_controller is None:
            self._lss_config_controller = LSSConfigControllerAPI(self._request_executor, self._config)
        return self._lss_config_controller

    @property
    def policy_set_controller(self):
        """Lazy load PolicySetControllerAPI."""
        if self._policy_set_controller is None:
            self._policy_set_controller = PolicySetControllerAPI(self._request_executor, self._config)
        return self._policy_set_controller

    @property
    def privileged_remote_access(self):
        """Lazy load PrivilegedRemoteAccessAPI."""
        if self._privileged_remote_access is None:
            self._privileged_remote_access = PrivilegedRemoteAccessAPI(self._request_executor, self._config)
        return self._privileged_remote_access

    @property
    def provisioning_key(self):
        """Lazy load ProvisioningKeyAPI."""
        if self._provisioning_key is None:
            self._provisioning_key = ProvisioningKeyAPI(self._request_executor, self._config)
        return self._provisioning_key

    @property
    def saml_attributes(self):
        """Lazy load SAMLAttributesAPI."""
        if self._saml_attributes is None:
            self._saml_attributes = SAMLAttributesAPI(self._request_executor, self._config)
        return self._saml_attributes

    @property
    def scim_attribute_header(self):
        """Lazy load ScimAttributeHeaderAPI."""
        if self._scim_attribute_header is None:
            self._scim_attribute_header = ScimAttributeHeaderAPI(self._request_executor, self._config)
        return self._scim_attribute_header

    @property
    def app_servers(self):
        """Lazy load AppServersAPI."""
        if self._app_servers is None:
            self._app_servers = AppServersAPI(self._request_executor, self._config)
        return self._app_servers

    @property
    def trusted_networks(self):
        """Lazy load TrustedNetworksAPI."""
        if self._trusted_networks is None:
            self._trusted_networks = TrustedNetworksAPI(self._request_executor, self._config)
        return self._trusted_networks
