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


class SoftwareInventory(ZscalerObject):
    """
    A class for SoftwareInventory objects.
    """

    def __init__(self, config=None):
        """
        Initialize the SoftwareInventory model based on API response.

        Args:
            config (dict): A dictionary representing the configuration.
        """
        super().__init__(config)

        if config:
            self.software = ZscalerCollection.form_list(
                config["software"] if "software" in config else [], str
            )
            self.next_offset = config["next_offset"] \
                if "next_offset" in config else None
        else:
            self.software = ZscalerCollection.form_list([], str)
            self.next_offset = None

    def request_format(self):
        """
        Return the object as a dictionary in the format expected for API requests.
        """
        parent_req_format = super().request_format()
        current_obj_format = {
            "software": self.software,
            "next_offset": self.next_offset
        }
        parent_req_format.update(current_obj_format)
        return parent_req_format
    
class DeviceSoftwareInventory(ZscalerObject):
    """
    A class for DeviceSoftwareInventory objects.
    """

    def __init__(self, config=None):
        """
        Initialize the DeviceSoftwareInventory model based on API response.

        Args:
            config (dict): A dictionary representing the configuration.
        """
        super().__init__(config)

        if config:
            self.software = ZscalerCollection.form_list(
                config["software"] if "software" in config else [], str
            )
            self.next_offset = config["next_offset"] \
                if "next_offset" in config else None
        else:
            self.software = ZscalerCollection.form_list([], str)
            self.next_offset = None

    def request_format(self):
        """
        Return the object as a dictionary in the format expected for API requests.
        """
        parent_req_format = super().request_format()
        current_obj_format = {
            "software": self.software,
            "next_offset": self.next_offset
        }
        parent_req_format.update(current_obj_format)
        return parent_req_format