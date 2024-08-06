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

from typing import Dict, Any, Optional, Union

from requests import Response

from zscaler.utils import snake_to_camel
from zscaler.zcon.client import ZCONClient


class ActivationService:
    ec_admin_activate_status_endpoint = "/ecAdminActivateStatus"
    ec_admin_activate_endpoint = "/ecAdminActivateStatus/activate"
    ec_admin_force_activate_endpoint = "/ecAdminActivateStatus/forcedActivate"

    def __init__(self, client: ZCONClient):
        self.client = client

    def _check_response(self, response: Response):
        if isinstance(response, Response):
            status_code = response.status_code
            if status_code > 299:
                raise Exception(f"Request failed with status code: {status_code}")
        return response

    def get_activation_status(self):
        response = self.client.get(self.ec_admin_activate_status_endpoint)
        data = self._check_response(response)
        return data

    def update_activation_status(
        self,
        org_edit_status: Optional[str] = None,
        org_last_activate_status: Optional[str] = None,
        admin_status_map: Optional[Dict[str, Any]] = None,
        admin_activate_status: Optional[str] = None,
    ):
        payload = {
            "orgEditStatus": org_edit_status,
            "org_last_activateStatus": org_last_activate_status,
            "adminStatusMap": admin_status_map,
            "adminAtivateStatus": admin_activate_status,
        }
        response = self.client.put(self.ec_admin_activate_endpoint, json=payload)
        data = self._check_response(response)
        return data

    def force_activation_status(
        self,
        org_edit_status: Optional[str] = None,
        org_last_activate_status: Optional[str] = None,
        admin_status_map: Optional[Dict[str, Any]] = None,
        admin_activate_status: Optional[str] = None,
    ):
        payload = {
            "orgEditStatus": org_edit_status,
            "org_last_activateStatus": org_last_activate_status,
            "adminStatusMap": admin_status_map,
            "adminAtivateStatus": admin_activate_status,
        }
        response = self.client.put(self.ec_admin_force_activate_endpoint, json=payload)
        data = self._check_response(response)
        return data
