from zscaler.zia.activate import ActivationAPI
from zscaler.zia.admin_roles import AdminRolesAPI
from zscaler.zia.admin_users import AdminUsersAPI
from zscaler.zia.apptotal import AppTotalAPI
from zscaler.zia.audit_logs import AuditLogsAPI
from zscaler.zia.authentication_settings import AuthenticationSettingsAPI
from zscaler.zia.cloudappcontrol import CloudAppControlAPI
from zscaler.zia.isolation_profile import CBIProfileAPI
from zscaler.zia.sandbox import CloudSandboxAPI
from zscaler.zia.dlp_dictionary import DLPDictionaryAPI
from zscaler.zia.dlp_engine import DLPEngineAPI
from zscaler.zia.dlp_web_rules import DLPWebRuleAPI
from zscaler.zia.dlp_templates import DLPTemplates
from zscaler.zia.dlp_resources import DLPResourcesAPI
from zscaler.zia.device_management import DeviceManagementAPI
from zscaler.zia.firewall import FirewallPolicyAPI
from zscaler.zia.forwarding_control import ForwardingControlAPI
from zscaler.zia.locations import LocationsAPI
from zscaler.zia.rule_labels import RuleLabelsAPI
from zscaler.zia.security_policy_settings import SecurityPolicyAPI
from zscaler.zia.ssl_inspection import SSLInspectionAPI
from zscaler.zia.traffic_gre_tunnels import TrafficForwardingGRETunnelAPI
from zscaler.zia.traffic_vpn_credentials import TrafficVPNCredentialAPI
from zscaler.zia.traffic_static_ip import TrafficStaticIPAPI
from zscaler.zia.url_categories import URLCategoriesAPI
from zscaler.zia.url_filtering import URLFilteringAPI
from zscaler.zia.user_management import UserManagementAPI
from zscaler.zia.workload_groups import WorkloadGroupsAPI
from zscaler.zia.zpa_gateway import ZPAGatewayAPI


class ZIAService:
    """ZIA Service client, exposing various ZIA APIs."""

    def __init__(self, client):
        # Ensure the service gets the request executor from the Client object
        self._request_executor = client._request_executor

    @property
    def admin_roles(self):
        """
        The interface object for the :ref:`ZIA Admin and Role Management interface <zia-admin_roles>`.

        """
        return AdminRolesAPI(self._request_executor)

    @property
    def admin_users(self):
        """
        The interface object for the :ref:`ZIA Admin Users interface <zia-admin_users>`.

        """
        return AdminUsersAPI(self._request_executor)

    @property
    def apptotal(self):
        """
        The interface object for the :ref:`ZIA AppTotal interface <zia-apptotal>`.

        """
        return AppTotalAPI(self._request_executor)

    @property
    def audit_logs(self):
        """
        The interface object for the :ref:`ZIA Admin Audit Logs interface <zia-audit_logs>`.

        """
        return AuditLogsAPI(self._request_executor)

    @property
    def activate(self):
        """
        The interface object for the :ref:`ZIA Activation interface <zia-activate>`.

        """
        return ActivationAPI(self)

    @property
    def authentication_settings(self):
        """
        The interface object for the :ref:`ZIA Authentication Security Settings interface <zia-authentication_settings>`.

        """
        return AuthenticationSettingsAPI(self._request_executor)

    @property
    def cloudappcontrol(self):
        """
        The interface object for the :ref:`ZIA Cloud App Control <zia-cloudappcontrol>`.

        """
        return CloudAppControlAPI(self._request_executor)

    @property
    def isolation_profile(self):
        """
        The interface object for the :ref:`ZIA Cloud Browser Isolation Profile <zia-isolation_profile>`.

        """
        return CBIProfileAPI(self._request_executor)

    @property
    def sandbox(self):
        """
        The interface object for the :ref:`ZIA Cloud Sandbox interface <zia-sandbox>`.

        """
        return CloudSandboxAPI(self._request_executor)

    @property
    def dlp_dictionary(self):
        """
        The interface object for the :ref:`ZIA DLP Dictionaries interface <zia-dlp_dictionary>`.


        """
        return DLPDictionaryAPI(self._request_executor)

    @property
    def dlp_engine(self):
        """
        The interface object for the :ref:`ZIA DLP Engine interface <zia-dlp_engine>`.

        """
        return DLPEngineAPI(self._request_executor)

    @property
    def dlp_web_rules(self):
        """
        The interface object for the :ref:`ZIA DLP Web Rules interface <zia-dlp_web_rules>`.

        """
        return DLPWebRuleAPI(self._request_executor)

    @property
    def dlp_templates(self):
        """
        The interface object for the :ref:`ZIA DLP Templates interface <zia-dlp_templates>`.

        """
        return DLPTemplates(self._request_executor)

    @property
    def dlp_resources(self):
        """
        The interface object for the :ref:`ZIA DLP Resources interface <zia-dlp_resources>`.

        """
        return DLPResourcesAPI(self._request_executor)

    @property
    def device_management(self):
        """
        The interface object for the :ref:`ZIA Device Management interface <zia-device_management>`.

        """
        return DeviceManagementAPI(self._request_executor)

    @property
    def firewall(self):
        """
        The interface object for the :ref:`ZIA Firewall Policies interface <zia-firewall>`.

        """
        return FirewallPolicyAPI(self._request_executor)

    @property
    def forwarding_control(self):
        """
        The interface object for the :ref:`ZIA Forwarding Control Policies interface <zia-forwarding_control>`.

        """
        return ForwardingControlAPI(self._request_executor)

    @property
    def locations(self):
        """
        The interface object for the :ref:`ZIA Locations interface <zia-locations>`.

        """
        return LocationsAPI(self._request_executor)

    @property
    def labels(self):
        """
        The interface object for the :ref:`ZIA Rule Labels interface <zia-labels>`.

        """
        return RuleLabelsAPI(self._request_executor)

    @property
    def security_policy_settings(self):
        """
        The interface object for the :ref:`ZIA Security Policy Settings interface <zia-security_policy_settings>`.

        """
        return SecurityPolicyAPI(self._request_executor)

    @property
    def ssl_inspection(self):
        """
        The interface object for the :ref:`ZIA SSL Inspection interface <zia-ssl_inspection>`.

        """
        return SSLInspectionAPI(self._request_executor)

    @property
    def traffic_gre_tunnel(self):
        """
        The interface object for the :ref:`ZIA Traffic Forwarding interface <zia-traffic_gre_tunnel>`.

        """
        return TrafficForwardingGRETunnelAPI(self._request_executor)

    @property
    def traffic_vpn_credentials(self):
        """
        The interface object for the :ref:`ZIA Traffic VPN Credential interface <zia-traffic_vpn_credentials>`.

        """
        return TrafficVPNCredentialAPI(self._request_executor)

    @property
    def traffic_static_ip(self):
        """
        The interface object for the :ref:`ZIA Traffic Static IP interface <zia-traffic_static_ip>`.

        """
        return TrafficStaticIPAPI(self._request_executor)

    @property
    def url_categories(self):
        """
        The interface object for the :ref:`ZIA URL Categories interface <zia-url_categories>`.

        """
        return URLCategoriesAPI(self._request_executor)

    @property
    def url_filtering(self):
        """
        The interface object for the :ref:`ZIA URL Filtering interface <zia-url_filtering>`.

        """
        return URLFilteringAPI(self._request_executor)

    @property
    def user_management(self):
        """
        The interface object for the :ref:`ZIA User Management interface <zia-user_management>`.

        """
        return UserManagementAPI(self._request_executor)

    @property
    def zpa_gateway(self):
        """
        The interface object for the :ref:`ZPA Gateway <zia-zpa_gateway>`.

        """
        return ZPAGatewayAPI(self._request_executor)

    @property
    def workload_groups(self):
        """
        The interface object for the :ref:`ZIA Workload Groups <zia-workload_groups>`.

        """
        return WorkloadGroupsAPI(self._request_executor)
