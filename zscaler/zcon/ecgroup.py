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

from typing import List, Dict, Any, Optional, Union
from zscaler.utils import snake_to_camel
from zscaler.zcon.client import ZCONClient
from requests import Response
import logging


class EcGroupService:
    ecgroup_endpoint = "/ecgroup"
    ecgroup_lite_endpoint = "/ecgroup/lite"

    def __init__(self, client: ZCONClient):
        self.client = client
        self.logger = logging.getLogger(__name__)

    def _check_response(self, response: Response):
        if isinstance(response, Response):
            status_code = response.status_code
            if status_code > 299:
                raise Exception(f"Request failed with status code: {status_code}")
        return response

    def get(self, ecgroup_id: int):
        response = self.client.get(f"{self.ecgroup_endpoint}/{ecgroup_id}")
        data = self._check_response(response)
        return data

    def get_by_name(self, ecgroup_name: str):
        response = self.client.get(self.ecgroup_endpoint)
        data = self._check_response(response)
        ecgroups = [ecgroup for ecgroup in data]
        for ecgroup in ecgroups:
            if ecgroup.get("name", "").lower() == ecgroup_name.lower():
                return ecgroup
        raise Exception(f"No EC Group found with name: {ecgroup_name}")

    def delete(self, ecgroup_id: int) -> None:
        response = self.client.delete(f"{self.ecgroup_endpoint}/{ecgroup_id}")
        self._check_response(response)

    def get_all(self):
        response = self.client.get(self.ecgroup_endpoint)
        data = self._check_response(response)
        return [ecgroup for ecgroup in data]

    def get_ecgroup_lite(self, ecgroup_id: int):
        response = self.client.get(f"{self.ecgroup_lite_endpoint}")
        data = self._check_response(response)
        ecgroups = [ecgroup for ecgroup in data]
        for ecgroup in ecgroups:
            if ecgroup.get("id") == ecgroup_id:
                return ecgroup
        raise Exception(f"No EC Group Lite found with ID: {ecgroup_id}")

    def get_ecgroup_lite_by_name(self, ecgroup_name: str):
        response = self.client.get(f"{self.ecgroup_lite_endpoint}?name={ecgroup_name}")
        data = self._check_response(response)
        ecgroups = [ecgroup for ecgroup in data]
        for ecgroup in ecgroups:
            if ecgroup.get("name", "").lower() == ecgroup_name.lower():
                return ecgroup
        raise Exception(f"No EC Group Lite found with name: {ecgroup_name}")
