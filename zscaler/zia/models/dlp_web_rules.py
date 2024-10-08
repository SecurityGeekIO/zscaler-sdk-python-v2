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
from zscaler.zia.models import dlp_templates as dlp_templates
from zscaler.zia.models import dlp_resources as dlp_resources
from zscaler.zia.models import location_group as location_group
from zscaler.zia.models import location_management as location_management
from zscaler.zia.models import user_management as user_management
from zscaler.zia.models import urlcategory as urlcategory
from zscaler.zia.models import workload_groups as workload_groups

class DLPWebRules(ZscalerObject):
    """
    A class representing a DLP Web Rule object.
    """

    def __init__(self, config=None):
        super().__init__(config)
        if config:
            self.id = config["id"]\
                if "id" in config else None
            self.name = config["name"]\
                if "name" in config else None
            self.description = config["description"]\
                if "description" in config else None
            self.rank = config["rank"]\
                if "rank" in config else None
            self.access_control = config["accessControl"]\
                if "accessControl" in config else None
            self.min_size = config["minSize"]\
                if "minSize" in config else None
            self.action = config["action"]\
                if "action" in config else None
            self.state = config["state"]\
                if "state" in config else None
            self.match_only = config["matchOnly"]\
                if "matchOnly" in config else False
            self.without_content_inspection = config["withoutContentInspection"]\
                if "withoutContentInspection" in config else False
            self.inspect_http_get_enabled = config["inspectHttpGetEnabled"]\
                if "inspectHttpGetEnabled" in config else False
            self.dlp_download_scan_enabled = config["dlpDownloadScanEnabled"]\
                if "dlpDownloadScanEnabled" in config else False
            self.zcc_notifications_enabled = config["zccNotificationsEnabled"]\
                if "zccNotificationsEnabled" in config else False
            self.severity = config["severity"]\
                if "severity" in config else None
            self.order = config["order"]\
                if "order" in config else None
            self.eun_template_id = config["eunTemplateId"]\
                if "eunTemplateId" in config else None
            self.zscaler_incident_receiver = config["zscalerIncidentReceiver"]\
                if "zscalerIncidentReceiver" in config else None

            # Handling lists of simple values
            self.protocols = ZscalerCollection.form_list(
                config["protocols"] if "protocols" in config else [],
                str
            )

            self.file_types = ZscalerCollection.form_list(
                config["fileTypes"] if "fileTypes" in config else [],
                str
            )
            self.cloud_applications = ZscalerCollection.form_list(
                config["cloudApplications"] if "cloudApplications" in config else [],
                str
            )
            self.location_groups = ZscalerCollection.form_list(
                config["locationGroups"] if "locationGroups" in config else [],
                location_group.LocationGroup
            )

            # Handling nested objects with ZscalerCollection and defensive programming
            self.locations = ZscalerCollection.form_list(
                config["locations"] if "locations" in config else [],
                location_management.LocationManagement
            )

            self.groups = ZscalerCollection.form_list(
                config["groups"] if "groups" in config else [],
                user_management.Groups
            )
            self.departments = ZscalerCollection.form_list(
                config["departments"] if "departments" in config else [],
                user_management.Department
            )
            self.users = ZscalerCollection.form_list(
                config["users"] if "users" in config else [],
                user_management.UserManagement
            )
            self.workload_groups = ZscalerCollection.form_list(
                config["workloadGroups"] if "workloadGroups" in config else [],
                workload_groups.WorkloadGroups
            )
            self.included_domain_profiles = ZscalerCollection.form_list(
                config["includedDomainProfiles"] if "includedDomainProfiles" in config else [],
                IncludedDomainProfile
            )
            self.source_ip_groups = ZscalerCollection.form_list(
                config["sourceIpGroups"] if "sourceIpGroups" in config else [],
                SourceIPGroup
            )
            self.url_categories = ZscalerCollection.form_list(
                config["urlCategories"] if "urlCategories" in config else [],
                urlcategory.URLCategory
            )
            self.zpa_app_segments = ZscalerCollection.form_list(
                config["zpaAppSegments"] if "zpaAppSegments" in config else [],
                ZPAAppSegment
            )

            # Handling single nested objects with defensive programming
            self.auditor = Auditor(config["auditor"])\
                if "auditor" in config else None
            self.notification_template = dlp_templates.DLPTemplates(
                config["notificationTemplate"]) if "notificationTemplate" in config else None
            self.icap_server = dlp_resources.DLPICAPServer(
                config["icapServer"]) if "icapServer" in config else None

        else:
            # Defaults when config is None
            self.id = None
            self.name = None
            self.description = None
            self.rank = None
            self.access_control = None
            self.min_size = None
            self.action = None
            self.state = None
            self.match_only = False
            self.without_content_inspection = False
            self.inspect_http_get_enabled = False
            self.dlp_download_scan_enabled = False
            self.zcc_notifications_enabled = False
            self.severity = None
            self.order = None
            self.eun_template_id = None
            self.zscaler_incident_receiver = None
            self.protocols = []
            self.file_types = []
            self.cloud_applications = []
            self.locations = []
            self.location_groups = []
            self.groups = []
            self.departments = []
            self.users = []
            self.url_categories = []
            self.zpa_app_segments = []
            self.workload_groups = []
            self.included_domain_profiles = []
            self.source_ip_groups = []
            self.auditor = None
            self.notification_template = None
            self.icap_server = None

    def request_format(self):
        """
        Return the object as a dictionary in the format expected for API requests.
        """
        parent_req_format = super().request_format()
        current_obj_format = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "rank": self.rank,
            "accessControl": self.access_control,
            "minSize": self.min_size,
            "action": self.action,
            "state": self.state,
            "matchOnly": self.match_only,
            "withoutContentInspection": self.without_content_inspection,
            "inspectHttpGetEnabled": self.inspect_http_get_enabled,
            "dlpDownloadScanEnabled": self.dlp_download_scan_enabled,
            "zccNotificationsEnabled": self.zcc_notifications_enabled,
            "severity": self.severity,
            "order": self.order,
            "eunTemplateId": self.eun_template_id,
            "zscalerIncidentReceiver": self.zscaler_incident_receiver,
            "protocols": self.protocols,
            "fileTypes": self.file_types,
            "cloudApplications": self.cloud_applications,
            "locations": [location.request_format() for location in self.locations],
            "locationGroups": [group.request_format() for group in self.location_groups],
            "groups": [group.request_format() for group in self.groups],
            "departments": [department.request_format() for department in self.departments],
            "users": [user.request_format() for user in self.users],
            "urlCategories": [url_category.request_format() for url_category in self.url_categories],
            "zpaAppSegments": [segment.request_format() for segment in self.zpa_app_segments],
            "workloadGroups": [group.request_format() for group in self.workload_groups],
            "includedDomainProfiles": [profile.request_format() for profile in self.included_domain_profiles],
            "sourceIpGroups": [group.request_format() for group in self.source_ip_groups],
            "auditor": self.auditor.request_format()\
                if self.auditor else None,
            "notificationTemplate": self.notification_template.request_format()\
                if self.notification_template else None,
            "icapServer": self.icap_server.request_format()\
                if self.icap_server else None,
        }
        parent_req_format.update(current_obj_format)
        return parent_req_format

# Example of nested models used within the DLPWebRules model

class Location(ZscalerObject):
    def __init__(self, config=None):
        super().__init__(config)
        self.id = config["id"]\
            if "id" in config else None
        self.name = config["name"]\
            if "name" in config else None

class LocationGroup(ZscalerObject):
    def __init__(self, config=None):
        super().__init__(config)
        self.id = config["id"]\
            if "id" in config else None
        self.name = config["name"]\
            if "name" in config else None

# Define other nested classes similarly.
