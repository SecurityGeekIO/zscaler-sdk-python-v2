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
from zscaler.request_executor import RequestExecutor
from zscaler.zpa.models.application_segment import ApplicationSegment
from zscaler.utils import format_url, add_id_groups


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
        self._request_executor: RequestExecutor = request_executor
        customer_id = config["client"].get("customerId")
        self._zpa_base_endpoint = f"/zpa/mgmtconfig/v1/admin/customers/{customer_id}"

    def list_segments(self, query_params=None, **kwargs) -> tuple:
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
        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._zpa_base_endpoint}
            /application
        """
        )

        # Handle optional query parameters
        query_params = query_params or {}
        query_params.update(kwargs)

        microtenant_id = query_params.get("microtenant_id", None)
        if microtenant_id:
            query_params["microtenantId"] = microtenant_id

        # Prepare request
        request, error = self._request_executor.create_request(http_method, api_url, params=query_params)
        if error:
            return (None, None, error)

        # Execute the request
        response, error = self._request_executor.execute(request)
        if error:
            return (None, response, error)

        try:
            result = []
            for item in response.get_all_pages_results():
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

        # Handle optional query parameters
        query_params = query_params or {}

        microtenant_id = query_params.get("microtenant_id", None)
        if microtenant_id:
            query_params["microtenantId"] = microtenant_id

        # Create the request
        request, error = self._request_executor.create_request(http_method, api_url, params=query_params)
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

    def add_segment(self, **kwargs) -> tuple:
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

        # Construct the body from kwargs (as a dictionary)
        body = kwargs

        # Check if microtenant_id is set in kwargs or the body, and use it to set query parameter
        microtenant_id = kwargs.get("microtenant_id") or body.get("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        # Reformat server_group_ids to match the expected API format (serverGroups)
        if "server_group_ids" in body:
            body["serverGroups"] = [{"id": group_id} for group_id in body.pop("server_group_ids")]

        # Convert clientless_app_ids to clientlessApps if present
        if "clientless_app_ids" in body:
            body["clientlessApps"] = body.pop("clientless_app_ids")

        if kwargs.get("tcp_port_ranges"):
            body["tcpPortRange"] = [{"from": ports[0], "to": ports[1]} for ports in kwargs.pop("tcp_port_ranges")]

        if kwargs.get("udp_port_ranges"):
            body["udpPortRange"] = [{"from": ports[0], "to": ports[1]} for ports in kwargs.pop("udp_port_ranges")]

        # Apply add_id_groups to reformat params based on self.reformat_params
        add_id_groups(self.reformat_params, kwargs, body)

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
        api_url = format_url(
            f"""
            {self._zpa_base_endpoint}
            /application/{segment_id}
        """
        )

        # Construct the body from kwargs (as a dictionary)
        body = kwargs

        # Check if microtenant_id is set in the body, and use it to set query parameter
        microtenant_id = body.get("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        # Reformat server_group_ids to match the expected API format (serverGroups)
        if "server_group_ids" in body:
            body["serverGroups"] = [{"id": group_id} for group_id in body.pop("server_group_ids")]

        # Convert clientless_app_ids to clientlessApps if present
        if "clientless_app_ids" in body:
            body["clientlessApps"] = body.pop("clientless_app_ids")

        # Handle clientlessApps block and automatically assign appId
        if "clientlessApps" in body:
            for clientless_app in body["clientlessApps"]:
                clientless_app["appId"] = segment_id  # Set appId to the segment_id

        # Handle port ranges if present in kwargs
        if kwargs.get("tcp_port_ranges"):
            body["tcpPortRange"] = [{"from": ports[0], "to": ports[1]} for ports in kwargs.pop("tcp_port_ranges")]

        if kwargs.get("udp_port_ranges"):
            body["udpPortRange"] = [{"from": ports[0], "to": ports[1]} for ports in kwargs.pop("udp_port_ranges")]

        # Apply reformatting of certain fields (if necessary)
        add_id_groups(self.reformat_params, kwargs, body)

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
        Deletes the specified Application Segment from ZPA.

        Args:
            segment_id (str): The unique identifier for the Application Segment.
            force_delete (bool):
                Setting this field to true deletes the mapping between Application Segment and Segment Group.
            microtenant_id (str, optional): The optional ID of the microtenant if applicable.

        Returns:
            tuple: A tuple containing the response and error (if any).
        """
        http_method = "delete".upper()
        api_url = format_url(
            f"""
            {self._zpa_base_endpoint}
            /application/{segment_id}
        """
        )

        # Handle microtenant_id in URL params if provided
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

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

    def get_segments_by_type(self, application_type: str, expand_all: bool = False, query_params=None, **kwargs) -> tuple:
        """
        Retrieve all configured application segments of a specified type, optionally expanding all related data.

        Args:
            application_type (str): Type of application segment to retrieve.
            Must be one of "BROWSER_ACCESS", "INSPECT", "SECURE_REMOTE_ACCESS".
            expand_all (bool, optional): Whether to expand all related data. Defaults to False.

        Keyword Args:
            query_params {dict}: Map of query parameters for the request.
                [query_params.pagesize] {int}: Page size for pagination.
                [query_params.search] {str}: Search string for filtering results.
                [query_params.expand_all] {bool}: Additional information related to the applications
                [query_params.microtenant_id] {str}: ID of the microtenant, if applicable.
                [query_params.max_items] {int}: Maximum number of items to fetch before stopping.
                [query_params.max_pages] {int}: Maximum number of pages to request before stopping.

        Returns:
            tuple: List of application segments.

        Examples:
            >>> app_type = 'BROWSER_ACCESS'
            >>> expand_all = True
            >>> search = "ba_server01"
            >>> app_segments = zpa.app_segments.get_segments_by_type(app_type, expand_all, search=search)
        """
        # Ensure the applicationType is provided
        if not application_type:
            raise ValueError("The 'application_type' parameter must be provided.")

        http_method = "GET"
        api_url = format_url(
            f"""
            {self._zpa_base_endpoint}
            /application/getAppsByType
        """
        )

        # Initialize query parameters and update with additional kwargs
        query_params = query_params or {}
        query_params.update(kwargs)

        # Ensure applicationType is always present in the query parameters
        query_params["applicationType"] = application_type

        # Handle optional expandAll parameter (add even when False as per API requirement)
        query_params["expandAll"] = str(expand_all).lower()  # Converts True/False to 'true'/'false'

        # Handle microtenant_id if provided
        microtenant_id = query_params.get("microtenant_id", None)
        if microtenant_id:
            query_params["microtenantId"] = microtenant_id

        # Prepare request
        request, error = self._request_executor.create_request(http_method, api_url, body={}, headers={}, params=query_params)
        if error:
            return (None, None, error)

        # Execute the request
        response, error = self._request_executor.execute(request)
        if error:
            return (None, response, error)

        try:
            # Directly return the raw response data as a list of dictionaries
            result = response.get_all_pages_results()
        except Exception as error:
            return (None, response, error)

        return (result, response, None)
