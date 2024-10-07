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
from zscaler.zpa.models.cloud_connector_groups import CloudConnectorGroup
from zscaler.utils import format_url
from zscaler.api_response import get_paginated_data
from urllib.parse import urlencode

class CloudConnectorGroupsAPI(APIClient):
    """
    A Client object for the Cloud Connector Groups resource.
    """

    def __init__(self):
        super().__init__()  # Inherit initialization from APIClient
        self._base_url = ""

    def list_cloud_connector_groups(
            self, query_params=None,
            keep_empty_params=False
    ) -> tuple:
        """
        Returns a list of all configured cloud connector groups.

        Keyword Args:
            query_params {dict}: Map of query parameters for the request.
                [query_params.pagesize] {int}: Page size for pagination.
                [query_params.search] {str}: Search string for filtering results.
                [query_params.microtenant_id] {str}: ID of the microtenant, if applicable.
                [query_params.max_items] {int}: Maximum number of items to fetch before stopping.
                [query_params.max_pages] {int}: Maximum number of pages to request before stopping.
            keep_empty_params {bool}: Whether to include empty parameters in the query string.

        Returns:
            list: A list of `CloudConnectorGroup` instances.
        
        Example:
            >>> cloud_connector_groups = zpa.cloud_connector_groups.list_cloud_connector_groups(search="example")
        """
        http_method = "get".upper()
        api_url = format_url(f"{self._base_url}/cloudConnectorGroup")

        # Handle query parameters (including microtenant_id if provided)
        query_params = query_params or {}

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
        response, error = self._request_executor.execute(request, CloudConnectorGroup)

        if error:
            return (None, response, error)

        try:
            result = []
            for item in response.get_body():
                result.append(CloudConnectorGroup(
                    self.form_response_body(item)
                ))
        except Exception as error:
            return (None, response, error)

        return (result, response, None)
    
    def get_cloud_connector_groups(self, group_id: str, query_params={}, keep_empty_params=False):
        """
        Returns information on the specified cloud connector group.

        Args:
            group_id (str): The unique identifier for the cloud connector group.
            query_params (dict): Optional query parameters.
            keep_empty_params (bool): Whether to include empty query parameters in the request.

        Returns:
            dict: The cloud connector group object.

        Example:
            >>> group, response, error = zpa.cloud_connector_groups.get_group('216196257331305019')
            >>> if error is None:
            ...     pprint(group)
        """
        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._base_url}/cloudConnectorGroup/{group_id}
        """
        )

        if query_params:
            encoded_query_params = urlencode(query_params)
            api_url += f"?{encoded_query_params}"

        body, headers, form = {}, {}, {}

        request, error = self._request_executor.create_request(
            http_method, api_url, body, headers, form, keep_empty_params=keep_empty_params
        )

        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request)

        if error:
            return (None, response, error)

        try:
            result = CloudConnectorGroup(response.get_body())
        except Exception as error:
            return (None, response, error)

        return result, response, None


# from box import Box, BoxList
# from requests import Response

# from zscaler.api_client import APIClient


# class CloudConnectorGroupsAPI(APIClient):
#     # def __init__(self, client: ZPAClient):
#     #     self.rest = client

#     def list_groups(self, **kwargs) -> BoxList:
#         """
#         Returns a list of all configured cloud connector groups.

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
#             :obj:`BoxList`: A list of all configured cloud connector groups.

#         Examples:
#             >>> for cloud_connector_group in zpa.cloud_connector_groups.list_groups():
#             ...    pprint(cloud_connector_group)

#         """
#         list, _ = self.rest.get_paginated_data(
#             path="/cloudConnectorGroup",
#         )
#         return list

#     def get_group(self, group_id: str) -> Box:
#         """
#         Returns information on the specified cloud connector group.

#         Args:
#             group_id (str):
#                 The unique identifier for the cloud connector group.

#         Returns:
#             :obj:`Box`: The resource record for the cloud connector group.

#         Examples:
#             >>> pprint(zpa.cloud_connector_groups.get_group('99999'))

#         """
#         response = self.rest.get("/cloudConnectorGroup/%s" % (group_id))
#         if isinstance(response, Response):
#             status_code = response.status_code
#             if status_code != 200:
#                 return None
#         return response
