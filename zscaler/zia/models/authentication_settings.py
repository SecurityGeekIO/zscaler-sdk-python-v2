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

class AuthenticationSettings(ZscalerObject):
    """
    A class for Authentication Settings objects.
    """

    def __init__(self, config=None):
        """
        Initialize the Authentication Settings model based on API response.

        Args:
            config (dict): A dictionary representing the Authentication Settings configuration.
        """
        super().__init__(config)
        if config:
            # Safely extract 'urls' from the config, default to an empty list if not present or not valid
            self.urls = config.get("urls", [])
            if not isinstance(self.urls, list):
                self.urls = []  # Fallback to empty list if 'urls' is not a list
        else:
            self.urls = []  # Fallback to empty list if config is None

    def request_format(self):
        """
        Return a dictionary formatted for the request body when submitting or modifying data.
        """
        parent_req_format = super().request_format()
        current_obj_format = {
            "urls": self.urls
        }
        parent_req_format.update(current_obj_format)
        return parent_req_format
