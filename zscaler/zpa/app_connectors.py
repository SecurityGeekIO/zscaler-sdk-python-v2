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
from zscaler.zpa.models.app_connectors import AppConnectorController
from urllib.parse import urlencode
from zscaler.utils import format_url, snake_to_camel


class AppConnectorControllerAPI(APIClient):
    """
    A Client object for the App Connectors resource.
    """

    def __init__(self):
        super().__init__()
        self._base_url = ""

    def list_connectors(
            self, query_params=None,
            keep_empty_params=False
    ) -> tuple:
        """
        Enumerates connectors in your organization with pagination.
        A subset of connectors can be returned that match a supported
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
            tuple: A tuple containing (list of AppConnector instances, Response, error)
        """
        # Initialize URL and HTTP method
        http_method = "get".upper()
        api_url = format_url(f"{self._base_url}/connector")

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
        response, error = self._request_executor.execute(request, AppConnectorController)

        if error:
            return (None, response, error)

        # Parse the response into AppConnector instances
        try:
            result = []
            for item in response.get_body():
                result.append(AppConnectorController(
                    self.form_response_body(item)
                ))
        except Exception as error:
            return (None, response, error)

        return (result, response, None)


    def get_connector(self, connector_id: str, **kwargs) -> AppConnectorController:
        """
        Returns information on the specified App Connector.

        Args:
            connector_id (str): The unique ID of the ZPA App Connector.

        Returns:
            AppConnector: The corresponding App Connector object.
        """
        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._base_url}/connector/{connector_id}
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

        return AppConnectorController(response.get_body())
    
    def get_connector_by_name(self, name: str, **kwargs) -> AppConnectorController:
        """
        Returns information on the App Connector with the specified name.

        Args:
            name (str): The name of the App Connector.

        Returns:
            AppConnector: The corresponding App Connector object or None if not found.
        """
        connectors = self.list_connectors(**kwargs)
        for connector in connectors:
            if connector.name == name:
                return connector
        return None

    def update_connector(self, connector_id: str, **kwargs) -> AppConnectorController:
        """
        Updates the specified ZPA App Connector.

        Args:
            connector_id (str): The unique ID of the App Connector.

        Returns:
            AppConnector: The updated App Connector object.
        """
        http_method = "put".upper()
        api_url = format_url(
            f"""
            {self._base_url}/connector/{connector_id}
            """
        )

        # Fetch the current App Connector data and update it with kwargs
        existing_connector = self.get_connector(connector_id)
        if not existing_connector:
            return None  # Defensive approach: exit if no connector found.

        payload = existing_connector.request_format()

        # Update payload with any new values from kwargs
        for key, value in kwargs.items():
            payload[snake_to_camel(key)] = value

        # Handle microtenant ID if provided
        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        # Prepare and execute the update request
        request, error = self._request_executor.create_request(http_method, api_url, json=payload, params=params)
        if error:
            return None

        # Execute the request and check the response
        _, error = self._request_executor.execute(request)
        if error:
            return None

        # Return the updated connector details
        return self.get_connector(connector_id)


    def delete_connector(self, connector_id: str, **kwargs) -> int:
        """
        Deletes the specified ZPA App Connector.

        Args:
            connector_id (str): The unique ID of the App Connector.

        Returns:
            int: Status code of the delete operation.
        """
        http_method = "delete".upper()
        api_url = format_url(
            f"""
            {self._base_url}/connector/{connector_id}
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

    def bulk_delete_connectors(self, connector_ids: list, **kwargs) -> int:
        """
        Bulk deletes the specified App Connectors from ZPA.

        Args:
            connector_ids (list): A list of App Connector IDs to be deleted.

        Returns:
            int: Status code for the operation.
        """
        http_method = "post".upper()
        api_url = format_url(
            f"""
            {self._base_url}/connector/bulkDelete
            """
        )
        payload = {"ids": connector_ids}

        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, json=payload, params=params)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return response.get_status_code()
