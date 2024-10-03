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
from zscaler.zpa.models.application_segment_pra import ApplicationSegmentPRA

class PrivilegedRemoteAccessPortal(ZscalerObject):
    """
    A class representing the Privileged Remote Access Portal.
    """

    def __init__(self, config=None):
        super().__init__(config)
        if config:
            self.id = config["id"]\
                if "id" in config else None
            self.name = config["name"]\
                if "name" in config else None
            self.enabled = config["enabled"]\
                if "enabled" in config else True
            self.description = config["description"]\
                if "description" in config else None
            self.certificate_id = config["certificateId"]\
                if "certificateId" in config else None
            self.certificate_name = config["certificateName"]\
                if "certificateName" in config else None
            self.cname = config["cName"]\
                if "cName" in config else None
            self.domain = config["domain"]\
                if "domain" in config else None
            self.user_notification = config["userNotification"]\
                if "userNotification" in config else None
            self.user_notification_enabled = config["userNotificationEnabled"]\
                if "userNotificationEnabled" in config else False
            self.microtenant_id = config["microtenantId"]\
                if "microtenantId" in config else None
            self.microtenant_name = config["microtenantName"]\
                if "microtenantName" in config else "Default"
        else:
            self.id = None
            self.name = None
            self.enabled = True
            self.description = None
            self.certificate_id = None
            self.certificate_name = None
            self.cname = None
            self.domain = None
            self.user_notification = None
            self.user_notification_enabled = False
            self.microtenant_id = None
            self.microtenant_name = "Default"

    def request_format(self):
        """
        Formats the PRA portal data into a dictionary suitable for API requests.
        """
        return {
            "id": self.id,
            "name": self.name,
            "enabled": self.enabled,
            "description": self.description,
            "certificateId": self.certificate_id,
            "certificateName": self.certificate_name,
            "cName": self.cname,
            "domain": self.domain,
            "userNotification": self.user_notification,
            "userNotificationEnabled": self.user_notification_enabled,
            "microtenantId": self.microtenant_id,
            "microtenantName": self.microtenant_name,
        }

class PrivilegedRemoteAccessConsole(ZscalerObject):
    """
    A class representing the Privileged Remote Access Console.
    """

    def __init__(self, config=None):
        super().__init__(config)
        if config:
            self.id = config["id"] \
                if "id" in config else None
            self.name = config["name"] \
                if "name" in config else None
            self.enabled = config["enabled"] \
                if "enabled" in config else True
            self.modified_time = config["modifiedTime"] \
                if "modifiedTime" in config else None
            self.creation_time = config["creationTime"] \
                if "creationTime" in config else None
            self.modified_by = config["modifiedBy"] \
                if "modifiedBy" in config else None
            self.description = config["description"] \
                if "description" in config else None
            self.microtenant_id = config["microtenantId"]\
                if "microtenantId" in config else None
            self.microtenant_name = config["microtenantName"]\
                if "microtenantName" in config else "Default"
                
            # Handling the nested PRA Application
            self.pra_application = ApplicationSegmentPRA(config["praApplication"]) \
                if "praApplication" in config else None

            # Handling the nested PRA Portals (list)
            self.pra_portals = ZscalerCollection.form_list(
                config["praPortals"], PrivilegedRemoteAccessPortal
            ) if "praPortals" in config else []
        else:
            self.id = None
            self.name = None
            self.enabled = True
            self.modified_time = None
            self.creation_time = None
            self.modified_by = None
            self.description = None
            self.pra_application = None
            self.microtenant_id = None
            self.microtenant_name = "Default"
            self.pra_portals = []

    def request_format(self):
        """
        Formats the PRA Console data into a dictionary suitable for API requests.
        """
        return {
            "id": self.id,
            "name": self.name,
            "enabled": self.enabled,
            "description": self.description,
            "microtenantId": self.microtenant_id,
            "microtenantName": self.microtenant_name,
            "praApplication": self.pra_application.request_format() \
                if self.pra_application else None,
            "praPortals": [portal.request_format() for portal in self.pra_portals],
        }

class PrivilegedRemoteAccessCredential(ZscalerObject):
    """
    A class representing the Privileged Remote Access Credential.
    """

    def __init__(self, config=None):
        super().__init__(config)
        if config:
            self.id = config["id"] if "id" in config else None
            self.name = config["name"] if "name" in config else None
            self.description = config["description"] if "description" in config else None
            self.user_domain = config["userDomain"] if "userDomain" in config else None
            self.user_name = config["userName"] if "userName" in config else None
            self.credential_type = config["credentialType"] if "credentialType" in config else None
            self.last_credential_reset_time = config["lastCredentialResetTime"] \
                if "lastCredentialResetTime" in config else None
            self.microtenant_id = config["microtenantId"] if "microtenantId" in config else None
            self.microtenant_name = config["microtenantName"] if "microtenantName" in config else "Default"
        else:
            self.id = None
            self.name = None
            self.description = None
            self.user_domain = None
            self.user_name = None
            self.credential_type = None
            self.last_credential_reset_time = None
            self.microtenant_id = None
            self.microtenant_name = "Default"

    def request_format(self):
        """
        Formats the credential data into a dictionary suitable for API requests.
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "userDomain": self.user_domain,
            "userName": self.user_name,
            "credentialType": self.credential_type,
            "lastCredentialResetTime": self.last_credential_reset_time,
            "microtenantId": self.microtenant_id,
            "microtenantName": self.microtenant_name,
        }

class PrivilegedRemoteAccessApproval(ZscalerObject):
    """
    A class representing the Privileged Remote Access Approval.
    """

    def __init__(self, config=None):
        super().__init__(config)
        if config:
            self.id = config["id"] if "id" in config else None
            self.start_time = config["startTime"] if "startTime" in config else None
            self.end_time = config["endTime"] if "endTime" in config else None
            self.modified_time = config["modifiedTime"] if "modifiedTime" in config else None
            self.creation_time = config["creationTime"] if "creationTime" in config else None
            self.status = config["status"] if "status" in config else None
            self.email_ids = config["emailIds"] if "emailIds" in config else []
            self.applications = [
                ApplicationSegmentPRA(app) for app in config.get("applications", [])
            ]
            
            # Working hours attributes directly defined in the class
            self.working_hours = config["workingHours"] if "workingHours" in config else {}
        else:
            self.id = None
            self.start_time = None
            self.end_time = None
            self.modified_time = None
            self.creation_time = None
            self.status = None
            self.email_ids = []
            self.applications = []
            self.working_hours = {}

    def request_format(self):
        """
        Formats the PRA approval data into a dictionary suitable for API requests.
        """
        return {
            "id": self.id,
            "startTime": self.start_time,
            "endTime": self.end_time,
            "status": self.status,
            "emailIds": self.email_ids,
            "applications": [app.request_format() for app in self.applications],
            "workingHours": self.working_hours,
        }
