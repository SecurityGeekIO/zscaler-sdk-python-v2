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


class AdminUsers:
    def __init__(
        self,
        id: int,
        login_name: Optional[str] = None,
        user_name: Optional[str] = None,
        email: Optional[str] = None,
        comments: Optional[str] = None,
        disabled: Optional[bool] = None,
        password: Optional[str] = None,
        pwd_last_modified_time: Optional[int] = None,
        is_non_editable: Optional[bool] = None,
        is_password_login_allowed: Optional[bool] = None,
        is_password_expired: Optional[bool] = None,
        is_auditor: Optional[bool] = None,
        is_security_report_comm_enabled: Optional[bool] = None,
        is_service_update_comm_enabled: Optional[bool] = None,
        is_product_update_comm_enabled: Optional[bool] = None,
        is_exec_mobile_app_enabled: Optional[bool] = None,
        admin_scope_group_member_entities: Optional[List[Dict[str, Any]]] = None,
        admin_scope_entities: Optional[List[Dict[str, Any]]] = None,
        admin_scope_type: Optional[str] = None,
        role: Optional[Dict[str, Any]] = None,
        exec_mobile_app_tokens: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ):
        self.id = id
        self.login_name = login_name
        self.user_name = user_name
        self.email = email
        self.comments = comments
        self.disabled = disabled
        self.password = password
        self.pwd_last_modified_time = pwd_last_modified_time
        self.is_non_editable = is_non_editable
        self.is_password_login_allowed = is_password_login_allowed
        self.is_password_expired = is_password_expired
        self.is_auditor = is_auditor
        self.is_security_report_comm_enabled = is_security_report_comm_enabled
        self.is_service_update_comm_enabled = is_service_update_comm_enabled
        self.is_product_update_comm_enabled = is_product_update_comm_enabled
        self.is_exec_mobile_app_enabled = is_exec_mobile_app_enabled
        self.admin_scope_group_member_entities = admin_scope_group_member_entities
        self.admin_scope_entities = admin_scope_entities
        self.admin_scope_type = admin_scope_type
        self.role = role
        self.exec_mobile_app_tokens = exec_mobile_app_tokens

        # Store any additional keyword arguments as attributes
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_api_payload(self):
        payload = {}
        for key, value in self.__dict__.items():
            if value is not None:
                payload[snake_to_camel(key)] = value
        return payload


class AdminUsersService:
    admin_users_endpoint = "/adminUsers"

    def __init__(self, client: ZCONClient):
        self.client = client

    def _check_response(self, response: Response) -> Union[None, dict]:
        if isinstance(response, Response):
            status_code = response.status_code
            if status_code > 299:
                raise Exception(f"Request failed with status code: {status_code}")
        return response

    def get(self, admin_user_id: int) -> Optional[AdminUsers]:
        response = self.client.get(f"{self.admin_users_endpoint}/{admin_user_id}")
        data = self._check_response(response)
        return AdminUsers(**data)

    def get_by_login_name(self, admin_users_login_name: str) -> Optional[AdminUsers]:
        admin_users = self.get_all_admin_users()
        for admin_user in admin_users:
            if admin_user.login_name.lower() == admin_users_login_name.lower():
                return admin_user
        raise Exception(f"No admin user found with login name: {admin_users_login_name}")

    def get_by_username(self, admin_username: str) -> Optional[AdminUsers]:
        admin_users = self.get_all_admin_users()
        for admin_user in admin_users:
            if admin_user.user_name.lower() == admin_username.lower():
                return admin_user
        raise Exception(f"No admin user found with username: {admin_username}")

    def create(self, admin_user: AdminUsers) -> Optional[AdminUsers]:
        payload = admin_user.to_api_payload()
        response = self.client.post(self.admin_users_endpoint, json=payload)
        data = self._check_response(response)
        return AdminUsers(**data)

    def update(self, admin_user_id: int, admin_user: AdminUsers) -> Optional[AdminUsers]:
        payload = admin_user.to_api_payload()
        response = self.client.put(f"{self.admin_users_endpoint}/{admin_user_id}", json=payload)
        data = self._check_response(response)
        return AdminUsers(**data)

    def delete(self, admin_user_id: int) -> None:
        response = self.client.delete(f"{self.admin_users_endpoint}/{admin_user_id}")
        self._check_response(response)

    def get_all_admin_users(self) -> List[AdminUsers]:
        response = self.client.get(f"{self.admin_users_endpoint}?includeAuditorUsers=true&includeAdminUsers=true")
        data = self._check_response(response)
        return [AdminUsers(**user) for user in data]
