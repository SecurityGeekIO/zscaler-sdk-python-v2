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
from zscaler.zpa.models.application_segment import ApplicationSegment
from urllib.parse import urlencode
from zscaler.utils import format_url


class ApplicationSegmentAPI(APIClient):
    """
    A client object for the Application Segments resource.
    """

    def __init__(self):
        super().__init__()  # Inherit initialization from APIClient
        self._base_url = ""

    def list_segments(
            self, query_params=None,
            keep_empty_params=False
    ) -> tuple:
        """
        Enumerates application segments in your organization with pagination.
        A subset of application segments can be returned that match a supported
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
            tuple: A tuple containing (list of ApplicationSegment instances, Response, error)
        """
        # Initialize URL and HTTP method
        http_method = "get".upper()
        api_url = format_url(f"{self._base_url}/application")

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
        response, error = self._request_executor.execute(request, ApplicationSegment)

        if error:
            return (None, response, error)

        # Parse the response into ApplicationSegment instances
        try:
            result = []
            for item in response.get_body():
                result.append(ApplicationSegment(
                    self.form_response_body(item)
                ))
        except Exception as error:
            return (None, response, error)

        return (result, response, None)
    
    def get_segment(self, segment_id: str, **kwargs) -> tuple:
        """
        Retrieve an application segment by its ID.

        Args:
            segment_id (str): The unique identifier of the application segment.

        Keyword Args:
            microtenant_id (str, optional): ID of the microtenant, if applicable.

        Returns:
            tuple: A tuple containing the `ApplicationSegment` instance, response object, and error if any.
        """
        http_method = "get".upper()
        api_url = format_url(f"""
            {self._base_url}
            /application/{segment_id}
        """)

        # Handle microtenant_id if provided
        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, {}, params)
        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request, ApplicationSegment)
        if error:
            return (None, response, error)

        return (ApplicationSegment(response.get_body()), response, None)

    def add_segment(self, name: str, domain_names: list, segment_group_id: str, server_group_ids: list, **kwargs) -> tuple:
        """
        Create a new application segment.

        Args:
            name (str): The name of the application segment.
            domain_names (list): A list of domain names for the application segment.
            segment_group_id (str): The ID of the segment group.
            server_group_ids (list): A list of server group IDs.

        Keyword Args:
            microtenant_id (str, optional): ID of the microtenant, if applicable.

        Returns:
            tuple: A tuple containing the `ApplicationSegment` instance, response object, and error if any.
        """
        http_method = "post".upper()
        api_url = format_url(f"""
            {self._base_url}
            /application
        """)

        payload = {
            "name": name,
            "domainNames": domain_names,
            "segmentGroupId": segment_group_id,
            "serverGroups": [{"id": group_id} for group_id in server_group_ids],
        }
        payload.update(APIClient.format_request_body(kwargs))

        # Handle microtenant_id if provided
        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, payload, params)
        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request, ApplicationSegment)
        if error:
            return (None, response, error)

        return (ApplicationSegment(response.get_body()), response, None)

    def update_segment(self, segment_id: str, **kwargs) -> tuple:
        """
        Update an existing application segment.

        Args:
            segment_id (str): The unique identifier of the application segment.

        Keyword Args:
            microtenant_id (str, optional): ID of the microtenant, if applicable.

        Returns:
            tuple: A tuple containing the updated `ApplicationSegment` instance, response object, and error if any.
        """
        http_method = "put".upper()
        api_url = format_url(f"""
            {self._base_url}
            /application/{segment_id}
        """)

        # Get the current segment data and update it with the provided kwargs
        existing_segment, response, error = self.get_segment(segment_id)
        if error:
            return (None, response, error)

        payload = existing_segment.request_format()
        payload.update(APIClient.format_request_body(kwargs))

        # Handle microtenant_id if provided
        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, payload, params)
        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request, ApplicationSegment)
        if error:
            return (None, response, error)

        return (ApplicationSegment(response.get_body()), response, None)

    def delete_segment(self, segment_id: str, force_delete: bool = False, **kwargs) -> tuple:
        """
        Delete an application segment.

        Args:
            segment_id (str): The unique identifier of the application segment.
            force_delete (bool, optional): Whether to force the deletion. Default is False.

        Keyword Args:
            microtenant_id (str, optional): ID of the microtenant, if applicable.

        Returns:
            tuple: A tuple containing the status code, response object, and error if any.
        """
        http_method = "delete".upper()
        api_url = format_url(f"""
            {self._base_url}
            /application/{segment_id}
        """)

        query = "forceDelete=true" if force_delete else ""

        # Handle microtenant_id if provided
        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, f"{api_url}?{query}", {}, params)
        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request)
        if error:
            return (None, response, error)

        return (response.status_code, response, None)
