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
from zscaler.zpa.models.segment_group import SegmentGroup
from zscaler.utils import format_url
from zscaler.api_response import get_paginated_data

class SegmentGroupsAPI(APIClient):
    """
    A client object for the Segment Groups resource.
    """

    def __init__(self):
        super().__init__()
        self._base_url = ""

    def list_groups(self, **kwargs) -> list:
        """
        Returns all configured segment groups with pagination support.

        Keyword Args:
            - search (str): The search string used to match against features and fields.
            - search_field (str): The field to be searched (default is "name").
            - max_items (int): Maximum number of items to return.
            - max_pages (int): Maximum number of pages to return.
            - pagesize (int): Number of items per page (default is 20, maximum is 500).
            - keep_empty_params (bool): Whether to include empty parameters in the query string.
            - microtenant_id (str): ID of the microtenant, if applicable.

        Returns:
            list: A list of `SegmentGroup` instances.
        
        Example:
            >>> segment_groups = zpa.segment_groups.list_groups(search="example", pagesize=100)
        """
        api_url = format_url(f"{self._base_url}/segmentGroup")

        # Add microtenant_id to kwargs if provided
        microtenant_id = kwargs.pop("microtenant_id", None)
        if microtenant_id:
            kwargs["microtenantId"] = microtenant_id

        # Fetch paginated data using the request executor
        list_data, error = get_paginated_data(
            request_executor=self._request_executor,
            path=api_url,
            **kwargs
        )

        if error:
            return []

        # Convert the raw segment group data into SegmentGroup objects
        return [SegmentGroup(group) for group in list_data]

    def get_group(self, group_id: str, **kwargs) -> SegmentGroup:
        """
        Gets information on the specified segment group.

        Args:
            group_id (str): The unique identifier of the segment group.

        Returns:
            SegmentGroup: The corresponding segment group object.
        """
        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._base_url}
            /segmentGroup/{group_id}
            """
        )

        # Add microtenant_id to kwargs if provided
        microtenant_id = kwargs.pop("microtenant_id", None)
        if microtenant_id:
            kwargs["microtenantId"] = microtenant_id

        request, error = self._request_executor.create_request(http_method, api_url, {}, kwargs)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return SegmentGroup(response.get_body())

    def add_group(self, name: str, enabled: bool = True, **kwargs) -> SegmentGroup:
        """
        Adds a new segment group.

        Args:
            name (str): The name of the segment group.
            enabled (bool): Enable the segment group. Defaults to True.

        Returns:
            SegmentGroup: The created segment group object.
        """
        http_method = "post".upper()
        api_url = format_url(
            f"""
            {self._base_url}
            /segmentGroup
        """
        )

        payload = {
            "name": name,
            "enabled": enabled,
        }

        # Add applications if provided
        if kwargs.get("application_ids"):
            payload["applications"] = [{"id": app_id} for app_id in kwargs.pop("application_ids")]

        payload.update(kwargs)

        # Add microtenant_id to kwargs if provided
        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, payload, params)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return SegmentGroup(response.get_body())

    def update_group(self, group_id: str, **kwargs) -> SegmentGroup:
        """
        Updates the specified segment group.

        Args:
            group_id (str): The unique identifier for the segment group being updated.

        Returns:
            SegmentGroup: The updated segment group object.
        """
        http_method = "put".upper()
        api_url = format_url(
            f"""
            {self._base_url}
            /segmentGroup/{group_id}
        """
        )

        # Get the current segment group data and update it with the new kwargs
        group_data = self.get_group(group_id).request_format()
        group_data.update(kwargs)

        # Add microtenant_id to kwargs if provided
        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, group_data, params)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return SegmentGroup(response.get_body())

    def delete_group(self, group_id: str, **kwargs) -> int:
        """
        Deletes the specified segment group.

        Args:
            group_id (str): The unique identifier for the segment group to be deleted.

        Returns:
            int: Status code of the delete operation.
        """
        http_method = "delete".upper()
        api_url = format_url(
            f"""
            {self._base_url}
            /segmentGroup/{group_id}
        """
        )
        
        # Add microtenant_id to kwargs if provided
        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, {}, params)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return response.status_code


# from box import Box, BoxList
# from requests import Response
# import logging
# from zscaler.utils import snake_to_camel
# from zscaler.utils import format_url
# from zscaler.api_client import APIClient

# # Setup logging
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger()

# class SegmentGroupsAPI(APIClient):

#     def list_groups(self, **kwargs) -> BoxList:
#         """
#         Returns a list of all configured segment groups.

#         Returns:
#             :obj:`BoxList`: A list of all configured segment groups.

#         Examples:
#             >>> for segment_group in zpa.segment_groups.list_groups():
#             ...    pprint(segment_group)

#         """
#         list, _ = self.rest.get_paginated_data(path="/segmentGroup", **kwargs, api_version="v1")
#         return list

#     def get_group(self, group_id: str, **kwargs) -> Box:
#         """
#         Returns information on the specified segment group.

#         Args:
#             group_id (str): The unique identifier for the segment group.

#         Returns:
#             :obj:`Box`: The resource record for the segment group.

#         Examples:
#             >>> pprint(zpa.segment_groups.get_group('99999'))

#         """
#         params = {}
#         if "microtenant_id" in kwargs:
#             params["microtenantId"] = kwargs.pop("microtenant_id")
#         return self.rest.get(f"segmentGroup/{group_id}", params=params)

#     def get_segment_group_by_name(self, name: str, **kwargs) -> Box:
#         """
#         Returns information on the segment group with the specified name.

#         Args:
#             name (str): The name of the segment group.

#         Returns:
#             :obj:`Box` or None: The resource record for the segment group if found, otherwise None.

#         Examples:
#             >>> segment_group = zpa.segment_groups.get_segment_group_by_name('example_name')
#             >>> if segment_group:
#             ...     pprint(segment_group)
#             ... else:
#             ...     print("Segment group not found")
#         """
#         groups = self.list_groups(**kwargs)
#         for group in groups:
#             if group.get("name") == name:
#                 return group
#         return None

#     def add_group(self, name: str, enabled: bool = True, api_version="v1", handler="mgmtconfig", **kwargs) -> dict:
#         """
#         Adds a new segment group.

#         Args:
#             name (str): The name of the new segment group.
#             enabled (bool): Enable the segment group. Defaults to True.
#             api_version (str): API version (e.g., "v1", "v2"). Defaults to "v1".
#             handler (str): API handler (e.g., "mgmtconfig", "userconfig"). Defaults to "mgmtconfig".
#             **kwargs:

#         Keyword Args:
#             application_ids (:obj:`list` of :obj:`dict`):
#                 Unique application IDs to associate with the segment group.
#             description (str):
#                 A description for the segment group.
#             microtenant_id (str):
#                 The microtenant ID to be used for this request.

#         Returns:
#             :obj:`dict`: The resource record for the newly created segment group.
#         """
#         http_method = "POST"

#         # Construct the full API URL with the correct placement of customerId
#         api_url = f"/zpa/{handler}/{api_version}/admin/customers/{self._customer_id}/segmentGroup"

#         # Log the constructed API URL
#         logger.debug(f"Constructed API URL: {api_url}")
#         print(f"Constructed API URL: {api_url}")

#         # Prepare the payload
#         payload = {
#             "name": name,
#             "enabled": enabled,
#         }

#         # Log the initial payload
#         logger.debug(f"Initial Payload: {payload}")
#         print(f"Initial Payload: {payload}")

#         if kwargs.get("application_ids"):
#             payload["applications"] = [{"id": app_id} for app_id in kwargs.pop("application_ids")]

#         # Additional arguments passed
#         for key, value in kwargs.items():
#             payload[snake_to_camel(key)] = value

#         # Log the final payload
#         logger.debug(f"Final Payload: {payload}")
#         print(f"Final Payload: {payload}")

#         # Create query parameters
#         microtenant_id = kwargs.pop("microtenant_id", None)
#         query_params = {"microtenantId": microtenant_id} if microtenant_id else {}

#         headers = {
#             "Accept": "application/json",
#             "Content-Type": "application/json"
#         }

#         # Log query parameters and headers
#         logger.debug(f"Query Params: {query_params}")
#         logger.debug(f"Headers: {headers}")
#         print(f"Query Params: {query_params}")
#         print(f"Headers: {headers}")

#         # Create the request using the RequestExecutor
#         request, error = self._request_executor.create_request(
#             method=http_method,
#             url=api_url,
#             body=payload,
#             headers=headers,
#             params=query_params
#         )

#         if error:
#             raise Exception(f"Error creating request: {error}")

#         # Log the request before execution
#         logger.debug(f"Request before execution: {request}")
#         print(f"Request before execution: {request}")

#         # Execute the request
#         response, error = self._request_executor.execute(request)

#         if error:
#             raise Exception(f"API call failed with error: {error}")

#         # Log the response status code and body
#         logger.debug(f"Response Status Code: {response.status_code}")
#         logger.debug(f"Response Body: {response.text}")
#         print(f"Response Status Code: {response.status_code}")
#         print(f"Response Body: {response.text}")

#         # Check for a success status code (like 201 Created)
#         if response.status_code >= 300:
#             raise Exception(f"API call failed with status code {response.status_code}: {response.text}")

#         # Handle successful creation (status 201)
#         if response.status_code == 201:
#             return response.json()

#         # For other successful cases (like 200), return the response as-is
#         return response.json()


#     def update_group(self, group_id: str, **kwargs) -> Box:
#         """
#         Updates an existing segment group.

#         Args:
#             group_id (str): The unique identifier for the segment group to be updated.
#             **kwargs: Optional keyword args.

#         Keyword Args:
#             name (str): The name of the new segment group.
#             enabled (bool): Enable the segment group.
#             application_ids (:obj:`list` of :obj:`dict`): Unique application IDs to associate with the segment group.
#             config_space (str): The config space for the segment group. Can either be DEFAULT or SIEM.
#             description (str): A description for the segment group.
#             policy_migrated (bool):
#             microtenant_id (str): The microtenant ID to be used for this request.

#         Returns:
#             :obj:`Box`: The resource record for the updated segment group.

#         Examples:
#             Updating the name of a segment group:

#             >>> zpa.segment_groups.update_group('99999',
#             ...    name='updated_name')

#         """
#         payload = {snake_to_camel(k): v for k, v in self.get_group(group_id).items()}

#         if kwargs.get("application_ids"):
#             payload["applications"] = [{"id": app_id} for app_id in kwargs.pop("application_ids")]

#         for key, value in kwargs.items():
#             payload[snake_to_camel(key)] = value

#         microtenant_id = kwargs.pop("microtenant_id", None)
#         params = {"microtenantId": microtenant_id} if microtenant_id else {}

#         resp = self.rest.put(f"segmentGroup/{group_id}", json=payload, params=params).status_code
#         if not isinstance(resp, Response):
#             return self.get_group(group_id)

#     # REQUIRES DEPLOYMENT OF ET-76506 IN PRODUCTION BEFORE ENABLING IT.
#     def update_group_v2(self, group_id: str, **kwargs) -> Box:
#         """
#         Updates an existing segment group using v2 endpoint.

#         Args:
#             group_id (str): The unique identifier for the segment group to be updated.
#             **kwargs: Optional keyword args.

#         Keyword Args:
#             name (str): The name of the new segment group.
#             enabled (bool): Enable the segment group.
#             application_ids (:obj:`list` of :obj:`dict`): Unique application IDs to associate with the segment group.
#             config_space (str): The config space for the segment group. Can either be DEFAULT or SIEM.
#             description (str): A description for the segment group.
#             policy_migrated (bool):
#             microtenant_id (str): The microtenant ID to be used for this request.

#         Returns:
#             :obj:`Box`: The resource record for the updated segment group.

#         Examples:
#             Updating the name of a segment group:

#             >>> zpa.segment_groups.update_group_v2('99999',
#             ...    name='updated_name')

#         """
#         payload = {snake_to_camel(k): v for k, v in self.get_group(group_id).items()}

#         if kwargs.get("application_ids"):
#             payload["applications"] = [{"id": app_id} for app_id in kwargs.pop("application_ids")]

#         for key, value in kwargs.items():
#             payload[snake_to_camel(key)] = value

#         microtenant_id = kwargs.pop("microtenant_id", None)
#         params = {"microtenantId": microtenant_id} if microtenant_id else {}

#         resp = self.rest.put(f"segmentGroup/{group_id}", json=payload, params=params, api_version="v2").status_code
#         if not isinstance(resp, Response):
#             return self.get_group(group_id)

#     def delete_group(self, group_id: str, **kwargs) -> int:
#         """
#         Deletes the specified segment group.

#         Args:
#             group_id (str): The unique identifier for the segment group to be deleted.

#         Returns:
#             :obj:`int`: The response code for the operation.

#         Examples:
#             >>> zpa.segment_groups.delete_group('99999')

#         """
#         params = {}
#         if "microtenant_id" in kwargs:
#             params["microtenantId"] = kwargs.pop("microtenant_id")
#         return self.rest.delete(f"segmentGroup/{group_id}", params=params).status_code
