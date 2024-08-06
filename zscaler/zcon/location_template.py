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

from zscaler.utils import recursive_snake_to_camel, snake_to_camel
from zscaler.zcon.client import ZCONClient
from requests import Response


class LocationTemplateService:
    location_template_endpoint = "/locationTemplate"

    def __init__(self, client: ZCONClient):
        self.client = client

    def _check_response(self, response: Response):
        if isinstance(response, Response):
            status_code = response.status_code
            if status_code > 299:
                raise Exception(f"Request failed with status code: {status_code}")
        return response

    def get(self, loc_template_id: int):
        response = self.client.get(f"{self.location_template_endpoint}/{loc_template_id}")
        data = self._check_response(response)
        return data

    def get_by_name(self, template_name: str):
        response = self.client.get(self.location_template_endpoint)
        data = self._check_response(response)
        templates = [tpl for tpl in data]
        for template in templates:
            if template.get("name", "").lower() == template_name.lower():
                return template
        raise ValueError(f"No location template found with name: {template_name}")

    def create(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        **kwargs,
    ):
        payload = {
            "name": name,
            "description": description,
        }

        # Add optional parameters to payload
        payload.update({recursive_snake_to_camel(k): v for k, v in kwargs.items() if v is not None})
        response = self.client.post(self.location_template_endpoint, json=payload)
        data = self._check_response(response)
        return data

    def update(
        self,
        loc_template_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        **kwargs,
    ):
        payload = {
            "name": name,
            "description": description,
        }

        # Add optional parameters to payload
        payload.update({recursive_snake_to_camel(k): v for k, v in kwargs.items() if v is not None})
        response = self.client.put(f"{self.location_template_endpoint}/{loc_template_id}", json=payload)
        data = self._check_response(response)
        return data

    def delete(self, loc_template_id: int):
        response = self.client.delete(f"{self.location_template_endpoint}/{loc_template_id}")
        self._check_response(response)

    def get_all(self):
        response, _ = self.client.get_paginated_data(path=self.location_template_endpoint)
        data = self._check_response(response)
        templates = [tpl for tpl in data]
        return templates
