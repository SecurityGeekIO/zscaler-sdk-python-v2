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

class InspectionProfile(ZscalerObject):
    """
    A class representing the Inspection Control configuration.
    """

    def __init__(self, config=None):
        super().__init__(config)
        if config:
            self.id = config["id"] if "id" in config else None
            self.name = config["name"] if "name" in config else None
            self.action = config["action"] if "action" in config else None
            self.action_value = config["actionValue"] if "actionValue" in config else None
            self.control_number = config["controlNumber"] if "controlNumber" in config else None
            self.control_type = config["controlType"] if "controlType" in config else None
            self.creation_time = config["creationTime"] if "creationTime" in config else None
            self.default_action = config["defaultAction"] if "defaultAction" in config else None
            self.default_action_value = config["defaultActionValue"] if "defaultActionValue" in config else None
            self.description = config["description"] if "description" in config else None
            self.modified_by = config["modifiedBy"] if "modifiedBy" in config else None
            self.modified_time = config["modifiedTime"] if "modifiedTime" in config else None
            self.paranoia_level = config["paranoiaLevel"] if "paranoiaLevel" in config else None
            self.protocol_type = config["protocolType"] if "protocolType" in config else None
            self.severity = config["severity"] if "severity" in config else None
            self.version = config["version"] if "version" in config else None

            # Handle nested attributes with defensive programming using ZscalerCollection
            self.rules = ZscalerCollection.form_list(config["rules"], dict) if "rules" in config else []
            self.associated_inspection_profile_names = ZscalerCollection.form_list(config["associatedInspectionProfileNames"], dict) if "associatedInspectionProfileNames" in config else []
        else:
            self.id = None
            self.name = None
            self.action = None
            self.action_value = None
            self.control_number = None
            self.control_type = None
            self.creation_time = None
            self.default_action = None
            self.default_action_value = None
            self.description = None
            self.modified_by = None
            self.modified_time = None
            self.paranoia_level = None
            self.protocol_type = None
            self.severity = None
            self.version = None
            self.rules = []
            self.associated_inspection_profile_names = []

    def request_format(self):
        """
        Formats the Inspection Control data into a dictionary suitable for API requests.
        """
        return {
            "id": self.id,
            "name": self.name,
            "action": self.action,
            "actionValue": self.action_value,
            "controlNumber": self.control_number,
            "controlType": self.control_type,
            "creationTime": self.creation_time,
            "defaultAction": self.default_action,
            "defaultActionValue": self.default_action_value,
            "description": self.description,
            "modifiedBy": self.modified_by,
            "modifiedTime": self.modified_time,
            "paranoiaLevel": self.paranoia_level,
            "protocolType": self.protocol_type,
            "severity": self.severity,
            "version": self.version,
            "rules": self.rules,  # no need for transformation if already a list of dictionaries
            "associatedInspectionProfileNames": self.associated_inspection_profile_names,
        }


class AppProtectionCustomControl(ZscalerObject):
    """
    A class representing the App Protection Custom Control.
    """

    def __init__(self, config=None):
        super().__init__(config)
        if config:
            self.id = config["id"] if "id" in config else None
            self.modified_time = config["modifiedTime"]\
                if "modifiedTime" in config else None
            self.creation_time = config["creationTime"]\
                if "creationTime" in config else None
            self.modified_by = config["modifiedBy"]\
                if "modifiedBy" in config else None
            self.name = config["name"]\
                if "name" in config else None
            self.description = config["description"]\
                if "description" in config else None
            self.severity = config["severity"]\
                if "severity" in config else None
            self.control_number = config["controlNumber"]\
                if "controlNumber" in config else None
            self.version = config["version"]\
                if "version" in config else None
            self.paranoia_level = config["paranoiaLevel"]\
                if "paranoiaLevel" in config else None
            self.default_action = config["defaultAction"]\
                if "defaultAction" in config else None
            self.protocol_type = config["protocolType"]\
                if "protocolType" in config else None
            self.type = config["type"]\
                if "type" in config else None
            self.control_rule_json = config["controlRuleJson"]\
                if "controlRuleJson" in config else None
        else:
            self.id = None
            self.modified_time = None
            self.creation_time = None
            self.modified_by = None
            self.name = None
            self.description = None
            self.severity = None
            self.control_number = None
            self.version = None
            self.paranoia_level = None
            self.default_action = None
            self.protocol_type = None
            self.type = None
            self.control_rule_json = None

    def request_format(self):
        """
        Formats the App Protection Custom Control data into a dictionary suitable for API requests.
        """
        return {
            "id": self.id,
            "modifiedTime": self.modified_time,
            "creationTime": self.creation_time,
            "modifiedBy": self.modified_by,
            "name": self.name,
            "description": self.description,
            "severity": self.severity,
            "controlNumber": self.control_number,
            "version": self.version,
            "paranoiaLevel": self.paranoia_level,
            "defaultAction": self.default_action,
            "protocolType": self.protocol_type,
            "type": self.type,
            "controlRuleJson": self.control_rule_json,
        }


class PredefinedInspectionControl(ZscalerObject):
    """
    A class representing the Predefined Inspection Control.
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
            self.name = config["name"]\
                if "name" in config else None
            self.description = config["description"]\
                if "description" in config else None
            self.severity = config["severity"]\
                if "severity" in config else None
            self.control_number = config["controlNumber"]\
                if "controlNumber" in config else None
            self.version = config["version"]\
                if "version" in config else None
            self.paranoia_level = config["paranoiaLevel"]\
                if "paranoiaLevel" in config else None
            self.default_action = config["defaultAction"]\
                if "defaultAction" in config else None
            self.control_type = config["controlType"]\
                if "controlType" in config else None
            self.protocol_type = config["protocolType"]\
                if "protocolType" in config else None
            self.control_group = config["controlGroup"]\
                if "controlGroup" in config else None

            # Handle associatedInspectionProfileNames using ZscalerCollection and the InspectionProfile class
            self.associated_inspection_profile_names = (
                ZscalerCollection.form_list(config["associatedInspectionProfileNames"], InspectionProfile)
                if "associatedInspectionProfileNames" in config
                else []
            )
        else:
            self.id = None
            self.modified_time = None
            self.creation_time = None
            self.name = None
            self.description = None
            self.severity = None
            self.control_number = None
            self.version = None
            self.paranoia_level = None
            self.default_action = None
            self.control_type = None
            self.protocol_type = None
            self.control_group = None
            self.associated_inspection_profile_names = []

    def request_format(self):
        """
        Formats the Predefined Inspection Control data into a dictionary suitable for API requests.
        """
        return {
            "id": self.id,
            "modifiedTime": self.modified_time,
            "creationTime": self.creation_time,
            "name": self.name,
            "description": self.description,
            "severity": self.severity,
            "controlNumber": self.control_number,
            "version": self.version,
            "paranoiaLevel": self.paranoia_level,
            "defaultAction": self.default_action,
            "controlType": self.control_type,
            "protocolType": self.protocol_type,
            "controlGroup": self.control_group,
            "associatedInspectionProfileNames": [
                profile.request_format() for profile in self.associated_inspection_profile_names
            ],
        }