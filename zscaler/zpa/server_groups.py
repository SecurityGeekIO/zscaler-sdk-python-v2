"""
Copyright (c) 2023, Zscaler Inc.

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
"""

from zscaler.api_client import APIClient
from zscaler.zpa.models.server_group import ServerGroup
from zscaler.utils import format_url, snake_to_camel, add_id_groups
from urllib.parse import urlencode


class ServerGroupsAPI(APIClient):
    """
    A client object for the Server Groups resource.
    """

    def __init__(self, request_executor, config):
        super().__init__()
        self._request_executor = request_executor
        customer_id = config["client"].get("customerId")
        self._base_endpoint = f"/zpa/mgmtconfig/v1/admin/customers/{customer_id}"

    def list_server_groups(self, query_params=None, keep_empty_params=False) -> tuple:
        """
        Enumerates server groups in your organization with pagination.
        A subset of server groups can be returned that match a supported
        filter expression or query.

        Args:
            query_params {dict}: Map of query parameters for the request.
                [query_params.pagesize] {int}: Page size for pagination.
                [query_params.search] {str}: Search string for filtering results.
                [query_params.microtenant_id] {str}: ID of the microtenant, if applicable.
                [query_params.max_items] {int}: Maximum number of items to fetch before stopping.
                [query_params.max_pages] {int}: Maximum number of pages to request before stopping.
            keep_empty_params {bool}: Whether to include empty parameters in the query string.

        Returns:
            tuple: A tuple containing (list of ServerGroups instances, Response, error)

        Examples:
            >>> server_groups = zpa.server_groups.list_groups(search="example")
        """
        http_method = "get".upper()
        api_url = format_url(f"{self._base_endpoint}/serverGroup")

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
        response, error = self._request_executor.execute(request, ServerGroup)

        if error:
            return (None, response, error)

        # Parse the response into AppConnectorGroup instances
        try:
            result = []
            for item in response.get_body():
                result.append(ServerGroup(self.form_response_body(item)))
        except Exception as error:
            return (None, response, error)

        return (result, response, None)

    def get_group(self, group_id: str, **kwargs) -> tuple:
        """
        Provides information on the specified server group.

        Args:
            group_id (str): The unique id for the server group.

        Returns:
            tuple: A tuple containing (ServerGroup, Response, error)
        """
        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._base_endpoint}
            /serverGroup/{group_id}
            """
        )

        # Optional parameters such as microtenant_id
        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, params=params)
        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request)
        if error:
            return (None, response, error)

        result = ServerGroup(response.get_body())
        return (result, response, None)

    def get_server_group_by_name(self, name: str, **kwargs) -> tuple:
        """
        Returns information on the server group with the specified name.

        Args:
            name (str): The name of the server group.

        Returns:
            tuple: A tuple containing (ServerGroup, Response, error)
        """
        groups, response, error = self.list_server_groups(**kwargs)
        if error:
            return (None, response, error)

        for group in groups:
            if group.name == name:
                return (group, response, None)

        return (None, response, None)

    def add_group(self, app_connector_group_ids: list, name: str, **kwargs) -> tuple:
        """
        Adds a server group.

        Args:
            name (str): The name for the server group.
            app_connector_group_ids (list of str): A list of application connector IDs that will be attached to the server group.

        Returns:
            tuple: A tuple containing (ServerGroup, Response, error)
        """
        http_method = "post".upper()
        api_url = format_url(
            f"""
            {self._base_endpoint}
            /serverGroup
        """
        )

        payload = {
            "name": name,
            "appConnectorGroups": [{"id": group_id} for group_id in app_connector_group_ids],
        }

        add_id_groups(self.reformat_params, kwargs, payload)

        for key, value in kwargs.items():
            payload[snake_to_camel(key)] = value

        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, json=payload, params=params)
        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request)
        if error:
            return (None, response, error)

        result = ServerGroup(response.get_body())
        return (result, response, None)

    def update_group(self, group_id: str, **kwargs) -> tuple:
        """
        Updates a server group.

        Args:
            group_id (str): The unique identifier for the server group.

        Returns:
            tuple: A tuple containing (ServerGroup, Response, error)
        """
        http_method = "put".upper()
        api_url = format_url(
            f"""
            {self._base_endpoint}
            /serverGroup/{group_id}
        """
        )

        existing_group, _, error = self.get_group(group_id, **kwargs)
        if error:
            return (None, None, error)

        payload = {snake_to_camel(k): v for k, v in existing_group.request_format().items()}

        add_id_groups(self.reformat_params, kwargs, payload)

        for key, value in kwargs.items():
            payload[snake_to_camel(key)] = value

        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, json=payload, params=params)
        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request)
        if error:
            return (None, response, error)

        result = ServerGroup(response.get_body())
        return (result, response, None)

    def delete_group(self, group_id: str, **kwargs) -> tuple:
        """
        Deletes the specified server group.

        Args:
            group_id (str): The unique id for the server group to be deleted.

        Returns:
            tuple: A tuple containing (None, Response, error)
        """
        http_method = "delete".upper()
        api_url = format_url(
            f"""
            {self._base_endpoint}
            /serverGroup/{group_id}
        """
        )

        params = {}
        if "microtenant_id" in kwargs:
            params["microtenantId"] = kwargs.pop("microtenant_id")

        request, error = self._request_executor.create_request(http_method, api_url, params=params)
        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request)
        if error:
            return (None, response, error)

        return (None, response, None)
