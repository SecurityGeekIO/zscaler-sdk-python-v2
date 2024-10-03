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

from zscaler.zpa.models.application_servers import AppServers
from zscaler.api_client import APIClient
from zscaler.utils import format_url
from zscaler.api_response import get_paginated_data
from urllib.parse import urlencode


class AppServersAPI(APIClient):

    def __init__(self):
        self._base_url = ""

    def list_servers(self, **kwargs) -> list:
        """
        Returns all configured servers with pagination support.

        Args:
            **kwargs: Optional keyword arguments to be passed to the pagination handler, such as:
                - search: The search string used to match against features and fields.
                - search_field: The field to be searched (default is "name").
                - max_items: Maximum number of items to return.
                - max_pages: Maximum number of pages to return.
                - pagesize: Number of items per page (default is 20, maximum is 500).
                - sort_order: The order in which to sort (e.g., ASC or DESC).
                - sort_by: The field by which to sort the results.
                - microtenant_id: ID of the microtenant, if applicable.

        Returns:
            list: A list of `AppServers` instances.

        Example:
            >>> servers = zpa.servers.list_servers(search="Example 100", pagesize=100, microtenant_id="216199618143464722")
        """
        # Construct the API URL with the base URL and the servers endpoint
        api_url = format_url(
            f"""
            {self._base_url}
            /server
        """
        )

        # Add microtenant_id to kwargs if provided
        microtenant_id = kwargs.pop("microtenant_id", None)
        if microtenant_id:
            kwargs["microtenantId"] = microtenant_id

        # Ensure the query params are properly encoded
        if kwargs:
            encoded_query_params = urlencode(kwargs)
            api_url += f"?{encoded_query_params}"

        # Call get_paginated_data to fetch the paginated server data
        list_data, error = get_paginated_data(request_executor=self.rest, path=api_url, **kwargs)

        if error:
            raise Exception(f"Error fetching server data: {error}")

        # Convert the raw server data into AppServers objects
        return [AppServers(server) for server in list_data]

    def get_server(self, server_id: str, **kwargs) -> AppServers:
        """
        Gets information on the specified server.

        Args:
            server_id (str): The unique identifier of the server.

        Returns:
            AppServers: The corresponding server object.
        """
        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._base_url}
            /server/{server_id}
            """
        )

        # Add microtenant_id to kwargs if provided
        microtenant_id = kwargs.pop("microtenant_id", None)
        if microtenant_id:
            kwargs["microtenantId"] = microtenant_id

        request, error = self._request_executor.create_request(http_method, api_url, {}, kwargs)
        if error:
            raise Exception(f"Failed to create request: {error}")

        response, error = self._request_executor.execute(request, AppServers)
        if error:
            raise Exception(f"API request failed: {error}")

        return AppServers(response.get_body())

    def add_server(self, name: str, address: str, enabled: bool = True, **kwargs) -> AppServers:
        """
        Add a new application server.

        Args:
            name (str): The name of the server.
            address (str): The IP address of the server.
            enabled (bool): Enable the server. Defaults to True.
        """
        http_method = "post".upper()
        api_url = format_url(
            f"""
            {self._base_url}
            /server
        """
        )

        payload = {
            "name": name,
            "address": address,
            "enabled": enabled,
        }
        payload.update(kwargs)

        # Add microtenant_id to kwargs if provided
        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, payload, params)
        if error:
            raise Exception(f"Failed to create request: {error}")

        response, error = self._request_executor.execute(request, AppServers)
        if error:
            raise Exception(f"API request failed: {error}")

        return AppServers(response.get_body())

    def update_server(self, server_id: str, **kwargs) -> AppServers:
        """
        Updates the specified server.

        Args:
            server_id (str): The unique identifier for the server being updated.
        """
        http_method = "put".upper()
        api_url = format_url(
            f"""
            {self._base_url}
            /server/{server_id}
        """
        )

        # Get the current server data and update it with the new kwargs
        server_data = self.get_server(server_id).request_format()
        server_data.update(kwargs)

        # Add microtenant_id to kwargs if provided
        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, server_data, params)
        if error:
            raise Exception(f"Failed to create request: {error}")

        response, error = self._request_executor.execute(request, AppServers)
        if error:
            raise Exception(f"API request failed: {error}")

        return AppServers(response.get_body())

    def delete_server(self, server_id: str, **kwargs) -> int:
        """
        Delete the specified server.

        Args:
            server_id (str): The unique identifier for the server to be deleted.

        Returns:
            int: Status code of the delete operation.
        """
        http_method = "delete".upper()
        api_url = format_url(
            f"""
            {self._base_url}
            /server/{server_id}
        """
        )

        # Add microtenant_id to kwargs if provided
        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, {}, params)
        if error:
            raise Exception(f"Failed to create request: {error}")

        response, error = self._request_executor.execute(request)
        if error:
            raise Exception(f"API request failed: {error}")

        return response.status_code


# from box import Box, BoxList
# from requests import Response

# from zscaler.utils import snake_to_camel
# from zscaler.api_client import APIClient


# class AppServersAPI(APIClient):
#     # def __init__(self, client: ZPAClient):
#     #     self.rest = client

#     def list_servers(self, **kwargs) -> BoxList:
#         """
#         Returns all configured servers.

#         Keyword Args:
#             **max_items (int):
#                 The maximum number of items to request before stopping iteration.
#             **max_pages (int):
#                 The maximum number of pages to request before stopping iteration.
#             **pagesize (int):
#                 Specifies the page size. The default size is 20, but the maximum size is 500.
#             **search (str, optional):
#                 The search string used to match against features and fields.

#         Returns:
#             :obj:`BoxList`: List of all configured servers.

#         Examples:
#             >>> servers = zpa.servers.list_servers()
#         """
#         list, _ = self.rest.get_paginated_data(path="/server", **kwargs, api_version="v1")
#         return list

#     def get_server(self, server_id: str, **kwargs) -> Box:
#         """
#         Gets information on the specified server.

#         Args:
#             server_id (str):
#                 The unique identifier for the server.

#         Returns:
#             :obj:`Box`: The resource record for the server.

#         Examples:
#             >>> server = zpa.servers.get_server('99999')

#         """
#         params = {}
#         if "microtenant_id" in kwargs:
#             params["microtenantId"] = kwargs.pop("microtenant_id")
#         return self.rest.get(f"server/{server_id}", params=params)

#     def get_server_by_name(self, name, **kwargs):
#         """
#         Returns information on the application server with the specified name.

#         Args:
#             name (str): The name of the application server.

#         Returns:
#             :obj:`Box` or None: The resource record for the application server if found, otherwise None.

#         Examples:
#             >>> app_server = zpa.servers.get_server_by_name('example_name')
#             >>> if app_server:
#             ...     pprint(app_server)
#             ... else:
#             ...     print("Application server not found")
#         """
#         servers = self.list_servers(**kwargs)
#         for server in servers:
#             if server.get("name") == name:
#                 return server
#         return None

#     def add_server(self, name: str, address: str, enabled: bool = True, **kwargs) -> Box:
#         """
#         Add a new application server.

#         Args:
#             name (str):
#                 The name of the server.
#             address (str):
#                 The IP address of the server.
#             enabled (bool):
#                  Enable the server. Defaults to True.
#             **kwargs:
#                 Optional keyword args.

#         Keyword Args:
#             description (str):
#                 A description for the server.
#             app_server_group_ids (list):
#                 Unique identifiers for the server groups the server belongs to.
#             config_space (str):
#                 The configuration space for the server. Defaults to DEFAULT.

#         Returns:
#             :obj:`Box`: The resource record for the newly created server.

#         Examples:
#             Create a server with the minimum required parameters:

#             >>> zpa.servers.add_server(
#             ...   name='myserver.example',
#             ...   address='192.0.2.10',
#             ...   enabled=True)

#         """
#         payload = {"name": name, "address": address, "enabled": enabled}

#         # Add optional parameters to payload
#         for key, value in kwargs.items():
#             payload[snake_to_camel(key)] = value

#         microtenant_id = kwargs.pop("microtenant_id", None)
#         params = {"microtenantId": microtenant_id} if microtenant_id else {}

#         response = self.rest.post("server", json=payload, params=params)
#         if isinstance(response, Response):
#             status_code = response.status_code
#             # Handle error response
#             raise Exception(f"API call failed with status {status_code}: {response.json()}")
#         return response

#     def update_server(self, server_id: str, **kwargs) -> Box:
#         """
#         Updates the specified server.

#         Args:
#             server_id (str):
#                 The unique identifier for the server being updated.
#             **kwargs:
#                 Optional keyword args.

#         Keyword Args:
#             name (str):
#                 The name of the server.
#             address (str):
#                 The IP address of the server.
#             enabled (bool):
#                  Enable the server.
#             description (str):
#                 A description for the server.
#             app_server_group_ids (list):
#                 Unique identifiers for the server groups the server belongs to.
#             config_space (str):
#                 The configuration space for the server.

#         Returns:
#             :obj:`Box`: The resource record for the updated server.

#         Examples:
#             Update the name of a server:

#             >>> zpa.servers.update_server(
#             ...   '99999',
#             ...   name='newname.example')

#             Update the address and enable a server:

#             >>> zpa.servers.update_server(
#             ...    '99999',
#             ...    address='192.0.2.20',
#             ...    enabled=True)

#         """
#         payload = {snake_to_camel(k): v for k, v in self.get_server(server_id).items()}

#         for key, value in kwargs.items():
#             payload[snake_to_camel(key)] = value

#         microtenant_id = kwargs.pop("microtenant_id", None)
#         params = {"microtenantId": microtenant_id} if microtenant_id else {}

#         resp = self.rest.put(f"server/{server_id}", json=payload, params=params).status_code
#         if not isinstance(resp, Response):
#             return self.get_server(server_id)

#     def delete_server(self, server_id: str, **kwargs) -> int:
#         """
#         Delete the specified server.

#         The server must not be assigned to any Server Groups or the operation will fail.

#         Args:
#             server_id (str): The unique identifier for the server to be deleted.

#         Returns:
#             :obj:`int`: The response code for the operation.

#         Examples:
#             >>> zpa.servers.delete_server('99999')

#         """
#         params = {}
#         if "microtenant_id" in kwargs:
#             params["microtenantId"] = kwargs.pop("microtenant_id")
#         return self.rest.delete(f"server/{server_id}", params=params).status_code
