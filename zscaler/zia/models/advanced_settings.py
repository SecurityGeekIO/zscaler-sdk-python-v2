"""
Copyright (c) 2023, Zscaler Inc.

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
"""


from zscaler.oneapi_object import ZscalerObject
from zscaler.oneapi_collection import ZscalerCollection

class CBIProfile(ZscalerObject):
    """
    A class representing a Devices object.
    """

    def __init__(self, config=None):
        super().__init__(config)
        if config:
            self.enable_dns_resolution_on_transparent_proxy = config["enableDnsResolutionOnTransparentProxy"]\
                if "enableDnsResolutionOnTransparentProxy" in config else False
            self.enable_ipv6_dns_resolution_on_transparent_proxy = config["enableIPv6DnsResolutionOnTransparentProxy"]\
                if "enableIPv6DnsResolutionOnTransparentProxy" in config else False
            self.enable_ipv6_dns_optimization_on_all_transparent_proxy = config["enableIPv6DnsOptimizationOnAllTransparentProxy"]\
                if "enableIPv6DnsOptimizationOnAllTransparentProxy" in config else False
            self.enable_evaluate_policy_on_global_ssl_bypass = config["enableEvaluatePolicyOnGlobalSSLBypass"]\
                if "enableEvaluatePolicyOnGlobalSSLBypass" in config else False     
            self.enable_office365 = config["enableOffice365"]\
                if "enableOffice365" in config else False     
            self.log_internal_ip = config["logInternalIp"]\
                if "logInternalIp" in config else False   
            self.enforce_surrogate_ip_for_windows_app = config["enforceSurrogateIpForWindowsApp"]\
                if "enforceSurrogateIpForWindowsApp" in config else False   
            self.track_http_tunnel_on_http_ports = config["trackHttpTunnelOnHttpPorts"]\
                if "trackHttpTunnelOnHttpPorts" in config else False   
            self.block_http_tunnel_on_non_http_ports = config["blockHttpTunnelOnNonHttpPorts"]\
                if "blockHttpTunnelOnNonHttpPorts" in config else False   
            self.block_domain_fronting_on_host_header = config["blockDomainFrontingOnHostHeader"]\
                if "blockDomainFrontingOnHostHeader" in config else False  
            self.zscaler_client_connector_1And_pac_road_warrior_in_firewall = config["zscalerClientConnector1AndPacRoadWarriorInFirewall"]\
                if "zscalerClientConnector1AndPacRoadWarriorInFirewall" in config else False                  
            self.cascade_url_filtering = config["cascadeUrlFiltering"]\
                if "cascadeUrlFiltering" in config else False    
            self.enable_policy_for_unauthenticated_traffic = config["enablePolicyForUnauthenticatedTraffic"]\
                if "enablePolicyForUnauthenticatedTraffic" in config else False    
            self.block_non_compliant_http_request_on_http_ports = config["blockNonCompliantHttpRequestOnHttpPorts"]\
                if "blockNonCompliantHttpRequestOnHttpPorts" in config else False    
            self.enable_admin_rank_access = config["enableAdminRankAccess"]\
                if "enableAdminRankAccess" in config else False  
            self.ui_session_timeout = config["uiSessionTimeout"]\
                if "uiSessionTimeout" in config else None  
            self.http2_non_browser_traffic_enabled = config["http2NonbrowserTrafficEnabled"]\
                if "http2NonbrowserTrafficEnabled" in config else False  
            self.ecs_for_all_enabled = config["ecsForAllEnabled"]\
                if "ecsForAllEnabled" in config else False  
            self.dynamic_user_risk_enabled = config["dynamicUserRiskEnabled"]\
                if "dynamicUserRiskEnabled" in config else False  
            self.block_connect_host_sni_mismatch = config["blockConnectHostSniMismatch"]\
                if "blockConnectHostSniMismatch" in config else False  
            self.prefer_sni_over_conn_host = config["preferSniOverConnHost"]\
                if "preferSniOverConnHost" in config else False
            self.sipa_xff_header_enabled = config["sipaXffHeaderEnabled"]\
                if "sipaXffHeaderEnabled" in config else False
            self.block_non_http_on_http_port_enabled = config["blockNonHttpOnHttpPortEnabled"]\
                if "blockNonHttpOnHttpPortEnabled" in config else False
            # Need to check formatt for this attribute
            # self.ecs_object = ZscalerCollection.form_list(
            #     config["ecsObject"] if "ecsObject" in config else [], str
            # )    
                                                                                                                                                                                  
            self.auth_bypass_url_categories = ZscalerCollection.form_list(
                config["authBypassUrlCategories"] if "authBypassUrlCategories" in config else [], str
            )    
            self.domain_fronting_bypass_url_categories = ZscalerCollection.form_list(
                config["domainFrontingBypassUrlCategories"] if "domainFrontingBypassUrlCategories" in config else [], str
            )     
            self.auth_bypass_urls = ZscalerCollection.form_list(
                config["authBypassUrls"] if "authBypassUrls" in config else [], str
            )
            self.auth_bypass_apps = ZscalerCollection.form_list(
                config["authBypassApps"] if "authBypassApps" in config else [], str
            )
            self.kerberos_bypass_url_categories = ZscalerCollection.form_list(
                config["kerberosBypassUrlCategories"] if "kerberosBypassUrlCategories" in config else [], str
            )
            self.kerberos_bypass_urls = ZscalerCollection.form_list(
                config["kerberosBypassUrls"] if "kerberosBypassUrls" in config else [], str
            ) 
            self.kerberos_bypass_apps = ZscalerCollection.form_list(
                config["kerberosBypassApps"] if "kerberosBypassApps" in config else [], str
            )     
            self.basic_bypass_url_categories = ZscalerCollection.form_list(
                config["basicBypassUrlCategories"] if "basicBypassUrlCategories" in config else [], str
            )    
            self.basic_bypass_apps = ZscalerCollection.form_list(
                config["basicBypassApps"] if "basicBypassApps" in config else [], str
            )     
            self.http_range_header_remove_url_categories = ZscalerCollection.form_list(
                config["httpRangeHeaderRemoveUrlCategories"] if "httpRangeHeaderRemoveUrlCategories" in config else [], str
            )    
            self.digest_auth_bypass_url_categories = ZscalerCollection.form_list(
                config["digestAuthBypassUrlCategories"] if "digestAuthBypassUrlCategories" in config else [], str
            )      
            self.digest_auth_bypass_urls = ZscalerCollection.form_list(
                config["digestAuthBypassUrls"] if "digestAuthBypassUrls" in config else [], str
            )      
            self.digest_auth_bypass_apps = ZscalerCollection.form_list(
                config["digestAuthBypassApps"] if "digestAuthBypassApps" in config else [], str
            )    
            self.dns_resolution_on_transparent_proxy_exempt_url_categories = ZscalerCollection.form_list(
                config["dnsResolutionOnTransparentProxyExemptUrlCategories"] if "dnsResolutionOnTransparentProxyExemptUrlCategories" in config else [], str
            )   
            self.dns_resolution_on_transparent_proxy_ipv6_exempt_url_categories = ZscalerCollection.form_list(
                config["dnsResolutionOnTransparentProxyIPv6ExemptUrlCategories"] if "dnsResolutionOnTransparentProxyIPv6ExemptUrlCategories" in config else [], str
            ) 
            self.dns_resolution_on_transparent_proxy_exempt_urls = ZscalerCollection.form_list(
                config["dnsResolutionOnTransparentProxyExemptUrls"] if "dnsResolutionOnTransparentProxyExemptUrls" in config else [], str
            )   
            self.dns_resolution_on_transparent_proxy_exempt_apps = ZscalerCollection.form_list(
                config["dnsResolutionOnTransparentProxyExemptApps"] if "dnsResolutionOnTransparentProxyExemptApps" in config else [], str
            )   
            self.dns_resolution_on_transparent_proxy_ipv6_exempt_apps = ZscalerCollection.form_list(
                config["dnsResolutionOnTransparentProxyIPv6ExemptApps"] if "dnsResolutionOnTransparentProxyIPv6ExemptApps" in config else [], str
            )   
            self.dns_resolution_on_transparent_proxy_url_categories = ZscalerCollection.form_list(
                config["dnsResolutionOnTransparentProxyUrlCategories"] if "dnsResolutionOnTransparentProxyUrlCategories" in config else [], str
            )   
            self.dns_resolution_on_transparent_proxy_ipv6_url_categories = ZscalerCollection.form_list(
                config["dnsResolutionOnTransparentProxyIPv6UrlCategories"] if "dnsResolutionOnTransparentProxyIPv6UrlCategories" in config else [], str
            )   
            self.dns_resolution_on_transparent_proxy_urls = ZscalerCollection.form_list(
                config["dnsResolutionOnTransparentProxyUrls"] if "dnsResolutionOnTransparentProxyUrls" in config else [], str
            )   
            self.dns_resolution_on_transparent_proxy_apps = ZscalerCollection.form_list(
                config["dnsResolutionOnTransparentProxyApps"] if "dnsResolutionOnTransparentProxyApps" in config else [], str
            ) 
            self.dns_resolution_on_transparent_proxy_ipv6_apps = ZscalerCollection.form_list(
                config["dnsResolutionOnTransparentProxyIPv6Apps"] if "dnsResolutionOnTransparentProxyIPv6Apps" in config else [], str
            ) 
            self.block_domain_fronting_apps = ZscalerCollection.form_list(
                config["blockDomainFrontingApps"] if "blockDomainFrontingApps" in config else [], str
            ) 
            self.prefer_sni_over_conn_host_apps = ZscalerCollection.form_list(
                config["preferSniOverConnHostApps"] if "preferSniOverConnHostApps" in config else [], str
            ) 
            self.prefer_sni_over_conn_host_apps = ZscalerCollection.form_list(
                config["preferSniOverConnHostApps"] if "preferSniOverConnHostApps" in config else [], str
            ) 
            self.sni_dns_optimization_bypass_url_categories = ZscalerCollection.form_list(
                config["sniDnsOptimizationBypassUrlCategories"] if "sniDnsOptimizationBypassUrlCategories" in config else [], str
            )
        else:
            self.id = None
            self.name = None
            self.url = None
            self.default_profile = None

    def request_format(self):
        """
        Return the object as a dictionary in the format expected for API requests.
        """
        parent_req_format = super().request_format()
        current_obj_format = {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "defaultProfile": self.default_profile,
        }
        parent_req_format.update(current_obj_format)
        return parent_req_format

