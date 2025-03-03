# flake8: noqa
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

# AUTO-GENERATED! DO NOT EDIT FILE DIRECTLY
# SEE CONTRIBUTOR DOCUMENTATION
from zscaler.oneapi_object import ZscalerObject
from zscaler.oneapi_collection import ZscalerCollection


class Zwaincidentresolved(ZscalerObject):
    """
    A class for Zwaincidentresolved objects.
    """

    def __init__(self, config=None):
        """
        Initialize the Zwaincidentresolved model based on API response.

        Args:
            config (dict): A dictionary representing the configuration.
        """
        super().__init__(config)

        if config:
            self.internal_id = config["internalId"] \
                if "internalId" in config else None
            self.integration_type = config["integrationType"] \
                if "integrationType" in config else None
            self.transaction_id = config["transactionId"] \
                if "transactionId" in config else None
            self.source_type = config["sourceType"] \
                if "sourceType" in config else None
            self.source_sub_type = config["sourceSubType"] \
                if "sourceSubType" in config else None
            self.source_actions = ZscalerCollection.form_list(
                config["sourceActions"] if "sourceActions" in config else [], str
            )
            self.severity = config["severity"] \
                if "severity" in config else None
            self.priority = config["priority"] \
                if "priority" in config else None
            self.matching_policies = config["matchingPolicies"] \
                if "matchingPolicies" in config else None
            self.match_count = config["matchCount"] \
                if "matchCount" in config else None
            self.created_at = config["createdAt"] \
                if "createdAt" in config else None
            self.last_updated_at = config["lastUpdatedAt"] \
                if "lastUpdatedAt" in config else None
            self.source_first_observed_at = config["sourceFirstObservedAt"] \
                if "sourceFirstObservedAt" in config else None
            self.source_last_observed_at = config["sourceLastObservedAt"] \
                if "sourceLastObservedAt" in config else None
            self.user_info = config["userInfo"] \
                if "userInfo" in config else None
            self.application_info = config["applicationInfo"] \
                if "applicationInfo" in config else None
            self.content_info = config["contentInfo"] \
                if "contentInfo" in config else None
            self.network_info = config["networkInfo"] \
                if "networkInfo" in config else None
            self.metadata_file_url = config["metadataFileUrl"] \
                if "metadataFileUrl" in config else None
            self.status = config["status"] \
                if "status" in config else None
            self.resolution = config["resolution"] \
                if "resolution" in config else None
            self.assigned_admin = config["assignedAdmin"] \
                if "assignedAdmin" in config else None
            self.last_notified_user = config["lastNotifiedUser"] \
                if "lastNotifiedUser" in config else None
            self.notes = ZscalerCollection.form_list(
                config["notes"] if "notes" in config else [], str
            )
            self.closed_code = config["closedCode"] \
                if "closedCode" in config else None
            self.incident_group_ids = ZscalerCollection.form_list(
                config["incidentGroupIds"] if "incidentGroupIds" in config else [], str
            )
            self.incident_groups = ZscalerCollection.form_list(
                config["incidentGroups"] if "incidentGroups" in config else [], str
            )
            self.dlp_incident_tickets = ZscalerCollection.form_list(
                config["dlpIncidentTickets"] if "dlpIncidentTickets" in config else [], str
            )
            self.labels = ZscalerCollection.form_list(
                config["labels"] if "labels" in config else [], str
            )
        else:
            self.internal_id = None
            self.integration_type = None
            self.transaction_id = None
            self.source_type = None
            self.source_sub_type = None
            self.source_actions = ZscalerCollection.form_list([], str)
            self.severity = None
            self.priority = None
            self.matching_policies = None
            self.match_count = None
            self.created_at = None
            self.last_updated_at = None
            self.source_first_observed_at = None
            self.source_last_observed_at = None
            self.user_info = None
            self.application_info = None
            self.content_info = None
            self.network_info = None
            self.metadata_file_url = None
            self.status = None
            self.resolution = None
            self.assigned_admin = None
            self.last_notified_user = None
            self.notes = ZscalerCollection.form_list([], str)
            self.closed_code = None
            self.incident_group_ids = ZscalerCollection.form_list([], str)
            self.incident_groups = ZscalerCollection.form_list([], str)
            self.dlp_incident_tickets = ZscalerCollection.form_list([], str)
            self.labels = ZscalerCollection.form_list([], str)

    def request_format(self):
        """
        Return the object as a dictionary in the format expected for API requests.
        """
        parent_req_format = super().request_format()
        current_obj_format = {
            "internalId": self.internal_id,
            "integrationType": self.integration_type,
            "transactionId": self.transaction_id,
            "sourceType": self.source_type,
            "sourceSubType": self.source_sub_type,
            "sourceActions": self.source_actions,
            "severity": self.severity,
            "priority": self.priority,
            "matchingPolicies": self.matching_policies,
            "matchCount": self.match_count,
            "createdAt": self.created_at,
            "lastUpdatedAt": self.last_updated_at,
            "sourceFirstObservedAt": self.source_first_observed_at,
            "sourceLastObservedAt": self.source_last_observed_at,
            "userInfo": self.user_info,
            "applicationInfo": self.application_info,
            "contentInfo": self.content_info,
            "networkInfo": self.network_info,
            "metadataFileUrl": self.metadata_file_url,
            "status": self.status,
            "resolution": self.resolution,
            "assignedAdmin": self.assigned_admin,
            "lastNotifiedUser": self.last_notified_user,
            "notes": self.notes,
            "closedCode": self.closed_code,
            "incidentGroupIds": self.incident_group_ids,
            "incidentGroups": self.incident_groups,
            "dlpIncidentTickets": self.dlp_incident_tickets,
            "labels": self.labels
        }
        parent_req_format.update(current_obj_format)
        return parent_req_format