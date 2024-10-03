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
from zscaler.zpa.models import application_segment\
    as application_segment
from zscaler.zpa.models import app_connector_groups\
    as app_connector_groups


class ServerGroup(ZscalerObject):
    """
    A class for ServerGroup objects.
    """

    def __init__(self, config=None):
        super().__init__(config)
        if config:
            self.id = config["id"]\
                if "id" in config else None
            self.modified_time = config["modifiedTime"]\
                if "modifiedTime" in config else None
            self.creation_time = config["creationTime"]\
                if "creationTime" in config else None
            self.modified_by = config["modifiedBy"]\
                if "modifiedBy" in config else None
            self.enabled = config["enabled"]\
                if "enabled" in config else None
            self.name = config["name"]\
                if "name" in config else None
            self.description = config["description"]\
                if "description" in config else None
            self.ip_anchored = config["ipAnchored"]\
                if "ipAnchored" in config else None
            self.config_space = config["configSpace"]\
                if "configSpace" in config else None
            self.extranet_enabled = config["extranetEnabled"]\
                if "extranetEnabled" in config else None
            self.microtenant_id = config["microtenantId"]\
                if "microtenantId" in config else None
            self.microtenant_name = config["microtenantName"]\
                if "microtenantName" in config else None
            self.dynamic_discovery = config["dynamicDiscovery"]\
                if "dynamicDiscovery" in config else None

            # Handle the nested list of applications
            if "applications" in config:
                self.applications = [application_segment.ApplicationSegment(app) for app in config["applications"]]
            else:
                self.applications = []

            # Handle the nested list of appConnectorGroups
            if "appConnectorGroups" in config:
                self.app_connector_groups = [app_connector_groups.AppConnectorGroup(connector) for connector in config["appConnectorGroups"]]
            else:
                self.app_connector_groups = []
        else:
            self.id = None
            self.modified_time = None
            self.creation_time = None
            self.modified_by = None
            self.enabled = None
            self.name = None
            self.description = None
            self.ip_anchored = None
            self.config_space = None
            self.extranet_enabled = None
            self.microtenant_name = None
            self.dynamic_discovery = None
            self.applications = []
            self.app_connector_groups = []

    def request_format(self):
        """
        Formats the current object for making requests.
        """
        parent_req_format = super().request_format()
        current_obj_format = {
            "id": self.id,
            "modifiedTime": self.modified_time,
            "creationTime": self.creation_time,
            "modifiedBy": self.modified_by,
            "enabled": self.enabled,
            "name": self.name,
            "description": self.description,
            "ipAnchored": self.ip_anchored,
            "configSpace": self.config_space,
            "extranetEnabled": self.extranet_enabled,
            "microtenantName": self.microtenant_name,
            "dynamicDiscovery": self.dynamic_discovery,
            "applications": [app.request_format() for app in self.applications],
            "appConnectorGroups": [connector.request_format() for connector in self.app_connector_groups],
        }
        parent_req_format.update(current_obj_format)
        return parent_req_format
