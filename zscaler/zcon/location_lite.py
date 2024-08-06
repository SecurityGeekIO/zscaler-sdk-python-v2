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

from typing import List, Optional, Any, Dict, Union
from requests import Response
from zscaler.zcon.client import ZCONClient


class LocationLiteService:
    locations_lite_endpoint = "/location/lite"

    def __init__(self, client: ZCONClient):
        self.client = client

    def _check_response(self, response: Response):
        if isinstance(response, Response):
            status_code = response.status_code
            if status_code > 299:
                raise Exception(f"Request failed with status code: {status_code}")
        return response

    def get(self, location_id: int):
        all_loc = self.get_all()
        if all_loc:
            for loc in all_loc:
                if loc.get("id") == location_id:
                    return loc
        return None

    def get_by_name(self, location_name: str):
        response = self.client.get(f"{self.locations_lite_endpoint}?name={location_name}")
        data = self._check_response(response)
        if data:
            for loc in data:
                if loc.get("name", "").lower() == location_name.lower():
                    return loc
        raise ValueError(f"No location found with name: {location_name}")

    def get_all(self):
        response, _ = self.client.get_paginated_data(path=self.locations_lite_endpoint)
        data = self._check_response(response)
        if data:
            return [loc for loc in data]
        return []
