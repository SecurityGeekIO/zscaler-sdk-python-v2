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


class ManagePass(ZscalerObject):
    def __init__(self, config=None):
        """
        Initialize the ManagePass model based on API response.

        Args:
            config (dict): A dictionary representing the ManagePass configuration.
        """
        super().__init__(config)

        if config:
            self.company_id = config.get("companyId")
            self.device_type = config.get("deviceType")
            self.exit_pass = config.get("exitPass")
            self.logout_pass = config.get("logoutPass")
            self.policy_name = config.get("policyName")
            self.uninstall_pass = config.get("uninstallPass")
            self.zad_disable_pass = config.get("zadDisablePass")
            self.zdp_disable_pass = config.get("zdpDisablePass")
            self.zdx_disable_pass = config.get("zdxDisablePass")
            self.zia_disable_pass = config.get("ziaDisablePass")
            self.zpa_disable_pass = config.get("zpaDisablePass")
        else:
            self.company_id = None
            self.device_type = None
            self.exit_pass = None
            self.logout_pass = None
            self.policy_name = None
            self.uninstall_pass = None
            self.zad_disable_pass = None
            self.zdp_disable_pass = None
            self.zdx_disable_pass = None
            self.zia_disable_pass = None
            self.zpa_disable_pass = None

    def request_format(self):
        parent_req_format = super().request_format()
        current_obj_format = {
            "companyId": self.company_id,
            "deviceType": self.device_type,
            "exitPass": self.exit_pass,
            "logoutPass": self.logout_pass,
            "policyName": self.policy_name,
            "uninstallPass": self.uninstall_pass,
            "zadDisablePass": self.zad_disable_pass,
            "zdpDisablePass": self.zdp_disable_pass,
            "zdxDisablePass": self.zdx_disable_pass,
            "ziaDisablePass": self.zia_disable_pass,
            "zpaDisablePass": self.zpa_disable_pass,
        }
        parent_req_format.update(current_obj_format)
        return parent_req_format


class ManagePassResponseContract(ZscalerObject):
    def __init__(self, config=None):
        """
        Initialize the ManagePassResponseContract model based on API response.

        Args:
            config (dict): A dictionary representing the ManagePassResponseContract configuration.
        """
        super().__init__(config)

        if config:
            self.error_message = config.get("errorMessage")
        else:
            self.error_message = None

    def request_format(self):
        parent_req_format = super().request_format()
        current_obj_format = {
            "errorMessage": self.error_message,
        }
        parent_req_format.update(current_obj_format)
        return parent_req_format
