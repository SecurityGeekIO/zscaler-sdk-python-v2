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
from urllib.parse import urlencode

class ServiceEdgeGroupAPI(APIClient):
    """
    A Client object for the Service Edge Group resource.
    """

    def __init__(self):
        super().__init__()
        self._base_url = ""

    def list_service_edge_groups(
            self, query_params=None,
            keep_empty_params=False
    ) -> tuple:
        """
        Enumerates connector groups in your organization with pagination.
        A subset of connector groups can be returned that match a supported
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
            tuple: A tuple containing (list of AppConnectorGroup instances, Response, error)
        """
        # Initialize URL and HTTP method
        http_method = "get".upper()
        api_url = f"{self._base_url}/serviceEdgeGroup"
        
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
        response, error = self._request_executor.execute(request, ServiceEdgeGroup)

        if error:
            return (None, response, error)

        # Parse the response into AppConnectorGroup instances
        try:
            result = []
            for item in response.get_body():
                result.append(ServiceEdgeGroup(
                    self.form_response_body(item)
                ))
        except Exception as error:
            return (None, response, error)

        return (result, response, None)

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