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

class CBIBanner(ZscalerObject):
    def __init__(self, config=None):
        """
        Initialize the CBIBanner model based on API response.

        Args:
            config (dict): A dictionary representing the cloud browser isolation banner.
        """
        super().__init__(config)

        # Using defensive programming to check each key's presence
        self.id = config["id"]\
            if config and "id" in config else None
        self.name = config["name"]\
            if config and "name" in config else None
        self.primary_color = config["primaryColor"]\
            if config and "primaryColor" in config else None
        self.text_color = config["textColor"]\
            if config and "textColor" in config else None
        self.notification_title = config["notificationTitle"]\
            if config and "notificationTitle" in config else None
        self.notification_text = config["notificationText"]\
            if config and "notificationText" in config else None
        self.logo = config["logo"]\
            if config and "logo" in config else None
        self.banner = config["banner"]\
            if config and "banner" in config else None
        self.persist = config["persist"]\
            if config and "persist" in config else None
        self.is_default = config["isDefault"]\
            if config and "isDefault" in config else None

    def request_format(self):
        """
        Formats the model data for API requests.
        """
        parent_req_format = super().request_format()
        current_obj_format = {
            "id": self.id,
            "name": self.name,
            "primaryColor": self.primary_color,
            "textColor": self.text_color,
            "notificationTitle": self.notification_title,
            "notificationText": self.notification_text,
            "logo": self.logo,
            "banner": self.banner,
            "persist": self.persist,
            "isDefault": self.is_default,
        }
        parent_req_format.update(current_obj_format)
        return parent_req_format

class CBICertificate(ZscalerObject):
    """
    A class representing a Cloud Browser Isolation Certificate object.
    """

    def __init__(self, config=None):
        """
        Initialize the CBICertificate model based on API response.

        Args:
            config (dict): A dictionary representing the cloud browser isolation certificate.
        """
        super().__init__(config)

        self.id = config["id"]\
            if config and "id" in config else None
        self.name = config["name"]\
            if config and "name" in config else None
        self.is_default = config["isDefault"]\
            if config and "isDefault" in config else False

    def request_format(self):
        """
        Prepare the object in a format suitable for sending as a request payload.

        Returns:
            dict: A dictionary representing the CBICertificate for API requests.
        """
        parent_req_format = super().request_format()
        current_obj_format = {
            "id": self.id,
            "name": self.name,
            "isDefault": self.is_default
        }
        parent_req_format.update(current_obj_format)
        return parent_req_format

class CBIProfile(ZscalerObject):
    """
    A class representing a Cloud Browser Isolation Profile object.
    """

    def __init__(self, config=None):
        """
        Initialize the CBIProfile model based on API response.

        Args:
            config (dict): A dictionary representing the cloud browser isolation profile.
        """
        super().__init__(config)

        self.id = config["id"]\
            if config and "id" in config else None
        self.name = config["name"]\
            if config and "name" in config else None
        self.is_default = config["isDefault"]\
            if config and "isDefault" in config else False
        
        # Handle nested regions as list of dictionaries
        self.regions = [
            {
                "name": region.get("name"),
                "id": region.get("id")
            }
            for region in config["regions"] if config and "regions" in config
        ] if config else []

        # Handle nested security controls
        security_controls = config["securityControls"]\
            if config and "securityControls" in config else {}
        self.security_controls = {
            "documentViewer": security_controls.get("documentViewer", False),
            "allowPrinting": security_controls.get("allowPrinting", True),
            "watermark": {
                "enabled": security_controls.get("watermark", {}).get("enabled", False)
            },
            "flattenedPdf": security_controls.get("flattenedPdf", False),
            "uploadDownload": security_controls.get("uploadDownload", "all"),
            "restrictKeystrokes": security_controls.get("restrictKeystrokes", False),
            "copyPaste": security_controls.get("copyPaste", "all"),
            "localRender": security_controls.get("localRender", True)
        }

    def request_format(self):
        """
        Prepare the object in a format suitable for sending as a request payload.

        Returns:
            dict: A dictionary representing the CBI profile for API requests.
        """
        parent_req_format = super().request_format()
        current_obj_format = {
            "id": self.id,
            "name": self.name,
            "isDefault": self.is_default,
            "regions": [
                {
                    "name": region["name"],
                    "id": region["id"]
                }
                for region in self.regions
            ],
            "securityControls": {
                "documentViewer": self.security_controls["documentViewer"],
                "allowPrinting": self.security_controls["allowPrinting"],
                "watermark": {
                    "enabled": self.security_controls["watermark"]["enabled"]
                },
                "flattenedPdf": self.security_controls["flattenedPdf"],
                "uploadDownload": self.security_controls["uploadDownload"],
                "restrictKeystrokes": self.security_controls["restrictKeystrokes"],
                "copyPaste": self.security_controls["copyPaste"],
                "localRender": self.security_controls["localRender"]
            }
        }
        parent_req_format.update(current_obj_format)
        return parent_req_format

class ZPACBIProfile(ZscalerObject):
    """
    A class representing a ZPA Profile object.
    """

    def __init__(self, config=None):
        """
        Initialize the ZPAProfile model based on API response.

        Args:
            config (dict): A dictionary containing ZPA profile data.
        """
        super().__init__(config)

        self.id = config["id"]\
            if config and "id" in config else None
        self.modified_time = config["modifiedTime"]\
            if config and "modifiedTime" in config else None
        self.creation_time = config["creationTime"]\
            if config and "creationTime" in config else None
        self.modified_by = config["modifiedBy"]\
            if config and "modifiedBy" in config else None
        self.name = config["name"]\
            if config and "name" in config else None
        self.cbi_tenant_id = config["cbiTenantId"]\
            if config and "cbiTenantId" in config else None
        self.cbi_profile_id = config["cbiProfileId"]\
            if config and "cbiProfileId" in config else None
        self.description = config["description"]\
            if config and "description" in config else None
        self.cbi_url = config["cbiUrl"]\
            if config and "cbiUrl" in config else None
        self.enabled = config["enabled"]\
            if config and "enabled" in config else True

    def request_format(self):
        """
        Prepare the object in a format suitable for sending as a request payload.

        Returns:
            dict: A dictionary representing the ZPA profile for API requests.
        """
        parent_req_format = super().request_format()
        current_obj_format = {
            "id": self.id,
            "modifiedTime": self.modified_time,
            "creationTime": self.creation_time,
            "modifiedBy": self.modified_by,
            "name": self.name,
            "cbiTenantId": self.cbi_tenant_id,
            "cbiProfileId": self.cbi_profile_id,
            "description": self.description,
            "cbiUrl": self.cbi_url,
            "enabled": self.enabled,
        }
        parent_req_format.update(current_obj_format)
        return parent_req_format

class CBIRegion(ZscalerObject):
    """
    A class representing a Cloud Browser Isolation Region object.
    """

    def __init__(self, config=None):
        """
        Initialize the CBIRegion object.

        Args:
            config (dict): A dictionary representing the cloud browser isolation region.
        """
        super().__init__(config)

        # Defensive strategy for initializing each field
        self.id = config["id"]\
            if config and "id" in config else None
        self.name = config["name"]\
            if config and "name" in config else None

    def request_format(self):
        """
        Prepare the object in a format suitable for sending as a request payload.

        Returns:
            dict: A dictionary representing the CBI region for API requests.
        """
        return {
            "id": self.id,
            "name": self.name
        }
