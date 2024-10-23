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
from zscaler.utils import format_url, transform_clientless_apps, add_id_groups


class ApplicationSegmentAPI(APIClient):
    reformat_params = [
        ("clientless_app_ids", "clientlessApps"),
        ("server_group_ids", "serverGroups"),
    ]
    """
    A client object for the Application Segments resource.
    """

    def __init__(self, request_executor, config):
        super().__init__()
        self._request_executor = request_executor
        customer_id = config["client"].get("customerId")
        self._zpa_base_endpoint = f"/zpa/mgmtconfig/v1/admin/customers/{customer_id}"

    def list_segments(self, query_params=None) -> tuple:
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

        Returns:
            tuple: A tuple containing (list of ApplicationSegment instances, Response, error)
        """
        # Initialize URL and HTTP method
        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._zpa_base_endpoint}
            /application
        """
        )

        query_params = query_params or {}
        microtenant_id = query_params.get("microtenant_id", None)
        if microtenant_id:
            query_params["microtenantId"] = microtenant_id

        # Build the query string
        if query_params:
            encoded_query_params = urlencode(query_params)
            api_url += f"?{encoded_query_params}"

        # Prepare request body and headers
        body = {}
        headers = {}

        # Prepare request
        request, error = self._request_executor.create_request(http_method, api_url, body, headers)
        if error:
            return (None, None, error)

        # Execute the request
        response, error = self._request_executor.execute(request)
        if error:
            return (None, response, error)

        try:
            result = []
            for item in response.get_results():
                result.append(ApplicationSegment(self.form_response_body(item)))
        except Exception as error:
            return (None, response, error)
        return (result, response, None)

    def get_segment(self, segment_id: str, query_params=None) -> tuple:
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
        api_url = format_url(
            f"""
            {self._zpa_base_endpoint}
            /application/{segment_id}
        """
        )

        # Build the query string
        if query_params:
            encoded_query_params = urlencode(query_params)
            api_url += f"?{encoded_query_params}"

        # Prepare request body, headers, and form (if needed)
        body = {}
        headers = {}

        # Create the request
        request, error = self._request_executor.create_request(http_method, api_url, body, headers)

        if error:
            return (None, None, error)

        # Execute the request
        response, error = self._request_executor.execute(request, ApplicationSegment)

        if error:
            return (None, response, error)

        # Parse the response into an AppConnectorGroup instance
        try:
            result = ApplicationSegment(self.form_response_body(response.get_body()))
        except Exception as error:
            return (None, response, error)
        return (result, response, None)

    def add_segment(self, app_segment) -> tuple:
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
        api_url = format_url(
            f"""
            {self._zpa_base_endpoint}
            /application
        """
        )

        # Ensure app_segment is a dictionary
        if isinstance(app_segment, dict):
            body = app_segment
        else:
            body = app_segment.as_dict()

        # Check if microtenant_id is set in the body, and use it to set query parameter
        microtenant_id = body.get("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        # Reformat server_group_ids to match the expected API format (serverGroups)
        if "server_group_ids" in body:
            body["serverGroups"] = [{"id": group_id} for group_id in body.pop("server_group_ids")]

        # Reformat clientless_app_ids if present
        if "clientless_app_ids" in body:
            body["clientlessApps"] = transform_clientless_apps(body.pop("clientless_app_ids"))

        # Create the request
        request, error = self._request_executor.create_request(http_method, api_url, body=body, params=params)
        if error:
            return (None, None, error)

        # Execute the request
        response, error = self._request_executor.execute(request, ApplicationSegment)
        if error:
            return (None, response, error)

        try:
            result = ApplicationSegment(self.form_response_body(response.get_body()))
        except Exception as error:
            return (None, response, error)
        return (result, response, None)

    def update_segment(self, segment_id: str, app_segment) -> tuple:
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
        api_url = format_url(
            f"""
            {self._zpa_base_endpoint}
            /application/{segment_id}
        """
        )

        # Ensure app_segment is a dictionary
        if isinstance(app_segment, dict):
            body = app_segment
        else:
            body = app_segment.as_dict()

        # Check if microtenant_id is set in the body, and use it to set query parameter
        microtenant_id = body.get("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        # Reformat server_group_ids to match the expected API format (serverGroups)
        if "server_group_ids" in body:
            body["serverGroups"] = [{"id": group_id} for group_id in body.pop("server_group_ids")]

        # Reformat clientless_app_ids if present
        if "clientless_app_ids" in body:
            body["clientlessApps"] = transform_clientless_apps(body.pop("clientless_app_ids"))
        # Create the request
        request, error = self._request_executor.create_request(http_method, api_url, body, {}, params)
        if error:
            return (None, None, error)

        # Execute the request
        response, error = self._request_executor.execute(request, ApplicationSegment)
        if error:
            return (None, response, error)

        # Handle case where no content is returned (204 No Content)
        if response is None:
            # Return a meaningful result to indicate success
            return (ApplicationSegment({"id": segment_id}), None, None)

        try:
            result = ApplicationSegment(self.form_response_body(response.get_body()))
        except Exception as error:
            return (None, response, error)
        return (result, response, None)

    def delete_segment(self, segment_id: str, force_delete: bool = False, microtenant_id: str = None) -> tuple:
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
        api_url = format_url(
            f"""
            {self._zpa_base_endpoint}
            /application/{segment_id}
        """
        )

        # Handle microtenant_id and forceDelete in URL params
        params = {}
        if microtenant_id:
            params["microtenantId"] = microtenant_id
        if force_delete:
            params["forceDelete"] = "true"

        # Create the request
        request, error = self._request_executor.create_request(http_method, api_url, params=params)
        if error:
            return (None, None, error)

        # Execute the request
        response, error = self._request_executor.execute(request)
        if error:
            return (None, response, error)

        return (None, response, None)
