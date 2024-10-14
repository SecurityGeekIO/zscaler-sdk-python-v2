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
from urllib.parse import urlencode


class SegmentGroupsAPI(APIClient):
    """
    A client object for the Segment Groups resource.
    """

    def __init__(self, request_executor, config):
        super().__init__()
        self._request_executor = request_executor
        customer_id = config["client"].get("customerId")
        self._base_endpoint = f"/zpa/mgmtconfig/v1/admin/customers/{customer_id}"

    def list_groups(self, query_params=None, keep_empty_params=False) -> tuple:
        """
        Enumerates segment groups in your organization with pagination.
        A subset of segment groups can be returned that match a supported
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

        Example:
            >>> segment_groups = zpa.segment_groups.list_groups(search="example", pagesize=100)
        """
        http_method = "get".upper()
        api_url = format_url(f"{self._base_endpoint}/segmentGroup")

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
        response, error = self._request_executor.execute(request, SegmentGroup)

        if error:
            return (None, response, error)

        # Parse the response into AppConnectorGroup instances
        try:
            result = []
            for item in response.get_body():
                result.append(SegmentGroup(self.form_response_body(item)))
        except Exception as error:
            return (None, response, error)

        return (result, response, None)

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
            {self._base_endpoint}
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
            {self._base_endpoint}
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
            {self._base_endpoint}
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
            {self._base_endpoint}
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
