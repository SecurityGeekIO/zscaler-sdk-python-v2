from zscaler.zpa.authdomains import AuthDomainsAPI
from zscaler.zpa.application_segment import ApplicationSegmentAPI
from zscaler.zpa.application_segment_inspection import AppSegmentsInspectionAPI
from zscaler.zpa.application_segment_pra import AppSegmentsPRAAPI
from zscaler.zpa.app_connector_groups import AppConnectorGroupAPI
from zscaler.zpa.app_connectors import AppConnectorControllerAPI
from zscaler.zpa.app_connector_schedule import AppConnectorScheduleAPI
from zscaler.zpa.servers import AppServersAPI
from zscaler.zpa.certificates import CertificatesAPI
from zscaler.zpa.cloud_connector_groups import CloudConnectorGroupsAPI
from zscaler.zpa.cloudbrowserisolation import CloudBrowserIsolationAPI
from zscaler.zpa.customer_version_profile import CustomerVersionProfileAPI
from zscaler.zpa.emergency_access import EmergencyAccessAPI
from zscaler.zpa.enrollment_certificates import EnrollmentCertificateAPI
from zscaler.zpa.idp import IDPControllerAPI
from zscaler.zpa.inspection import InspectionControllerAPI
from zscaler.zpa.machine_groups import MachineGroupsAPI
from zscaler.zpa.microtenants import MicrotenantsAPI
from zscaler.zpa.lss import LSSConfigControllerAPI
from zscaler.zpa.policies import PolicySetControllerAPI
from zscaler.zpa.posture_profiles import PostureProfilesAPI
from zscaler.zpa.privileged_remote_access import PrivilegedRemoteAccessAPI
from zscaler.zpa.provisioning import ProvisioningKeyAPI
from zscaler.zpa.segment_groups import SegmentGroupsAPI
from zscaler.zpa.server_groups import ServerGroupsAPI
from zscaler.zpa.service_edges import ServiceEdgeControllerAPI
from zscaler.zpa.service_edge_groups import ServiceEdgeGroupAPI
from zscaler.zpa.service_edge_schedule import ServiceEdgeScheduleAPI
from zscaler.zpa.saml_attributes import SAMLAttributesAPI
from zscaler.zpa.scim_groups import SCIMGroupsAPI
from zscaler.zpa.scim_attributes import ScimAttributeHeaderAPI
from zscaler.zpa.trusted_networks import TrustedNetworksAPI


class ZPAService:
    """ZPA Service client, exposing various ZPA APIs."""

    def __init__(self, request_executor, config):
        self._request_executor = request_executor
        self._config = config

    @property
    def authdomains(self):
        """
        The interface object for the :ref:`ZPA Auth Domains interface <zpa-authdomains>`.

        """
        return AuthDomainsAPI(self._request_executor, self._config)

    @property
    def app_segments(self):
        """
        The interface object for the :ref:`ZPA Application Segments interface <zpa-app_segments>`.

        """
        return ApplicationSegmentAPI(self._request_executor, self._config)

    @property
    def app_segments_pra(self):
        """
        The interface object for the :ref:`ZPA Application Segments PRA interface <zpa-app_segments_pra>`.

        """
        return AppSegmentsPRAAPI(self._request_executor, self._config)

    @property
    def app_segments_inspection(self):
        """
        The interface object for the :ref:`ZPA Application Segments PRA interface <zpa-app_segments_inspection>`.

        """
        return AppSegmentsInspectionAPI(self._request_executor, self._config)

    @property
    def certificates(self):
        """
        The interface object for the :ref:`ZPA Browser Access Certificates interface <zpa-certificates>`.

        """
        return CertificatesAPI(self._request_executor, self._config)

    @property
    def customer_version_profile(self):
        """
        The interface object for the :ref:`ZPA Customer Version profile interface <zpa-customer_version_profile>`.

        """
        return CustomerVersionProfileAPI(self._request_executor, self._config)
    
    @property
    def isolation(self):
        """
        The interface object for the :ref:`ZPA Isolation <zpa-isolation>`.

        """
        return CloudBrowserIsolationAPI(self._request_executor, self._config)

    @property
    def cloud_connector_groups(self):
        """
        The interface object for the :ref:`ZPA Cloud Connector Groups interface <zpa-cloud_connector_groups>`.

        """
        return CloudConnectorGroupsAPI(self._request_executor, self._config)

    @property
    def app_connector_groups(self):
        """
        The interface object for the :ref:`ZPA App Connector Groups interface <zpa-app_connector_groups>`.

        """
        return AppConnectorGroupAPI(self._request_executor, self._config)
    
    @property
    def connectors(self):
        """
        The interface object for the :ref:`ZPA Connectors interface <zpa-connectors>`.

        """
        return AppConnectorControllerAPI(self._request_executor, self._config)

    @property
    def app_connector_schedule(self):
        """
        The interface object for the :ref:`ZPA App Connector Groups interface <zpa-app_connector_schedule>`.

        """
        return AppConnectorScheduleAPI(self._request_executor, self._config)
    
    @property
    def emergency_access(self):
        """
        The interface object for the :ref:`ZPA Emergency Access interface <zpa-emergency_access>`.

        """
        return EmergencyAccessAPI(self._request_executor, self._config)

    @property
    def enrollment_certificates(self):
        """
        The interface object for the :ref:`ZPA Enrollment Certificate interface <zpa-enrollment_certificates>`.

        """
        return EnrollmentCertificateAPI(self._request_executor, self._config)
    
    @property
    def idp(self):
        """
        The interface object for the :ref:`ZPA IDP interface <zpa-idp>`.

        """
        return IDPControllerAPI(self._request_executor, self._config)

    @property
    def inspection(self):
        """
        The interface object for the :ref:`ZPA Inspection interface <zpa-inspection>`.

        """
        return InspectionControllerAPI(self._request_executor, self._config)

    @property
    def lss(self):
        """
        The interface object for the :ref:`ZIA Log Streaming Service Config interface <zpa-lss>`.

        """
        return LSSConfigControllerAPI(self._request_executor, self._config)

    @property
    def machine_groups(self):
        """
        The interface object for the :ref:`ZPA Machine Groups interface <zpa-machine_groups>`.

        """
        return MachineGroupsAPI(self._request_executor, self._config)

    @property
    def microtenants(self):
        """
        The interface object for the :ref:`ZPA Microtenants interface <zpa-microtenants>`.

        """
        return MicrotenantsAPI(self._request_executor, self._config)

    @property
    def policies(self):
        """
        The interface object for the :ref:`ZPA Policy Sets interface <zpa-policies>`.

        """
        return PolicySetControllerAPI(self._request_executor, self._config)

    @property
    def posture_profiles(self):
        """
        The interface object for the :ref:`ZPA Posture Profiles interface <zpa-posture_profiles>`.

        """
        return PostureProfilesAPI(self._request_executor, self._config)

    @property
    def privileged_remote_access(self):
        """
        The interface object for the :ref:`ZPA Privileged Remote Access interface <zpa-privileged_remote_access>`.

        """
        return PrivilegedRemoteAccessAPI(self._request_executor, self._config)

    @property
    def provisioning(self):
        """
        The interface object for the :ref:`ZPA Provisioning interface <zpa-provisioning>`.

        """
        return ProvisioningKeyAPI(self._request_executor, self._config)

    @property
    def saml_attributes(self):
        """
        The interface object for the :ref:`ZPA SAML Attributes interface <zpa-saml_attributes>`.

        """
        return SAMLAttributesAPI(self._request_executor, self._config)

    @property
    def scim_attributes(self):
        """
        The interface object for the :ref:`ZPA SCIM Attributes interface <zpa-scim_attributes>`.

        """
        return ScimAttributeHeaderAPI(self._request_executor, self._config)

    @property
    def scim_groups(self):
        """
        The interface object for the :ref:`ZPA SCIM Groups interface <zpa-scim_groups>`.

        """
        return SCIMGroupsAPI(self._request_executor, self._config)

    @property
    def segment_groups(self):
        """
        The interface object for the :ref:`ZPA Segment Groups interface <zpa-segment_groups>`.

        """
        return SegmentGroupsAPI(self._request_executor, self._config)

    @property
    def server_groups(self):
        """
        The interface object for the :ref:`ZPA Server Groups interface <zpa-server_groups>`.

        """
        return ServerGroupsAPI(self._request_executor, self._config)

    @property
    def servers(self):
        """
        The interface object for the :ref:`ZPA Application Servers interface <zpa-app_servers>`.

        """
        return AppServersAPI(self._request_executor, self._config)

    @property
    def service_edges(self):
        """
        The interface object for the :ref:`ZPA Service Edges interface <zpa-service_edges>`.

        """
        return ServiceEdgeControllerAPI(self._request_executor, self._config)

    @property
    def service_edge_group(self):
        """
        The interface object for the :ref:`ZPA Service Edge Groups interface <zpa-service_edge_groups>`.

        """
        return ServiceEdgeGroupAPI(self._request_executor, self._config)

    @property
    def service_edge_schedule(self):
        """
        The interface object for the :ref:`ZPA Service Edge Groups interface <zpa-service_edge_schedule>`.

        """
        return ServiceEdgeScheduleAPI(self._request_executor, self._config)
    
    @property
    def trusted_networks(self):
        """
        The interface object for the :ref:`ZPA Trusted Networks interface <zpa-trusted_networks>`.

        """
        return TrustedNetworksAPI(self._request_executor, self._config)