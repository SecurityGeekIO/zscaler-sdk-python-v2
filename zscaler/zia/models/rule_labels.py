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

class RuleLabels(ZscalerObject):
    """
    A class for RuleLabels objects.
    """

    def __init__(self, config=None):
        """
        Initialize the RuleLabels model based on API response.

        Args:
            config (dict): A dictionary representing the Rule Labels configuration.
        """
        super().__init__(config)

        if config:
            # Defensive approach using 'if' conditions
            if "id" in config:
                self.id = config["id"]
            else:
                self.id = None

            if "name" in config:
                self.name = config["name"]
            else:
                self.name = None

            if "lastModifiedTime" in config:
                self.last_modified_time = config["lastModifiedTime"]
            else:
                self.last_modified_time = None

            if "lastModifiedBy" in config:
                if "id" in config["lastModifiedBy"] and "name" in config["lastModifiedBy"]:
                    self.last_modified_by = {
                        "id": config["lastModifiedBy"]["id"],
                        "name": config["lastModifiedBy"]["name"]
                    }
                else:
                    self.last_modified_by = None
            else:
                self.last_modified_by = None

            if "createdBy" in config:
                if "id" in config["createdBy"] and "name" in config["createdBy"]:
                    self.created_by = {
                        "id": config["createdBy"]["id"],
                        "name": config["createdBy"]["name"]
                    }
                else:
                    self.created_by = None
            else:
                self.created_by = None

            if "referencedRuleCount" in config:
                self.referenced_rule_count = config["referencedRuleCount"]
            else:
                self.referenced_rule_count = 0
        else:
            # Initialize with default None or 0 values
            self.id = None
            self.name = None
            self.last_modified_time = None
            self.last_modified_by = None
            self.created_by = None
            self.referenced_rule_count = 0

    def request_format(self):
        """
        Return the object as a dictionary in the format expected for API requests.
        """
        parent_req_format = super().request_format()
        current_obj_format = {
            "id": self.id,
            "name": self.name,
            "lastModifiedTime": self.last_modified_time,
            "lastModifiedBy": self.last_modified_by,
            "createdBy": self.created_by,
            "referencedRuleCount": self.referenced_rule_count
        }
        parent_req_format.update(current_obj_format)
        return parent_req_format
