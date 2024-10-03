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
from zscaler.zpa.models import trusted_network\
    as trusted_networks
from zscaler.zpa.models import service_edges\
    as service_edges
    
class ServiceEdgeGroup(ZscalerObject):
    """
    A class representing the Service Edge Group.
    """

    def __init__(self, config=None):
        super().__init__(config)
        if config:
            self.id = config["id"] if "id" in config else None
            self.name = config["name"] if "name" in config else None
            self.enabled = config["enabled"] if "enabled" in config else True
            self.latitude = config["latitude"] if "latitude" in config else None
            self.longitude = config["longitude"] if "longitude" in config else None
            self.location = config["location"] if "location" in config else None
            self.version_profile_id = config["versionProfileId"] if "versionProfileId" in config else None
            self.override_version_profile = config["overrideVersionProfile"] if "overrideVersionProfile" in config else False
            self.city_country = config["cityCountry"] if "cityCountry" in config else None
            self.country_code = config["countryCode"] if "countryCode" in config else None
            self.upgrade_day = config["upgradeDay"] if "upgradeDay" in config else None
            self.upgrade_time_in_secs = config["upgradeTimeInSecs"] if "upgradeTimeInSecs" in config else None
            self.is_public = config["isPublic"] if "isPublic" in config else False
            self.trusted_networks = ZscalerCollection.form_list(config["trustedNetworks"], trusted_networks.TrustedNetwork) if "trustedNetworks" in config else []
            self.service_edges = ZscalerCollection.form_list(config["serviceEdges"], service_edges.ServiceEdge) if "serviceEdges" in config else []
        else:
            self.id = None
            self.name = None
            self.enabled = True
            self.latitude = None
            self.longitude = None
            self.location = None
            self.version_profile_id = None
            self.override_version_profile = False
            self.city_country = None
            self.country_code = None
            self.upgrade_day = None
            self.upgrade_time_in_secs = None
            self.is_public = False
            self.trusted_networks = []
            self.service_edges = []

    def request_format(self):
        """
        Formats the Service Edge Group data into a dictionary suitable for API requests.
        """
        return {
            "id": self.id,
            "name": self.name,
            "enabled": self.enabled,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "location": self.location,
            "versionProfileId": self.version_profile_id,
            "overrideVersionProfile": self.override_version_profile,
            "cityCountry": self.city_country,
            "countryCode": self.country_code,
            "upgradeDay": self.upgrade_day,
            "upgradeTimeInSecs": self.upgrade_time_in_secs,
            "isPublic": self.is_public,
            "trustedNetworks": [tn.request_format() for tn in self.trusted_networks],
            "serviceEdges": [se.request_format() for se in self.service_edges],
        }
