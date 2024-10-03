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

import os
from zscaler.api_client import APIClient
from zscaler.zpa.models.service_edge_groups import ServiceEdgeGroup
from zscaler.utils import format_url, snake_to_camel, pick_version_profile, add_id_groups
from zscaler.api_response import get_paginated_data

class ServiceEdgeGroupAPI(APIClient):
    """
    A Client object for the Service Edge Group resource.
    """

    def __init__(self):
        super().__init__()
        self._base_url = ""

    def list_service_edge_groups(self, **kwargs) -> list:
        """
        Returns all configured service edge groups.

        Keyword Args:
            search (str, optional): The search string used to match against features and fields.
            max_items (int, optional): Maximum number of items to return.
            max_pages (int, optional): Maximum number of pages to return.
            pagesize (int, optional): Number of items per page (default is 100, maximum is 1000).

        Returns:
            list: A list of `ServiceEdgeGroup` instances.
        """
        api_url = f"{self._base_url}/serviceEdgeGroup"
        
        # Fetch paginated data
        list_data, error = get_paginated_data(
            request_executor=self._request_executor,
            path=api_url,
            **kwargs
        )

        if error:
            return []

        # Convert raw data to ServiceEdgeGroup objects
        return [ServiceEdgeGroup(group) for group in list_data]

    def get_service_edge_group(self, group_id: str, **kwargs) -> ServiceEdgeGroup:
        """
        Retrieves information about a specific service edge group.

        Args:
            group_id (str): The unique identifier of the service edge group.

        Returns:
            ServiceEdgeGroup: The service edge group object.
        """
        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._base_url}/serviceEdgeGroup/{group_id}
            """
        )

        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, params=params)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return ServiceEdgeGroup(response.get_body())

    def add_service_edge_group(self, name: str, latitude: str, longitude: str, location: str, **kwargs) -> ServiceEdgeGroup:
        """
        Adds a new service edge group.

        Args:
            name (str): The name of the service edge group.
            latitude (str): The latitude of the physical location.
            longitude (str): The longitude of the physical location.
            location (str): The name of the location.

        Returns:
            ServiceEdgeGroup: The newly created service edge group object.
        """
        http_method = "post".upper()
        api_url = format_url(
            f"""
            {self._base_url}/serviceEdgeGroup
            """
        )

        payload = {
            "name": name,
            "latitude": latitude,
            "longitude": longitude,
            "location": location,
        }

        add_id_groups(self.reformat_params, kwargs, payload)
        pick_version_profile(kwargs, payload)

        for key, value in kwargs.items():
            payload[snake_to_camel(key)] = value

        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, json=payload, params=params)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return ServiceEdgeGroup(response.get_body())

    def update_service_edge_group(self, group_id: str, **kwargs) -> ServiceEdgeGroup:
        """
        Updates a specified service edge group.

        Args:
            group_id (str): The unique ID of the service edge group.

        Returns:
            ServiceEdgeGroup: The updated service edge group object.
        """
        http_method = "put".upper()
        api_url = format_url(
            f"""
            {self._base_url}/serviceEdgeGroup/{group_id}
            """
        )        

        # Fetch the existing service edge group data
        existing_group = self.get_service_edge_group(group_id)
        payload = existing_group.request_format()

        add_id_groups(self.reformat_params, kwargs, payload)
        pick_version_profile(kwargs, payload)

        for key, value in kwargs.items():
            payload[snake_to_camel(key)] = value

        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, json=payload, params=params)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return ServiceEdgeGroup(response.get_body())

    def delete_service_edge_group(self, group_id: str, **kwargs) -> int:
        """
        Deletes the specified service edge group.

        Args:
            group_id (str): The unique ID of the service edge group to delete.

        Returns:
            int: Status code of the delete operation.
        """
        http_method = "delete".upper()
        api_url = format_url(
            f"""
            {self._base_url}/serviceEdgeGroup/{group_id}
            """
        )        

        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, params=params)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return response.get_status_code()