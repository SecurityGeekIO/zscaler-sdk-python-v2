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
from requests import Response, utils
from zscaler.utils import snake_to_camel
from zscaler.zcon.client import ZCONClient


class AdminRoles:
    def __init__(
        self,
        id: int,
        rank: Optional[int] = None,
        name: Optional[str] = None,
        policy_access: Optional[str] = None,
        alerting_access: Optional[str] = None,
        dashboard_access: Optional[str] = None,
        report_access: Optional[str] = None,
        analysis_access: Optional[str] = None,
        username_access: Optional[str] = None,
        admin_acct_access: Optional[str] = None,
        device_info_access: Optional[str] = None,
        is_auditor: Optional[bool] = None,
        permissions: Optional[List[str]] = None,
        is_non_editable: Optional[bool] = None,
        logs_limit: Optional[str] = None,
        role_type: Optional[str] = None,
        feature_permissions: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        self.id = id
        self.rank = rank
        self.name = name
        self.policy_access = policy_access
        self.alerting_access = alerting_access
        self.dashboard_access = dashboard_access
        self.report_access = report_access
        self.analysis_access = analysis_access
        self.username_access = username_access
        self.admin_acct_access = admin_acct_access
        self.device_info_access = device_info_access
        self.is_auditor = is_auditor
        self.permissions = permissions
        self.is_non_editable = is_non_editable
        self.logs_limit = logs_limit
        self.role_type = role_type
        self.feature_permissions = feature_permissions

        # Store any additional keyword arguments as attributes
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_api_payload(self):
        payload = {}
        for key, value in self.__dict__.items():
            if value is not None:
                payload[snake_to_camel(key)] = value
        return payload


class AdminRolesService:
    admin_roles_endpoint = "/adminRoles"

    def __init__(self, client: ZCONClient):
        self.client = client

    def _check_response(self, response: Response) -> Union[None, dict]:
        if isinstance(response, Response):
            status_code = response.status_code
            if status_code > 299:
                raise Exception(f"Request failed with status code: {status_code}")
        return response

    def get(self, admin_role_id: int) -> Optional[AdminRoles]:
        """
        getting: HTTP Status 405 - Method Not Allowed
        """
        response = self.get_all_admin_roles()
        for r in response:
            if r.id == admin_role_id:
                return r
        raise Exception(f"Failed to get admin role by ID {admin_role_id}, not found")

    def get_by_name(self, admin_role_name: str) -> Optional[AdminRoles]:
        response = self.client.get(self.admin_roles_endpoint)
        data = self._check_response(response)
        admin_roles = [AdminRoles(**role) for role in data]
        for admin_role in admin_roles:
            if admin_role.name.lower() == admin_role_name.lower():
                return admin_role
        raise Exception(f"No admin role found with name: {admin_role_name}")

    def get_api_role(self, api_role: str) -> Optional[AdminRoles]:
        response = self.client.get(f"{self.admin_roles_endpoint}?includeApiRole={utils.quote(api_role)}")
        data = self._check_response(response)
        admin_roles = [AdminRoles(**role) for role in data]
        for admin_role in admin_roles:
            if admin_role.name.lower() == api_role.lower():
                return admin_role
        raise Exception(f"No API role found with name: {api_role}")

    def get_auditor_role(self, auditor_role: str) -> Optional[AdminRoles]:
        response = self.client.get(f"{self.admin_roles_endpoint}?includeAuditorRole={utils.quote(auditor_role)}")
        data = self._check_response(response)
        admin_roles = [AdminRoles(**role) for role in data]
        for admin_role in admin_roles:
            if admin_role.name.lower() == auditor_role.lower():
                return admin_role
        raise Exception(f"No auditor role found with name: {auditor_role}")

    def get_partner_role(self, partner_role: str) -> Optional[AdminRoles]:
        response = self.client.get(f"{self.admin_roles_endpoint}?includePartnerRole={utils.quote(partner_role)}")
        data = self._check_response(response)
        admin_roles = [AdminRoles(**role) for role in data]
        for admin_role in admin_roles:
            if admin_role.name.lower() == partner_role.lower():
                return admin_role
        raise Exception(f"No partner role found with name: {partner_role}")

    def get_all_admin_roles(self) -> List[AdminRoles]:
        response = self.client.get(self.admin_roles_endpoint)
        data = self._check_response(response)
        return [AdminRoles(**role) for role in data]

    def create(self, admin_role: AdminRoles) -> Optional[AdminRoles]:
        payload = admin_role.to_api_payload()
        response = self.client.post(self.admin_roles_endpoint, json=payload)
        data = self._check_response(response)
        return AdminRoles(**data)

    def update(self, admin_role_id: int, admin_role: AdminRoles) -> Optional[AdminRoles]:
        payload = admin_role.to_api_payload()
        response = self.client.put(f"{self.admin_roles_endpoint}/{admin_role_id}", json=payload)
        data = self._check_response(response)
        return AdminRoles(**data)

    def delete(self, admin_role_id: int) -> None:
        response = self.client.delete(f"{self.admin_roles_endpoint}/{admin_role_id}")
        self._check_response(response)
