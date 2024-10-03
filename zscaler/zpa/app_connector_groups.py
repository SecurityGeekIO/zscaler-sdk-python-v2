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
from zscaler.zpa.models.app_connector_groups import AppConnectorGroup
from zscaler.api_response import get_paginated_data
from zscaler.utils import format_url, add_id_groups, pick_version_profile, snake_to_camel


class AppConnectorGroupAPI(APIClient):
    """
    A Client object for the App Connector Groups resource.
    """

    reformat_params = [
        ("connector_ids", "connectors"),
        ("server_group_ids", "serverGroups"),
    ]

    def __init__(self):
        super().__init__()
        self._base_url = ""

    def list_connector_groups(self, **kwargs) -> tuple:
        """
        Returns a list of all connector groups.

        Keyword Args:
            max_items (int, optional): The maximum number of items to request before stopping iteration.
            max_pages (int, optional): The maximum number of pages to request before stopping iteration.
            pagesize (int, optional): Specifies the page size. The default size is 100, but the maximum size is 1000.
            search (str, optional): The search string used to match against a department's name or comments attributes.
            keep_empty_params (bool): Whether to include empty parameters in the query string.
            microtenant_id (str, optional): ID of the microtenant, if applicable.

        Returns:
            tuple: A tuple containing (list of AppConnectorGroup instances, Response, error)
        """
        api_url = format_url(f"{self._base_url}/appConnectorGroup")

        # Extract microtenant_id from kwargs and add to params if provided
        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        # Fetch paginated data using the request_executor
        list_data, response, error = get_paginated_data(
            request_executor=self._request_executor, path=api_url, params=params, **kwargs
        )

        if error:
            return (None, response, error)

        # Convert the raw data into AppConnectorGroup instances
        result = [AppConnectorGroup(group) for group in list_data]
        return (result, response, None)

    def get_connector_group(self, group_id: str, **kwargs) -> tuple:
        """
        Gets information for a specified connector group.

        Args:
            group_id (str): The unique identifier for the connector group.

        Returns:
            tuple: A tuple containing (AppConnectorGroup, Response, error)
        """
        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._base_url}/appConnectorGroup/{group_id}
            """
        )

        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, params=params)
        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request)
        if error:
            return (None, response, error)

        result = AppConnectorGroup(response.get_body())
        return (result, response, None)

    def get_connector_group_by_name(self, name: str, **kwargs) -> tuple:
        """
        Returns information on the app connector group with the specified name.

        Args:
            name (str): The name of the app connector group.

        Returns:
            tuple: A tuple containing (AppConnectorGroup, Response, error)
        """
        groups, response, error = self.list_connector_groups(**kwargs)
        if error:
            return (None, response, error)

        for group in groups:
            if group.name == name:
                return (group, response, None)

        return (None, response, None)

    def add_connector_group(self, name: str, latitude: int, location: str, longitude: int, **kwargs) -> tuple:
        """
        Adds a new ZPA App Connector Group.

        Args:
            name (str): The name of the App Connector Group.
            latitude (int): The latitude representing the App Connector's physical location.
            location (str): The name of the location that the App Connector Group represents.
            longitude (int): The longitude representing the App Connector's physical location.
            **kwargs: Optional keyword args.

        Keyword Args:
            **connector_ids (list):
                The unique ids for the App Connectors that will be added to this App Connector Group.
            **city_country (str):
                The City and Country for where the App Connectors are located. Format is:

                ``<City>, <Country Code>`` e.g. ``Sydney, AU``
            **country_code (str):
                The ISO<std> Country Code that represents the country where the App Connectors are located.
            **description (str):
                Additional information about the App Connector Group.
            **dns_query_type (str):
                The type of DNS queries that are enabled for this App Connector Group. Accepted values are:
                ``IPV4_IPV6``, ``IPV4`` and ``IPV6``
            **enabled (bool):
                Is the App Connector Group enabled? Defaults to ``True``.
            **override_version_profile (bool):
                Override the local App Connector version according to ``version_profile``. Defaults to ``False``.
            **server_group_ids (list):
                The unique ids of the Server Groups that are associated with this App Connector Group
            **lss_app_connector_group (bool):
            **upgrade_day (str):
                The day of the week that upgrades will be pushed to the App Connector.
            **upgrade_time_in_secs (str):
                The time of the day that upgrades will be pushed to the App Connector.
            **version_profile (str):
                The version profile to use. This will automatically set ``override_version_profile`` to True.
                Accepted values are:
                ``default``, ``previous_default`` and ``new_release``

        Returns:
            tuple: A tuple containing (AppConnectorGroup, Response, error)
        """
        http_method = "post".upper()
        api_url = format_url(
            f"""
            {self._base_url}/appConnectorGroup
            """
        )

        payload = {
            "name": name,
            "latitude": latitude,
            "location": location,
            "longitude": longitude,
        }

        add_id_groups(self.reformat_params, kwargs, payload)
        pick_version_profile(kwargs, payload)

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

        result = AppConnectorGroup(response.get_body())
        return (result, response, None)

    def update_connector_group(self, group_id: str, **kwargs) -> tuple:
        """
        Updates an existing ZPA App Connector Group.

        Args:
            group_id (str): The unique id for the App Connector Group in ZPA.
            **kwargs: Optional keyword args.

        Keyword Args:
            **connector_ids (list):
                The unique ids for the App Connectors that will be added to this App Connector Group.
            **city_country (str):
                The City and Country for where the App Connectors are located. Format is:

                ``<City>, <Country Code>`` e.g. ``Sydney, AU``
            **country_code (str):
                The ISO<std> Country Code that represents the country where the App Connectors are located.
            **description (str):
                Additional information about the App Connector Group.
            **dns_query_type (str):
                The type of DNS queries that are enabled for this App Connector Group. Accepted values are:
                ``IPV4_IPV6``, ``IPV4`` and ``IPV6``
            **enabled (bool):
                Is the App Connector Group enabled? Defaults to ``True``.
            **name (str): The name of the App Connector Group.
            **latitude (int): The latitude representing the App Connector's physical location.
            **location (str): The name of the location that the App Connector Group represents.
            **longitude (int): The longitude representing the App Connector's physical location.
            **override_version_profile (bool):
                Override the local App Connector version according to ``version_profile``. Defaults to ``False``.
            **server_group_ids (list):
                The unique ids of the Server Groups that are associated with this App Connector Group
            **lss_app_connector_group (bool):
            **upgrade_day (str):
                The day of the week that upgrades will be pushed to the App Connector.
            **upgrade_time_in_secs (str):
                The time of the day that upgrades will be pushed to the App Connector.
            **version_profile (str):
                The version profile to use. This will automatically set ``override_version_profile`` to True.
                Accepted values are:

                ``default``, ``previous_default`` and ``new_release``

        Returns:
            tuple: A tuple containing (AppConnectorGroup, Response, error)
        """
        http_method = "put".upper()
        api_url = format_url(
            f"""
            {self._base_url}/appConnectorGroup/{group_id}
            """
        )
        
        existing_group, _, error = self.get_connector_group(group_id, **kwargs)
        if error:
            return (None, None, error)

        payload = {snake_to_camel(k): v for k, v in existing_group.request_format().items()}

        add_id_groups(self.reformat_params, kwargs, payload)
        pick_version_profile(kwargs, payload)

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

        result = AppConnectorGroup(response.get_body())
        return (result, response, None)

    def delete_connector_group(self, group_id: str, **kwargs) -> tuple:
        """
        Deletes the specified App Connector Group from ZPA.

        Args:
            group_id (str): The unique identifier for the App Connector Group.

        Returns:
            tuple: A tuple containing (None, Response, error)
        """
        http_method = "delete".upper()
        api_url = format_url(
            f"""
            {self._base_url}/appConnectorGroup/{group_id}
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

