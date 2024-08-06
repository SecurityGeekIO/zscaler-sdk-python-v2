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

from typing import List, Optional, Dict, Any, Union

from zscaler.utils import recursive_snake_to_camel, snake_to_camel
from zscaler.zcon.client import ZCONClient
from typing import List, Optional
from requests import Response


class LocationService:
    locations_endpoint = "/location"

    def __init__(self, client: ZCONClient):
        self.client = client

    def _check_response(self, response: Response):
        if isinstance(response, Response):
            status_code = response.status_code
            if status_code > 299:
                raise Exception(f"Request failed with status code: {status_code}")
        return response

    def get(self, location_id: int):
        response = self.client.get(f"{self.locations_endpoint}/{location_id}")
        data = self._check_response(response)
        return data

    def get_by_name(self, location_name: str):
        response = self.client.get(self.locations_endpoint)
        data = self._check_response(response)
        locations = [loc for loc in data]
        for location in locations:
            if location.get("name", "").lower() == location_name.lower():
                return location
        raise ValueError(f"No location found with name: {location_name}")

    def create(
        self,
        name: Optional[str] = None,
        country: Optional[str] = None,
        state: Optional[str] = None,
        language: Optional[str] = None,
        **kwargs,
    ):
        payload = {
            "name": name,
            "country": country,
            "state": state,
            "language": language,
        }

        # Add optional parameters to payload
        payload.update({recursive_snake_to_camel(k): v for k, v in kwargs.items() if v is not None})
        response = self.client.post(self.locations_endpoint, json=payload)
        data = self._check_response(response)
        return data

    def update(
        self,
        location_id: int,
        name: Optional[str] = None,
        country: Optional[str] = None,
        state: Optional[str] = None,
        language: Optional[str] = None,
        **kwargs,
    ):
        payload = {
            "name": name,
            "country": country,
            "state": state,
            "language": language,
        }

        # Add optional parameters to payload
        payload.update({recursive_snake_to_camel(k): v for k, v in kwargs.items() if v is not None})
        response = self.client.put(f"{self.locations_endpoint}/{location_id}", json=payload)
        data = self._check_response(response)
        return data

    def delete(self, location_id: int) -> None:
        response = self.client.delete(f"{self.locations_endpoint}/{location_id}")
        self._check_response(response)

    def get_all(self):
        response, _ = self.client.get_paginated_data(path=self.locations_endpoint)
        data = self._check_response(response)
        locations = [loc for loc in data]
        return locations
