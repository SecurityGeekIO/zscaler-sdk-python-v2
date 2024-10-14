# -*- coding: utf-8 -*-

# Copyright (c) 2023, Zscaler Inc.
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.


from typing import Optional

from zscaler.api_client import APIClient
from zscaler.zpa.models.privileged_remote_access import PrivilegedRemoteAccessPortal
from zscaler.zpa.models.privileged_remote_access import PrivilegedRemoteAccessConsole
from zscaler.zpa.models.privileged_remote_access import PrivilegedRemoteAccessCredential
from zscaler.zpa.models.privileged_remote_access import PrivilegedRemoteAccessApproval
from zscaler.utils import format_url
from urllib.parse import urlencode
from zscaler.utils import is_valid_ssh_key, snake_to_camel, validate_and_convert_times


class PrivilegedRemoteAccessAPI(APIClient):
    def __init__(self, request_executor, config):
        super().__init__()
        self._request_executor = request_executor
        customer_id = config["client"].get("customerId")
        self._base_endpoint = f"/zpa/mgmtconfig/v1/admin/customers/{customer_id}"

    def list_portals(self, query_params=None, keep_empty_params=False) -> tuple:
        """
        Returns a list of all configured PRA portals with pagination support.

        Keyword Args:
            query_params {dict}: Map of query parameters for the request.
                [query_params.pagesize] {int}: Page size for pagination.
                [query_params.search] {str}: Search string for filtering results.
                [query_params.microtenant_id] {str}: ID of the microtenant, if applicable.
                [query_params.max_items] {int}: Maximum number of items to fetch before stopping.
                [query_params.max_pages] {int}: Maximum number of pages to request before stopping.
            keep_empty_params {bool}: Whether to include empty parameters in the query string.

        Returns:
            tuple: A list of `PrivilegedRemoteAccessPortal` instances.
        """
        http_method = "get".upper()
        api_url = format_url(f"{self._base_endpoint}/praPortal")

        # Handle query parameters (including microtenant_id if provided)
        query_params = query_params or {}
        microtenant_id = query_params.pop("microtenant_id", None)
        if microtenant_id:
            query_params["microtenantId"] = microtenant_id

        # Build the query string
        if query_params:
            encoded_query_params = urlencode(query_params)
            api_url += f"?{encoded_query_params}"

        # Prepare request body and headers
        body = {}
        headers = {}
        form = {}

        # Create the request
        request, error = self._request_executor.create_request(
            http_method, api_url, body, headers, form, keep_empty_params=keep_empty_params
        )

        if error:
            return (None, None, error)

        # Execute the request
        response, error = self._request_executor.execute(request, PrivilegedRemoteAccessPortal)

        if error:
            return (None, response, error)

        # Parse the response into AppConnectorGroup instances
        try:
            result = []
            for item in response.get_body():
                result.append(PrivilegedRemoteAccessPortal(self.form_response_body(item)))
        except Exception as error:
            return (None, response, error)

        return (result, response, None)

    def get_portal(self, portal_id: str, **kwargs) -> PrivilegedRemoteAccessPortal:
        """
        Provides information on the specified PRA portal.

        Args:
            portal_id (str): The unique identifier of the portal.

        Returns:
            PrivilegedRemoteAccessPortal: The corresponding portal object.
        """
        http_method = "get".upper()
        api_url = format_url(f"{self._base_endpoint}/praPortal/{portal_id}")

        # Optional parameters such as microtenant_id
        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, {}, params)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return PrivilegedRemoteAccessPortal(response.get_body())

    def add_portal(
        self, name: str, certificate_id: str, domain: str, enabled: bool = True, **kwargs
    ) -> PrivilegedRemoteAccessPortal:
        """
        Adds a new PRA portal.

        Args:
            name (str): The name of the PRA portal.
            certificate_id (str): The unique identifier of the certificate.
            domain (str): The domain of the PRA portal.
            enabled (bool): Whether the PRA portal is enabled (default is True).

        Returns:
            PrivilegedRemoteAccessPortal: The newly created portal object.
        """
        http_method = "post".upper()
        api_url = format_url(f"{self._base_endpoint}/praPortal")

        payload = {
            "name": name,
            "enabled": enabled,
            "certificateId": certificate_id,
            "domain": domain,
        }

        # Add additional optional parameters
        for key, value in kwargs.items():
            payload[snake_to_camel(key)] = value

        # Handle microtenant_id
        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, payload, params)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return PrivilegedRemoteAccessPortal(response.get_body())

    def update_portal(self, portal_id: str, **kwargs) -> PrivilegedRemoteAccessPortal:
        """
        Updates the specified PRA portal.

        Args:
            portal_id (str): The unique identifier of the portal being updated.

        Returns:
            PrivilegedRemoteAccessPortal: The updated portal object.
        """
        http_method = "put".upper()
        api_url = format_url(f"{self._base_endpoint}/praPortal/{portal_id}")

        # Get the current portal data and update it with new kwargs
        current_portal = self.get_portal(portal_id)
        payload = current_portal.request_format()
        payload.update(kwargs)

        # Handle microtenant_id
        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, payload, params)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return PrivilegedRemoteAccessPortal(response.get_body())

    def delete_portal(self, portal_id: str, **kwargs) -> int:
        """
        Deletes the specified PRA portal.

        Args:
            portal_id (str): The unique identifier of the portal to be deleted.

        Returns:
            int: Status code of the delete operation.
        """
        http_method = "delete".upper()
        api_url = format_url(f"{self._base_endpoint}/praPortal/{portal_id}")

        # Handle microtenant_id
        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, {}, params)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return response.get_status_code()

    def list_consoles(self, query_params=None, keep_empty_params=False) -> tuple:
        """
        Returns a list of all Privileged Remote Access (PRA) consoles.

        Args:
            query_params {dict}: Map of query parameters for the request.
                [query_params.pagesize] {int}: Page size for pagination.
                [query_params.search] {str}: Search string for filtering results.
                [query_params.microtenant_id] {str}: ID of the microtenant, if applicable.
                [query_params.max_items] {int}: Maximum number of items to fetch before stopping.
                [query_params.max_pages] {int}: Maximum number of pages to request before stopping.
            keep_empty_params {bool}: Whether to include empty parameters in the query string.

        Returns:
            list: A list of `PrivilegedRemoteAccessConsole` instances.
        """
        # Initialize URL and HTTP method
        http_method = "get".upper()
        api_url = format_url(f"{self._base_endpoint}/praConsole")

        # Handle query parameters (including microtenant_id if provided)
        query_params = query_params or {}
        microtenant_id = query_params.pop("microtenant_id", None)
        if microtenant_id:
            query_params["microtenantId"] = microtenant_id

        # Build the query string
        if query_params:
            encoded_query_params = urlencode(query_params)
            api_url += f"?{encoded_query_params}"

        # Prepare request body and headers
        body = {}
        headers = {}
        form = {}

        # Create the request
        request, error = self._request_executor.create_request(
            http_method, api_url, body, headers, form, keep_empty_params=keep_empty_params
        )

        if error:
            return (None, None, error)

        # Execute the request
        response, error = self._request_executor.execute(request, PrivilegedRemoteAccessConsole)

        if error:
            return (None, response, error)

        # Parse the response into AppConnectorGroup instances
        try:
            result = []
            for item in response.get_body():
                result.append(PrivilegedRemoteAccessConsole(self.form_response_body(item)))
        except Exception as error:
            return (None, response, error)

        return (result, response, None)

    def get_console(self, console_id: str, **kwargs) -> PrivilegedRemoteAccessConsole:
        """
        Returns information on a specific PRA console.

        Args:
            console_id (str): The unique identifier for the PRA console.

        Returns:
            PrivilegedRemoteAccessConsole: The corresponding console object.
        """
        http_method = "get".upper()
        api_url = format_url(f"{self._base_endpoint}/praConsole/{console_id}")

        # Add microtenant_id to kwargs if provided
        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, {}, params)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return PrivilegedRemoteAccessConsole(response.get_body())

    def add_console(
        self, name: str, pra_application_id: str, pra_portal_ids: list, enabled: bool = True, **kwargs
    ) -> PrivilegedRemoteAccessConsole:
        """
        Adds a new Privileged Remote Access (PRA) console.

        Args:
            name (str): The name of the console.
            pra_application_id (str): The ID of the PRA application.
            pra_portal_ids (list): A list of PRA portal IDs.
            enabled (bool): Whether the console is enabled.

        Keyword Args:
            description (str): The description of the console.

        Returns:
            PrivilegedRemoteAccessConsole: The newly created console.
        """
        http_method = "post".upper()
        api_url = format_url(f"{self._base_endpoint}/praConsole")

        # Build the payload
        payload = {
            "name": name,
            "enabled": enabled,
            "praApplication": {"id": pra_application_id},
            "praPortals": [{"id": portal_id} for portal_id in pra_portal_ids],
        }

        # Add optional params
        for key, value in kwargs.items():
            payload[snake_to_camel(key)] = value

        request, error = self._request_executor.create_request(http_method, api_url, payload)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return PrivilegedRemoteAccessConsole(response.get_body())

    def update_console(
        self, console_id: str, pra_application_id: str = None, pra_portal_ids: list = None, **kwargs
    ) -> PrivilegedRemoteAccessConsole:
        """
        Updates the specified PRA console.

        Args:
            console_id (str): The unique identifier for the console.
            pra_application_id (str, optional): The ID of the PRA application.
            pra_portal_ids (list, optional): List of PRA portal IDs.

        Returns:
            PrivilegedRemoteAccessConsole: The updated console.
        """
        http_method = "put".upper()
        api_url = format_url(f"{self._base_endpoint}/praConsole/{console_id}")

        # Get existing data to merge changes
        console_data = self.get_console(console_id).request_format()

        # Apply updates
        if pra_application_id:
            console_data["praApplication"] = {"id": pra_application_id}
        if pra_portal_ids:
            console_data["praPortals"] = [{"id": id} for id in pra_portal_ids]

        # Add any additional kwargs
        for key, value in kwargs.items():
            console_data[snake_to_camel(key)] = value

        request, error = self._request_executor.create_request(http_method, api_url, console_data)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return PrivilegedRemoteAccessConsole(response.get_body())

    def delete_console(self, console_id: str, **kwargs) -> int:
        """
        Deletes the specified PRA console.

        Args:
            console_id (str): The unique identifier for the console.

        Returns:
            int: The status code of the delete operation.
        """
        http_method = "delete".upper()
        api_url = format_url(f"{self._base_endpoint}/praConsole/{console_id}")

        # Add microtenant_id to params if provided
        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, {}, params)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return response.status_code

    def add_bulk_console(self, consoles: list) -> list:
        """
        Adds multiple Privileged Remote Access (PRA) consoles in bulk.

        Args:
            consoles (list): A list of dictionaries, each containing details for a console.

        Returns:
            list: A list of newly created PRA consoles.
        """
        http_method = "post".upper()
        api_url = format_url(f"{self._base_endpoint}/praConsole/bulk")

        # Build the payload
        payload = [
            {
                "name": console.get("name"),
                "enabled": console.get("enabled", True),
                "praApplication": {"id": console.get("pra_application_id")},
                "praPortals": [{"id": id} for id in console.get("pra_portal_ids", [])],
                "description": console.get("description", ""),
            }
            for console in consoles
        ]

        request, error = self._request_executor.create_request(http_method, api_url, payload)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return [PrivilegedRemoteAccessConsole(console) for console in response.get_body()]

    def list_credentials(self, query_params=None, keep_empty_params=False) -> tuple:
        """
        Returns a list of all privileged remote access credentials.

        Args:
            query_params {dict}: Map of query parameters for the request.
                [query_params.pagesize] {int}: Page size for pagination.
                [query_params.search] {str}: Search string for filtering results.
                [query_params.microtenant_id] {str}: ID of the microtenant, if applicable.
                [query_params.max_items] {int}: Maximum number of items to fetch before stopping.
                [query_params.max_pages] {int}: Maximum number of pages to request before stopping.
            keep_empty_params {bool}: Whether to include empty parameters in the query string.

        Returns:
            tuple: A tuple containing (list of PrivilegedRemoteAccessCredential instances, Response, error)
        """
        http_method = "get".upper()
        api_url = format_url(f"{self._base_endpoint}/credential")

        # Handle query parameters (including microtenant_id if provided)
        query_params = query_params or {}
        microtenant_id = query_params.pop("microtenant_id", None)
        if microtenant_id:
            query_params["microtenantId"] = microtenant_id

        # Build the query string
        if query_params:
            encoded_query_params = urlencode(query_params)
            api_url += f"?{encoded_query_params}"

        # Prepare request body and headers
        body = {}
        headers = {}
        form = {}

        # Create the request
        request, error = self._request_executor.create_request(
            http_method, api_url, body, headers, form, keep_empty_params=keep_empty_params
        )

        if error:
            return (None, None, error)

        # Execute the request
        response, error = self._request_executor.execute(request, PrivilegedRemoteAccessCredential)

        if error:
            return (None, response, error)

        # Parse the response into AppConnectorGroup instances
        try:
            result = []
            for item in response.get_body():
                result.append(PrivilegedRemoteAccessCredential(self.form_response_body(item)))
        except Exception as error:
            return (None, response, error)

        return (result, response, None)

    def get_credential(self, credential_id: str, **kwargs) -> PrivilegedRemoteAccessCredential:
        """
        Returns information on the specified privileged remote access credential.

        Args:
            credential_id (str): The unique identifier of the credential.

        Returns:
            PrivilegedRemoteAccessCredential: The resource record for the credential.
        """
        http_method = "get".upper()
        api_url = format_url(f"{self._base_endpoint}/credential/{credential_id}")

        request, error = self._request_executor.create_request(http_method, api_url, params=kwargs)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return PrivilegedRemoteAccessCredential(response.get_body())

    def add_credential(
        self,
        name: str,
        credential_type: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        private_key: Optional[str] = None,
        **kwargs,
    ) -> PrivilegedRemoteAccessCredential:
        """
        Adds a new privileged remote access credential.

        Args:
            name (str): The name of the credential.
            credential_type (str): The type of credential ('USERNAME_PASSWORD', 'SSH_KEY', 'PASSWORD').
            username (str, optional): The username for 'USERNAME_PASSWORD' or 'SSH_KEY' types.
            password (str, optional): The password for 'USERNAME_PASSWORD' or 'PASSWORD' types.
            private_key (str, optional): The private key for 'SSH_KEY' type.

        Returns:
            PrivilegedRemoteAccessCredential: The newly created credential resource.
        """
        payload = {"name": name, "credentialType": credential_type}

        if credential_type == "USERNAME_PASSWORD":
            if not username or not password:
                raise ValueError("Username and password must be provided for USERNAME_PASSWORD type.")
            payload.update({"userName": username, "password": password})

        elif credential_type == "SSH_KEY":
            if not username or not private_key:
                raise ValueError("Username and private_key must be provided for SSH_KEY type.")
            if not is_valid_ssh_key(private_key):
                raise ValueError("Invalid SSH key format.")
            payload.update({"userName": username, "privateKey": private_key})

        elif credential_type == "PASSWORD":
            if not password:
                raise ValueError("Password must be provided for PASSWORD type.")
            payload["password"] = password

        # Add optional parameters to payload
        for key, value in kwargs.items():
            payload[snake_to_camel(key)] = value

        request, error = self._request_executor.create_request("POST", f"{self._base_endpoint}/credential", json=payload)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return PrivilegedRemoteAccessCredential(response.get_body())

    def update_credential(self, credential_id: str, **kwargs) -> PrivilegedRemoteAccessCredential:
        """
        Updates a specified credential based on provided keyword arguments.

        Args:
            credential_id (str): The unique identifier for the credential being updated.

        Returns:
            PrivilegedRemoteAccessCredential: The updated credential resource.
        """
        existing_credential = self.get_credential(credential_id)
        if not existing_credential:
            raise Exception(f"Failed to fetch credential {credential_id}")

        payload = existing_credential.request_format()

        # Update payload with any additional keyword arguments
        for key, value in kwargs.items():
            payload[snake_to_camel(key)] = value

        request, error = self._request_executor.create_request(
            "PUT", f"{self._base_endpoint}/credential/{credential_id}", json=payload
        )
        if error:
            return None

        _, error = self._request_executor.execute(request)  # We do not need the response here, just executing
        if error:
            return None

        return self.get_credential(credential_id)  # Fetch and return the updated credential

    def delete_credential(self, credential_id: str) -> int:
        """
        Deletes the specified privileged remote access credential.

        Args:
            credential_id (str): The unique identifier of the credential to delete.

        Returns:
            int: The HTTP status code of the delete operation.
        """
        request, error = self._request_executor.create_request("DELETE", f"{self._base_endpoint}/credential/{credential_id}")
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return response.get_status_code()

    def credential_move(self, credential_id: str, **kwargs) -> dict:
        """
        Moves privileged remote access credentials between parent tenant and microtenants.

        Args:
            credential_id (str): The unique identifier of the credential.
            target_microtenant_id (str): The unique identifier of the target microtenant.

        Returns:
            dict: Empty dictionary if the move operation is successful.
        """
        payload = {"targetMicrotenantId": kwargs.pop("target_microtenant_id", None)}

        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(
            "POST", f"{self._base_endpoint}/credential/{credential_id}/move", json=payload, params=params
        )
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error or response.get_status_code() != 204:
            return None  # No exception message, only returning None based on Okta-style pattern

        return {}

    def list_approval(self, query_params=None, keep_empty_params=False) -> tuple:
        """
        Returns a list of all privileged remote access approvals.

        Args:
            query_params {dict}: Map of query parameters for the request.
                [query_params.pagesize] {int}: Page size for pagination.
                [query_params.search] {str}: Search string for filtering results.
                [query_params.microtenant_id] {str}: ID of the microtenant, if applicable.
                [query_params.max_items] {int}: Maximum number of items to fetch before stopping.
                [query_params.max_pages] {int}: Maximum number of pages to request before stopping.
            keep_empty_params {bool}: Whether to include empty parameters in the query string.

        Returns:
            tuple: A tuple containing (list of PrivilegedRemoteAccessApproval instances, Response, error)
        """
        http_method = "get".upper()
        api_url = format_url(f"{self._base_endpoint}/approval")

        # Handle query parameters (including microtenant_id if provided)
        query_params = query_params or {}
        microtenant_id = query_params.pop("microtenant_id", None)
        if microtenant_id:
            query_params["microtenantId"] = microtenant_id

        # Build the query string
        if query_params:
            encoded_query_params = urlencode(query_params)
            api_url += f"?{encoded_query_params}"

        # Prepare request body and headers
        body = {}
        headers = {}
        form = {}

        # Create the request
        request, error = self._request_executor.create_request(
            http_method, api_url, body, headers, form, keep_empty_params=keep_empty_params
        )

        if error:
            return (None, None, error)

        # Execute the request
        response, error = self._request_executor.execute(request, PrivilegedRemoteAccessApproval)

        if error:
            return (None, response, error)

        # Parse the response into AppConnectorGroup instances
        try:
            result = []
            for item in response.get_body():
                result.append(PrivilegedRemoteAccessApproval(self.form_response_body(item)))
        except Exception as error:
            return (None, response, error)

        return (result, response, None)

    def get_approval(self, approval_id: str) -> PrivilegedRemoteAccessApproval:
        """
        Returns information on the specified pra approval.

        Args:
            approval_id (str): The unique identifier for the pra approval.

        Returns:
            PrivilegedRemoteAccessApproval: The resource record for the PRA approval.
        """
        api_url = format_url(f"{self._base_endpoint}/approval/{approval_id}")
        request, error = self._request_executor.create_request("GET", api_url)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return PrivilegedRemoteAccessApproval(response.get_body())

    def add_approval(
        self,
        email_ids: list,
        application_ids: list,
        start_time: str,
        end_time: str,
        status: str,
        working_hours: dict,
        **kwargs,
    ) -> PrivilegedRemoteAccessApproval:
        """
        Adds a privileged remote access approval.

        Args:
            email_ids (list): Email addresses of the users for the approval.
            application_ids (list): List of associated application segment ids.
            start_time (str): Start timestamp in UNIX format.
            end_time (str): End timestamp in UNIX format.
            status (str): Status of the approval. Supported: INVALID, ACTIVE, FUTURE, EXPIRED.
            working_hours (dict): Working hours configuration.

        Returns:
            PrivilegedRemoteAccessApproval: The newly created PRA approval.
        """
        start_epoch, end_epoch = validate_and_convert_times(start_time, end_time, working_hours["time_zone"])

        payload = {
            "emailIds": email_ids,
            "applications": [{"id": app_id} for app_id in application_ids],
            "startTime": start_epoch,
            "endTime": end_epoch,
            "status": status,
            "workingHours": {
                "startTimeCron": working_hours["start_time_cron"],
                "endTimeCron": working_hours["end_time_cron"],
                "startTime": working_hours["start_time"],
                "endTime": working_hours["end_time"],
                "days": working_hours["days"],
                "timeZone": working_hours["time_zone"],
            },
        }

        # Add optional parameters
        for key, value in kwargs.items():
            payload[snake_to_camel(key)] = value

        api_url = format_url(f"{self._base_endpoint}/approval")
        request, error = self._request_executor.create_request("POST", api_url, json=payload)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return PrivilegedRemoteAccessApproval(response.get_body())

    def update_approval(self, approval_id: str, **kwargs) -> PrivilegedRemoteAccessApproval:
        """
        Updates a specified approval based on provided keyword arguments.

        Args:
            approval_id (str): The unique identifier for the approval being updated.

        Returns:
            PrivilegedRemoteAccessApproval: The updated approval resource.
        """
        existing_approval = self.get_approval(approval_id)
        if not existing_approval:
            raise Exception(f"Failed to fetch approval {approval_id}")

        payload = existing_approval.request_format()

        # Pre-process and validate start_time and end_time if provided
        if "start_time" in kwargs and "end_time" in kwargs:
            start_time = kwargs.pop("start_time")
            end_time = kwargs.pop("end_time")
            time_zone = kwargs.get("working_hours", {}).get("time_zone", existing_approval.working_hours.time_zone)
            start_epoch, end_epoch = validate_and_convert_times(start_time, end_time, time_zone)
            kwargs["start_time"] = start_epoch
            kwargs["end_time"] = end_epoch

        # Update payload with additional keyword arguments
        for key, value in kwargs.items():
            payload[snake_to_camel(key)] = value

        api_url = format_url(f"{self._base_endpoint}/approval/{approval_id}")
        request, error = self._request_executor.create_request("PUT", api_url, json=payload)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error or response.get_status_code() != 204:
            return None

        return self.get_approval(approval_id)

    def delete_approval(self, approval_id: str) -> int:
        """
        Deletes a specified privileged remote access approval.

        Args:
            approval_id (str): The unique identifier for the approval to be deleted.

        Returns:
            int: Status code of the delete operation.
        """
        api_url = format_url(f"{self._base_endpoint}/approval/{approval_id}")
        request, error = self._request_executor.create_request("DELETE", api_url)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return response.get_status_code()

    def expired_approval(self) -> int:
        """
        Deletes all expired privileged approvals.

        Returns:
            int: Status code of the delete operation.
        """
        api_url = format_url(f"{self._base_endpoint}/approval/expired")
        request, error = self._request_executor.create_request("DELETE", api_url)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return response.get_status_code()
