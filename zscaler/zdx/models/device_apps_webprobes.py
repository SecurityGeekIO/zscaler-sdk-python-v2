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

class DeviceAppWebProbes(ZscalerObject):
    """
    A class for DeviceAppWebProbes objects.
    """

    def __init__(self, config=None):
        """
        Initialize the DeviceAppWebProbes model based on API response.

        Args:
            config (dict): A dictionary representing the configuration.
        """
        super().__init__(config)

        if config:
            self.id = config["id"] \
                if "id" in config else None
            self.name = config["name"] \
                if "name" in config else None
            self.num_probes = config["num_probes"] \
                if "num_probes" in config else None
            self.avg_score = config["avg_score"] \
                if "avg_score" in config else None
            self.avg_pft = config["avg_pft"] \
                if "avg_pft" in config else None
        else:
            self.id = None
            self.name = None
            self.num_probes = None
            self.avg_score = None
            self.avg_pft = None

    def request_format(self):
        """
        Return the object as a dictionary in the format expected for API requests.
        """
        parent_req_format = super().request_format()
        current_obj_format = {
            "id": self.id,
            "name": self.name,
            "num_probes": self.num_probes,
            "avg_score": self.avg_score,
            "avg_pft": self.avg_pft
        }
        parent_req_format.update(current_obj_format)
        return parent_req_format
    
class DeviceWebProbePageFetch(ZscalerObject):
    """
    A class for DeviceWebProbePageFetch objects.
    """

    def __init__(self, config=None):
        """
        Initialize the DeviceWebProbePageFetch model based on API response.

        Args:
            config (dict): A dictionary representing the configuration.
        """
        super().__init__(config)

        if config:
            self.metric = config["metric"] \
                if "metric" in config else None
            self.unit = config["unit"] \
                if "unit" in config else None
            self.datapoints = ZscalerCollection.form_list(
                config["datapoints"] if "datapoints" in config else [], str
            )
        else:
            self.metric = None
            self.unit = None
            self.datapoints = ZscalerCollection.form_list([], str)

    def request_format(self):
        """
        Return the object as a dictionary in the format expected for API requests.
        """
        parent_req_format = super().request_format()
        current_obj_format = {
            "metric": self.metric,
            "unit": self.unit,
            "datapoints": self.datapoints
        }
        parent_req_format.update(current_obj_format)
        return parent_req_format