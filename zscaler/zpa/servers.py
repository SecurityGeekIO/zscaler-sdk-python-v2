from . import ZPAClient
from requests import Response
from box import Box, BoxList
from zscaler.utils import (
    snake_to_camel,
)

class AppServersService:
    def __init__(self, client: ZPAClient):
        self.rest = client
        self.customer_id = client.customer_id

    def add_server(self, name: str, address: str, enabled: bool = True, **kwargs) -> Box:
        """
        Add a new application server.

        Args:
            name (str):
                The name of the server.
            address (str):
                The IP address of the server.
            enabled (bool):
                 Enable the server. Defaults to True.
            **kwargs:
                Optional keyword args.

        Keyword Args:
            description (str):
                A description for the server.
            app_server_group_ids (list):
                Unique identifiers for the server groups the server belongs to.
            config_space (str):
                The configuration space for the server. Defaults to DEFAULT.

        Returns:
            :obj:`Box`: The resource record for the newly created server.

        Examples:
            Create a server with the minimum required parameters:

            >>> zpa.servers.add_server(
            ...   name='myserver.example',
            ...   address='192.0.2.10',
            ...   enabled=True)

        """
        payload = {"name": name, "address": address, "enabled": enabled}

        # Add optional parameters to payload
        for key, value in kwargs.items():
            payload[snake_to_camel(key)] = value

        return self._post("server", json=payload)

    def list_servers(self, **kwargs) -> BoxList:
        """
        Returns all configured servers.

        Keyword Args:
            **max_items (int):
                The maximum number of items to request before stopping iteration.
            **max_pages (int):
                The maximum number of pages to request before stopping iteration.
            **pagesize (int):
                Specifies the page size. The default size is 20, but the maximum size is 500.
            **search (str, optional):
                The search string used to match against features and fields.

        Returns:
            :obj:`BoxList`: List of all configured servers.

        Examples:
            >>> servers = zpa.servers.list_servers()
        """
        list, _ = self.rest.get_paginated_data(
            base_url="/mgmtconfig/v1/admin/customers/%s/server" % (self.customer_id),
            data_key_name="list",
        )
        return list

    def get_server(self, server_id: str) -> Box:
        """
        Gets information on the specified server.

        Args:
            server_id (str):
                The unique identifier for the server.

        Returns:
            :obj:`Box`: The resource record for the server.

        Examples:
            >>> server = zpa.servers.get_server('99999')

        """
        response = self.rest.get("/mgmtconfig/v1/admin/customers/%s/server/%s" % (self.customer_id, server_id))
        if isinstance(response, Response):
            status_code = response.status_code
            if status_code != 200:
                return None
        return response

    def get_server_by_name(self, name):
        apps = self.list_servers()
        for app in apps:
            if app.get("name") == name:
                return app
        return None

    def delete_server(self, server_id: str) -> int:
        """
        Delete the specified server.

        The server must not be assigned to any Server Groups or the operation will fail.

        Args:
            server_id (str): The unique identifier for the server to be deleted.

        Returns:
            :obj:`int`: The response code for the operation.

        Examples:
            >>> zpa.servers.delete_server('99999')

        """
        response = self.rest.delete("/mgmtconfig/v1/admin/customers/%s/server/%s?%s" % (self.customer_id, server_id))
        return response.status_code

    def update_server(self, server_id: str, **kwargs) -> Box:
        """
        Updates the specified server.

        Args:
            server_id (str):
                The unique identifier for the server being updated.
            **kwargs:
                Optional keyword args.

        Keyword Args:
            name (str):
                The name of the server.
            address (str):
                The IP address of the server.
            enabled (bool):
                 Enable the server.
            description (str):
                A description for the server.
            app_server_group_ids (list):
                Unique identifiers for the server groups the server belongs to.
            config_space (str):
                The configuration space for the server.

        Returns:
            :obj:`Box`: The resource record for the updated server.

        Examples:
            Update the name of a server:

            >>> zpa.servers.update_server(
            ...   '99999',
            ...   name='newname.example')

            Update the address and enable a server:

            >>> zpa.servers.update_server(
            ...    '99999',
            ...    address='192.0.2.20',
            ...    enabled=True)

        """
        # Set payload to value of existing record
        payload = {snake_to_camel(k): v for k, v in self.get_server(server_id).items()}

        # Add optional parameters to payload
        for key, value in kwargs.items():
            payload[snake_to_camel(key)] = value

        response = self.rest.put(
            "/mgmtconfig/v1/admin/customers/%s/server/%s" % (self.customer_id, server_id),
            data=payload,
        )
        if isinstance(response, Response):
            status_code = response.status_code
            if status_code > 299:
                return None
        return self.get_servers(server_id)
