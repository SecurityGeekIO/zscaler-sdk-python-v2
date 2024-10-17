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


class Device(ZscalerObject):
    def __init__(self, config=None):
        """
        Initialize the Device model based on API response.

        Args:
            config (dict): A dictionary representing the Device configuration.
        """
        super().__init__(config)

        if config:
            self.agent_version = config.get("agentVersion")
            self.company_name = config.get("companyName")
            self.config_download_time = config.get("config_download_time")
            self.deregistration_timestamp = config.get("deregistrationTimestamp")
            self.detail = config.get("detail")
            self.download_count = config.get("download_count")
            self.hardware_fingerprint = config.get("hardwareFingerprint")
            self.keep_alive_time = config.get("keepAliveTime")
            self.last_seen_time = config.get("last_seen_time")
            self.mac_address = config.get("macAddress")
            self.machine_hostname = config.get("machineHostname")
            self.manufacturer = config.get("manufacturer")
            self.os_version = config.get("osVersion")
            self.owner = config.get("owner")
            self.policy_name = config.get("policyName")
            self.registration_state = config.get("registrationState")
            self.registration_time = config.get("registration_time")
            self.state = config.get("state")
            self.tunnel_version = config.get("tunnelVersion")
            self.type = config.get("type")
            self.udid = config.get("udid")
            self.upm_version = config.get("upmVersion")
            self.user = config.get("user")
            self.vpn_state = config.get("vpnState")
            self.zapp_arch = config.get("zappArch")
        else:
            self.agent_version = None
            self.company_name = None
            self.config_download_time = None
            self.deregistration_timestamp = None
            self.detail = None
            self.download_count = None
            self.hardware_fingerprint = None
            self.keep_alive_time = None
            self.last_seen_time = None
            self.mac_address = None
            self.machine_hostname = None
            self.manufacturer = None
            self.os_version = None
            self.owner = None
            self.policy_name = None
            self.registration_state = None
            self.registration_time = None
            self.state = None
            self.tunnel_version = None
            self.type = None
            self.udid = None
            self.upm_version = None
            self.user = None
            self.vpn_state = None
            self.zapp_arch = None

    def request_format(self):
        parent_req_format = super().request_format()
        current_obj_format = {
            "agentVersion": self.agent_version,
            "companyName": self.company_name,
            "config_download_time": self.config_download_time,
            "deregistrationTimestamp": self.deregistration_timestamp,
            "detail": self.detail,
            "download_count": self.download_count,
            "hardwareFingerprint": self.hardware_fingerprint,
            "keepAliveTime": self.keep_alive_time,
            "last_seen_time": self.last_seen_time,
            "macAddress": self.mac_address,
            "machineHostname": self.machine_hostname,
            "manufacturer": self.manufacturer,
            "osVersion": self.os_version,
            "owner": self.owner,
            "policyName": self.policy_name,
            "registrationState": self.registration_state,
            "registration_time": self.registration_time,
            "state": self.state,
            "tunnelVersion": self.tunnel_version,
            "type": self.type,
            "udid": self.udid,
            "upmVersion": self.upm_version,
            "user": self.user,
            "vpnState": self.vpn_state,
            "zappArch": self.zapp_arch,
        }
        parent_req_format.update(current_obj_format)
        return parent_req_format
