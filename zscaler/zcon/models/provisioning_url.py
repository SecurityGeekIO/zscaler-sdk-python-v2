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


class ProvisioningURL(ZscalerObject):
    """
    A class for ProvisioningURL objects.
    """

    def __init__(self, config=None):
        """
        Initialize the ProvisioningURL model based on API response.

        Args:
            config (dict): A dictionary representing the configuration.
        """
        super().__init__(config)

        if config:
            self.id = config["id"] \
                if "id" in config else None
            self.name = config["name"] \
                if "name" in config else None
            self.desc = config["desc"] \
                if "desc" in config else None
            self.prov_url = config["provUrl"] \
                if "provUrl" in config else None
            self.prov_url_type = config["provUrlType"] \
                if "provUrlType" in config else None
            self.prov_url_data = config["provUrlData"] \
                if "provUrlData" in config else None
            self.used_in_ec_groups = ZscalerCollection.form_list(
                config["usedInEcGroups"] if "usedInEcGroups" in config else [], str
            )
            self.status = config["status"] \
                if "status" in config else None
            self.last_mod_uid = config["lastModUid"] \
                if "lastModUid" in config else None
            self.last_mod_time = config["lastModTime"] \
                if "lastModTime" in config else None
        else:
            self.id = None
            self.name = None
            self.desc = None
            self.prov_url = None
            self.prov_url_type = None
            self.prov_url_data = None
            self.used_in_ec_groups = ZscalerCollection.form_list([], str)
            self.status = None
            self.last_mod_uid = None
            self.last_mod_time = None

    def request_format(self):
        """
        Return the object as a dictionary in the format expected for API requests.
        """
        parent_req_format = super().request_format()
        current_obj_format = {
            "id": self.id,
            "name": self.name,
            "desc": self.desc,
            "provUrl": self.prov_url,
            "provUrlType": self.prov_url_type,
            "provUrlData": self.prov_url_data,
            "usedInEcGroups": self.used_in_ec_groups,
            "status": self.status,
            "lastModUid": self.last_mod_uid,
            "lastModTime": self.last_mod_time
        }
        parent_req_format.update(current_obj_format)
        return parent_req_format