# -*- coding: utf-8 -*-

# Copyright (c) 2023, Zscaler Inc.
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

from typing import Optional, List, Dict, Any, Union

from zscaler.utils import snake_to_camel
from zscaler.zcon.client import ZCONClient
from requests import Response


class APIKeyProvisioningService:
    api_keys_endpoint = "/apiKeys"
    regenerate_api_keys_endpoint = "/regenerate"

    def __init__(self, client: ZCONClient):
        self.client = client

    def _check_response(self, response: Response):
        if isinstance(response, Response):
            status_code = response.status_code
            if status_code > 299:
                raise Exception(f"Request failed with status code: {status_code}")
        return response

    def get(self, api_key_id: int):
        response = self.client.get(f"{self.api_keys_endpoint}/{api_key_id}")
        data = self._check_response(response)
        return data

    def get_partner_api_key(self, api_key_value: str, include_partner_key: bool):
        url = f"{self.api_keys_endpoint}?includePartnerKey={str(include_partner_key).lower()}"
        response = self.client.get(url)
        data = self._check_response(response)
        api_keys = [key for key in data]
        for key in api_keys:
            if key.get("key_value") == api_key_value:
                return key
        raise ValueError(f"No partner API key found with key value: {api_key_value}")

    def list_all(self):
        response = self.client.get(path=self.api_keys_endpoint)
        data = self._check_response(response)
        return [key for key in data]

    def create(
        self,
        key_value: Optional[str] = None,
        permissions: Optional[List[str]] = None,
        enabled: bool = False,
        include_partner_key: bool = False,
        key_id: Optional[int] = None,
        **kwargs,
    ):
        payload = {
            "keyValue": key_value,
            "permissions": permissions,
            "enabled": enabled,
        }

        # Add optional parameters to payload
        payload.update({snake_to_camel(k): v for k, v in kwargs.items() if v is not None})

        if key_id is not None:
            url = f"{self.api_keys_endpoint}/{key_id}{self.regenerate_api_keys_endpoint}?includePartnerKey={str(include_partner_key).lower()}"
        else:
            url = f"{self.api_keys_endpoint}?includePartnerKey={str(include_partner_key).lower()}"

        response = self.client.post(url, json=payload)
        data = self._check_response(response)
        return data
