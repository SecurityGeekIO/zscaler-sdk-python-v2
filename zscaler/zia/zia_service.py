from zscaler.zia.rule_labels import RuleLabelsAPI
# from zscaler.zia.user_management import UserManagementAPI

class ZIAService:
    def __init__(self, client):
        # Ensure the service gets the request executor from the Client object
        self._request_executor = client._request_executor

    @property
    def labels(self):
        """
        The interface object for the :ref:`ZIA Rule Labels interface <zia-labels>`.

        """
        return RuleLabelsAPI(self._request_executor)

    # @property
    # def admin_and_role_management(self):
    #     """
    #     The interface object for the :ref:`ZIA Admin and Role Management interface <zia-admin_and_role_management>`.

    #     """
    #     return AdminAndRoleManagementAPI(self)

    # @property
    # def apptotal(self):
    #     """
    #     The interface object for the :ref:`ZIA AppTotal interface <zia-apptotal>`.

    #     """
    #     return AppTotalAPI(self)

    # @property
    # def audit_logs(self):
    #     """
    #     The interface object for the :ref:`ZIA Admin Audit Logs interface <zia-audit_logs>`.

    #     """
    #     return AuditLogsAPI(self)

    # @property
    # def activate(self):
    #     """
    #     The interface object for the :ref:`ZIA Activation interface <zia-activate>`.

    #     """
    #     return ActivationAPI(self)

    # @property
    # def dlp(self):
    #     """
    #     The interface object for the :ref:`ZIA DLP Dictionaries interface <zia-dlp>`.


    #     """
    #     return DLPAPI(self)

    # @property
    # def firewall(self):
    #     """
    #     The interface object for the :ref:`ZIA Firewall Policies interface <zia-firewall>`.

    #     """
    #     return FirewallPolicyAPI(self)

    # @property
    # def forwarding_control(self):
    #     """
    #     The interface object for the :ref:`ZIA Forwarding Control Policies interface <zia-forwarding_control>`.

    #     """
    #     return ForwardingControlAPI(self)

    # @property
    # def device_management(self):
    #     """
    #     The interface object for the :ref:`ZIA device interface <zia-device_management>`.

    #     """
    #     return DeviceManagementAPI(self)

    # @property
    # def locations(self):
    #     """
    #     The interface object for the :ref:`ZIA Locations interface <zia-locations>`.

    #     """
    #     return LocationsAPI(self)

    # @property
    # def sandbox(self):
    #     """
    #     The interface object for the :ref:`ZIA Cloud Sandbox interface <zia-sandbox>`.

    #     """
    #     return CloudSandboxAPI(self)

    # @property
    # def security(self):
    #     """
    #     The interface object for the :ref:`ZIA Security Policy Settings interface <zia-security>`.

    #     """
    #     return SecurityPolicyAPI(self)

    # @property
    # def authentication_settings(self):
    #     """
    #     The interface object for the :ref:`ZIA Authentication Security Settings interface <zia-authentication_settings>`.

    #     """
    #     return AuthenticationSettingsAPI(self)

    # @property
    # def ssl(self):
    #     """
    #     The interface object for the :ref:`ZIA SSL Inspection interface <zia-ssl_inspection>`.

    #     """
    #     return SSLInspectionAPI(self)

    # @property
    # def traffic(self):
    #     """
    #     The interface object for the :ref:`ZIA Traffic Forwarding interface <zia-traffic>`.

    #     """
    #     return TrafficForwardingAPI(self)

    # @property
    # def url_categories(self):
    #     """
    #     The interface object for the :ref:`ZIA URL Categories interface <zia-url_categories>`.

    #     """
    #     return URLCategoriesAPI(self)

    # @property
    # def url_filtering(self):
    #     """
    #     The interface object for the :ref:`ZIA URL Filtering interface <zia-url_filtering>`.

    #     """
    #     return URLFilteringAPI(self)

    # @property
    # def cloudappcontrol(self):
    #     """
    #     The interface object for the :ref:`ZIA Cloud App Control <zia-cloudappcontrol>`.

    #     """
    #     return CloudAppControlAPI(self)

    # @property
    # def users(self):
    #     """
    #     The interface object for the :ref:`ZIA User Management interface <zia-users>`.

    #     """
    #     return UserManagementAPI(self)

    # @property
    # def web_dlp(self):
    #     """
    #     The interface object for the :ref:`ZIA Web DLP interface <zia-web_dlp>`.

    #     """
    #     return WebDLPAPI(self)

    # @property
    # def zpa_gateway(self):
    #     """
    #     The interface object for the :ref:`ZPA Gateway <zia-zpa_gateway>`.

    #     """
    #     return ZPAGatewayAPI(self)

    # @property
    # def isolation_profile(self):
    #     """
    #     The interface object for the :ref:`ZIA Cloud Browser Isolation Profile <zia-isolation_profile>`.

    #     """
    #     return IsolationProfileAPI(self)

    # @property
    # def workload_groups(self):
    #     """
    #     The interface object for the :ref:`ZIA Workload Groups <zia-workload_groups>`.

    #     """
    #     return WorkloadGroupsAPI(self)
