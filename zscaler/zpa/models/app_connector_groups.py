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


class AppConnectorGroup(ZscalerObject):
    def __init__(self, config=None):
        """
        Initialize the AppConnectorGroup model based on API response.

        Args:
            config (dict): A dictionary representing the App Connector Group configuration.
        """
        super().__init__(config)

        if config:
            self.id = config["id"] if "id" in config else None
            self.modified_time = config["modifiedTime"]\
                if "modifiedTime" in config else None
            self.creation_time = config["creationTime"]\
                if "creationTime" in config else None
            self.modified_by = config["modifiedBy"]\
                if "modifiedBy" in config else None
            self.name = config["name"]\
                if "name" in config else None
            self.enabled = config["enabled"]\
                if "enabled" in config else None
            self.description = config["description"]\
                if "description" in config else None
            self.version_profile_id = config["versionProfileId"]\
                if "versionProfileId" in config else None
            self.override_version_profile = config["overrideVersionProfile"]\
                if "overrideVersionProfile" in config else None
            self.version_profile_name = config["versionProfileName"]\
                if "versionProfileName" in config else None
            self.upgrade_priority = config["upgradePriority"]\
                if "upgradePriority" in config else None
            self.version_profile_visibility_scope = config["versionProfileVisibilityScope"]\
                if "versionProfileVisibilityScope" in config else None
            self.upgrade_time_in_secs = config["upgradeTimeInSecs"]\
                if "upgradeTimeInSecs" in config else None
            self.upgrade_day = config["upgradeDay"]\
                if "upgradeDay" in config else None
            self.location = config["location"]\
                if "location" in config else None
            self.latitude = config["latitude"]\
                if "latitude" in config else None
            self.longitude = config["longitude"]\
                if "longitude" in config else None
            self.dns_query_type = config["dnsQueryType"]\
                if "dnsQueryType" in config else None
            self.city_country = config["cityCountry"]\
                if "cityCountry" in config else None
            self.country_code = config["countryCode"]\
                if "countryCode" in config else None
            self.tcp_quick_ack_app = config["tcpQuickAckApp"]\
                if "tcpQuickAckApp" in config else None
            self.tcp_quick_ack_assistant = config["tcpQuickAckAssistant"]\
                if "tcpQuickAckAssistant" in config else None
            self.tcp_quick_ack_read_assistant = config["tcpQuickAckReadAssistant"]\
                if "tcpQuickAckReadAssistant" in config else None
            self.pra_enabled = config["praEnabled"]\
                if "praEnabled" in config else None
            self.use_in_dr_mode = config["useInDrMode"]\
                if "useInDrMode" in config else None
            self.waf_disabled = config["wafDisabled"]\
                if "wafDisabled" in config else None
            self.microtenant_id = config["microtenantId"]\
                if "microtenantId" in config else None
            self.microtenant_name = config["microtenantName"]\
                if "microtenantName" in config else None
            self.lss_app_connector_group = config["lssAppConnectorGroup"]\
                if "lssAppConnectorGroup" in config else None
        else:
            self.id = None
            self.modified_time = None
            self.creation_time = None
            self.modified_by = None
            self.name = None
            self.enabled = None
            self.description = None
            self.version_profile_id = None
            self.override_version_profile = None
            self.version_profile_name = None
            self.upgrade_priority = None
            self.version_profile_visibility_scope = None
            self.upgrade_time_in_secs = None
            self.upgrade_day = None
            self.location = None
            self.latitude = None
            self.longitude = None
            self.dns_query_type = None
            self.city_country = None
            self.country_code = None
            self.tcp_quick_ack_app = None
            self.tcp_quick_ack_assistant = None
            self.tcp_quick_ack_read_assistant = None
            self.pra_enabled = None
            self.use_in_dr_mode = None
            self.waf_disabled = None
            self.microtenant_id = None
            self.microtenant_name = None
            self.lss_app_connector_group = None

    def request_format(self):
        parent_req_format = super().request_format()
        current_obj_format = {
            "id": self.id,
            "modifiedTime": self.modified_time,
            "creationTime": self.creation_time,
            "modifiedBy": self.modified_by,
            "name": self.name,
            "enabled": self.enabled,
            "description": self.description,
            "versionProfileId": self.version_profile_id,
            "overrideVersionProfile": self.override_version_profile,
            "versionProfileName": self.version_profile_name,
            "upgradePriority": self.upgrade_priority,
            "versionProfileVisibilityScope": self.version_profile_visibility_scope,
            "upgradeTimeInSecs": self.upgrade_time_in_secs,
            "upgradeDay": self.upgrade_day,
            "location": self.location,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "dnsQueryType": self.dns_query_type,
            "cityCountry": self.city_country,
            "countryCode": self.country_code,
            "tcpQuickAckApp": self.tcp_quick_ack_app,
            "tcpQuickAckAssistant": self.tcp_quick_ack_assistant,
            "tcpQuickAckReadAssistant": self.tcp_quick_ack_read_assistant,
            "praEnabled": self.pra_enabled,
            "useInDrMode": self.use_in_dr_mode,
            "wafDisabled": self.waf_disabled,
            "microtenantId": self.microtenant_id,
            "microtenantName": self.microtenant_name,
            "lssAppConnectorGroup": self.lss_app_connector_group,
        }
        parent_req_format.update(current_obj_format)
        return parent_req_format

