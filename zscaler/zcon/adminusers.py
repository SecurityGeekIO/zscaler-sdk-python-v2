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
from zscaler.utils import snake_to_camel, convert_keys
from zscaler.zcon.client import ZCONClient


class AdminUsersService:
    admin_users_endpoint = "/adminUsers"

    def __init__(self, client: ZCONClient):
        self.client = client

    def _check_response(self, response: Response):
        if isinstance(response, Response):
            status_code = response.status_code
            if status_code > 299:
                raise Exception(f"Request failed with status code: {status_code}")
        return response

    def list_admins(
        self,
        include_auditor_users: Optional[bool] = None,
        include_admin_users: Optional[bool] = None,
        partner_type: Optional[str] = None,
    ):
        """
        List all existing admin users.

        Keyword Args:
            include_auditor_users (bool): Include / exclude auditor users in the response.
            include_admin_users (bool): Include / exclude admin users in the response.
            partner_type (str): The partner type to filter by.

        Returns:
            :obj:`BoxList`: The list of admin users.

        Examples:
            List all admins::

                for admin in zcon.admin.list_admins():
                    print(admin)

            List all admins with advanced features::

                for admin in zcon.admin_users.list_admins(
                    include_auditor_users=True,
                    include_admin_users=True,
                    partner_type="ORG_ADMIN",
                ):
                    print(admin)

        """
        params = {}
        if include_auditor_users is not None:
            params["includeAuditorUsers"] = str(include_auditor_users).lower()
        if include_admin_users is not None:
            params["includeAdminUsers"] = str(include_admin_users).lower()
        if partner_type is not None:
            params["partnerType"] = partner_type

        response = self.client.get(self.admin_users_endpoint, params=params)
        data = self._check_response(response)
        return [user for user in data]

    def get_admin(self, admin_id: int):
        """
        Get details for a specific admin user.

        Args:
            admin_id (str): The ID of the admin user to retrieve.

        Returns:
            :obj:`Box`: The admin user details.

        Examples:
            Print the details of an admin user::

                print(zcon.admin.get_admin("123456789")

        """
        response = self.client.get(f"{self.admin_users_endpoint}/{admin_id}")
        data = self._check_response(response)
        return data

    def get_by_login_name(self, admin_users_login_name: str):
        admin_users = self.list_admins()
        for admin_user in admin_users:
            if admin_user.get("login_name", "").lower() == admin_users_login_name.lower():
                return admin_user
        raise Exception(f"No admin user found with login name: {admin_users_login_name}")

    def get_by_username(self, admin_username: str):
        admin_users = self.list_admins()
        for admin_user in admin_users:
            if admin_user.get("user_name", "").lower() == admin_username.lower():
                return admin_user
        raise Exception(f"No admin user found with username: {admin_username}")

    def add_admin(
        self,
        user_name: str,
        login_name: str,
        role: Union[str, Dict[str, Any]],
        email: str,
        password: str,
        **kwargs,
    ):
        """
        Create a new admin user.

        Args:
            user_name (str): The name of the admin user.
            login_name (str): The login name of the admin user.
            role (Union[str, Dict[str, Any]]): The role of the admin user.
            email (str): The email address of the admin user.
            password (str): The password for the admin user.

        Keyword Args:
            disabled (bool): Indicates whether the admin is disabled.
            new_location_create_allowed (bool): Indicates whether the admin can create new locations.
            admin_scope_type (str): The admin scope type.
            admin_scope_group_member_entity_ids (list): Applicable if the admin scope type is `LOCATION_GROUP`.
            is_default_admin (bool): Indicates whether the admin is the default admin.
            is_deprecated_default_admin (bool): Indicates whether this admin is deletable.
            is_auditor (bool): Indicates whether the admin is an auditor.
            is_security_report_comm_enabled (bool): Indicates whether the admin can receive security reports.
            is_service_update_comm_enabled (bool): Indicates whether the admin can receive service updates.
            is_password_login_allowed (bool): Indicates whether the admin can log in with a password.
            is_product_update_comm_enabled (bool): Indicates whether the admin can receive product updates.
            is_exec_mobile_app_enabled (bool): Indicates whether Executive Insights App access is enabled for the admin.
            send_mobile_app_invite (bool): Indicates whether to send an invitation email to download Executive Insights App to admin.
            send_zdx_onboard_invite (bool): Indicates whether to send an invitation email for ZDX onboarding to admin.
            comments (str): Comments for the admin user.
            name (str): Admin user's "friendly" name, e.g., "FirstName LastName" (this field typically matches userName.)

        Returns:
            :obj:`AdminUsers`: The newly created admin user.

        Examples:
            Create a new admin user with only the required parameters::

                zcon.admin_users.add_admin(
                    user_name="Jane Smith",
                    login_name="jsmith",
                    role="admin",
                    email="jsmith@example.com",
                    password="password123",
                )

            Create a new admin with some additional parameters::

                zcon.admin_users.add_admin(
                    user_name="Jane Smith",
                    login_name="jsmith",
                    role="admin",
                    email="jsmith@example.com",
                    password="password123",
                    is_default_admin=False,
                    disabled=False,
                    comments="New admin user"
                )
        """
        payload = {
            "userName": user_name,
            "loginName": login_name,
            "role": role if isinstance(role, dict) else {"id": role, "name": role},
            "email": email,
            "password": password,
        }

        # Add optional parameters to payload
        payload.update({snake_to_camel(k): v for k, v in kwargs.items() if v is not None})

        response = self.client.post(self.admin_users_endpoint, json=payload)
        data = self._check_response(response)
        return data

    def update_admin(
        self,
        admin_id: int,
        user_name: str,
        login_name: str,
        role: Union[str, Dict[str, Any]],
        email: str,
        password: str,
        **kwargs,
    ):
        """
        Update an existing admin user.

        Args:
            admin_id (str): The ID of the admin user to update.

        Keyword Args:
            role (str): The role of the admin user.
            email (str): The email address of the admin user.
            password (str): The password for the admin user.
            disabled (bool): Indicates whether the admin is disabled.
            new_location_create_allowed (bool): Indicates whether the admin can create new locations.
            admin_scope_type (str): The admin scope type.
            admin_scope_group_member_entity_ids (list): Applicable if the admin scope type is `LOCATION_GROUP`.
            is_default_admin (bool): Indicates whether the admin is the default admin.
            is_deprecated_default_admin (bool): Indicates whether this admin is deletable.
            is_auditor (bool): Indicates whether the admin is an auditor.
            is_security_report_comm_enabled (bool): Indicates whether the admin can receive security reports.
            is_service_update_comm_enabled (bool): Indicates whether the admin can receive service updates.
            is_password_login_allowed (bool): Indicates whether the admin can log in with a password.
            is_product_update_comm_enabled (bool): Indicates whether the admin can receive product updates.
            is_exec_mobile_app_enabled (bool): Indicates whether Executive Insights App access is enabled for the admin.
            send_mobile_app_invite (bool): Indicates whether to send an invitation email to download Executive Insights App to admin.
            send_zdx_onboard_invite (bool): Indicates whether to send an invitation email for ZDX onboarding to admin.
            comments (str): Comments for the admin user.
            name (str): Admin user's "friendly" name, e.g., "FirstName LastName" (this field typically matches userName.)

        Returns:
            :obj:`AdminUsers`: The updated admin user.

        Examples:
            Update an admin user::

                zcon.admin.update_admin(
                    admin_id="123456789",
                    admin_scope_type="LOCATION_GROUP",
                    comments="Updated admin user",
                )
        """
        payload = {
            "userName": user_name,
            "loginName": login_name,
            "role": role if isinstance(role, dict) else {"id": role, "name": role},
            "email": email,
            "password": password,
        }

        # Add optional parameters to payload
        payload.update({snake_to_camel(k): v for k, v in kwargs.items() if v is not None})

        response = self.client.put(f"{self.admin_users_endpoint}/{admin_id}", json=convert_keys(payload))
        data = self._check_response(response)
        return data

    def delete_admin(self, admin_id: int) -> None:
        """
        Delete the specified admin user.

        Args:
            admin_id (str): The ID of the admin user to delete.

        Returns:
            :obj:`int`: The status code of the operation.

        Examples:
            Delete an admin user::

                zcon.admin.delete_admin("123456789")

        """
        response = self.client.delete(f"{self.admin_users_endpoint}/{admin_id}")
        self._check_response(response)
