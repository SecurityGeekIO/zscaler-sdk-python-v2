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


class PublicCloudAccountService:
    public_cloud_endpoint = "/publicCloudAccountDetails"
    public_cloud_endpoint_lite = "/publicCloudAccountDetails/lite"
    public_cloud_account_status = "/publicCloudAccountIdStatus"

    def __init__(self, client: ZCONClient):
        self.client = client

    def _check_response(self, response: Response):
        if isinstance(response, Response):
            status_code = response.status_code
            if status_code > 299:
                raise Exception(f"Request failed with status code: {status_code}")
        return response

    def get(self, account_id: int):
        response = self.client.get(f"{self.public_cloud_endpoint}/{account_id}")
        data = self._check_response(response)
        return data

    def get_lite(self):
        response = self.client.get(self.public_cloud_endpoint_lite)
        data = self._check_response(response)
        return [account for account in data]

    def get_account_status(self):
        response = self.client.get(self.public_cloud_account_status)
        data = self._check_response(response)
        return data

    def get_all(self):
        response, _ = self.client.get_paginated_data(path=self.public_cloud_endpoint)
        data = self._check_response(response)
        return [account for account in data]
