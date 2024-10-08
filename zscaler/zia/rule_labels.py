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
from zscaler.zia.models.rule_labels import RuleLabels
from zscaler.utils import format_url, snake_to_camel
from urllib.parse import urlencode


class RuleLabelsAPI(APIClient):
    """
    A Client object for the Rule labels resource.
    """
    def __init__(self):
        super().__init__()
        self._base_url = ""

    def list_labels(
            self, query_params=None,
            keep_empty_params=False
    ) -> tuple:
        """
        Enumerates rule labels in your organization with pagination.
        A subset of rule labels  can be returned that match a supported
        filter expression or query.

        Args:
            query_params {dict}: Map of query parameters for the request.
                [query_params.pagesize] {int}: Page size for pagination.
                [query_params.search] {str}: Search string for filtering results.
                [query_params.max_items] {int}: Maximum number of items to fetch before stopping.
                [query_params.max_pages] {int}: Maximum number of pages to request before stopping.
            keep_empty_params {bool}: Whether to include empty parameters in the query string.

        Returns:
            tuple: A tuple containing (list of Rule Labels instances, Response, error)

        Examples:
            List Rule Labels using default settings:

            >>> for label in zia.labels.list_labels():
            ...   print(label)

            List labels, limiting to a maximum of 10 items:

            >>> for label in zia.labels.list_labels(max_items=10):
            ...    print(label)

            List labels, returning 200 items per page for a maximum of 2 pages:

            >>> for label in zia.labels.list_labels(page_size=200, max_pages=2):
            ...    print(label)

        """
        http_method = "get".upper()
        api_url = format_url(f"{self._base_url}/ruleLabels")

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
        response, error = self._request_executor.execute(request, RuleLabels)

        if error:
            return (None, response, error)

        # Parse the response into AppConnectorGroup instances
        try:
            result = []
            for item in response.get_body():
                result.append(RuleLabels(
                    self.form_response_body(item)
                ))
        except Exception as error:
            return (None, response, error)

        return (result, response, None)

    def get_label(
        self, label_id: str, 
        query_params=None, 
        keep_empty_params=False
) -> tuple:
        """
        Fetches a specific rule labels by ID.

        Args:
            label_id (str): The unique identifier for the connector group.
            query_params (dict, optional): Map of query parameters for the request.
            keep_empty_params (bool): Whether to include empty parameters in the query string.

        Returns:
            tuple: A tuple containing (AppConnectorGroup instance, Response, error).
        """
        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._base_url}/ruleLabels/{label_id}
            """
        )
        # Handle optional query parameters
        query_params = query_params or {}

        # Build the query string
        if query_params:
            encoded_query_params = urlencode(query_params)
            api_url += f"?{encoded_query_params}"

        # Prepare request body, headers, and form (if needed)
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
        response, error = self._request_executor.execute(request, RuleLabels)

        if error:
            return (None, response, error)

        try:
            result = RuleLabels(
                self.form_response_body(response.get_body())
            )
        except Exception as error:
            return (None, response, error)

        return (result, response, None)

    def add_label(self, name: str, query_params=None, keep_empty_params=False) -> tuple:
        """
        Creates a new ZIA Rule Label.

        Args:
            name (str): The name of the Rule Label.
            query_params (dict, optional): Optional parameters for the request.
                [query_params.description] {str}: Additional information about the Rule Label.
            keep_empty_params (bool, optional): Whether to include empty parameters in the request.

        Returns:
            tuple: A tuple containing the newly added Rule Label (Box), response, and error.
        """
        http_method = "post".upper()
        api_url = format_url(f"{self._base_url}/ruleLabels")

        # Build the payload
        payload = {"name": name}

        # Add optional query parameters to the payload
        query_params = query_params or {}
        for key, value in query_params.items():
            payload[snake_to_camel(key)] = value

        form = {}

        # Create the request
        request, error = self._request_executor.create_request(
            http_method, api_url, payload, form, keep_empty_params=keep_empty_params
        )

        if error:
            return (None, None, error)

        # Execute the request
        response, error = self._request_executor.execute(request, RuleLabels)

        if error:
            return (None, response, error)

        try:
            result = RuleLabels(self.form_response_body(response.get_body()))
        except Exception as error:
            return (None, response, error)

        return (result, response, None)

    def update_label(self, label_id: int, **kwargs) -> tuple:
        """
        Updates information for the specified ZIA Rule Label.

        Args:
            label_id (str): The unique ID for the Rule Label.

        Returns:
            tuple: A tuple containing the updated Rule Label (Box), response, and error.
        """
        http_method = "put".upper()
        api_url = format_url(f"{self._base_url}/ruleLabels/{label_id}")

        # Construct the payload using the provided kwargs
        payload = {snake_to_camel(key): value for key, value in kwargs.items()}

        # Create and send the request
        request, error = self._request_executor.create_request(http_method, api_url, payload, {}, {})
        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request, RuleLabels)
        if error:
            return (None, response, error)

        try:
            # Parse and return the updated object from the API response
            result = RuleLabels(self.form_response_body(response.get_body()))
        except Exception as error:
            return (None, response, error)
        return (result, response, None)

    def delete_label(self, label_id: str, query_params=None, keep_empty_params=False) -> tuple:
        """
        Deletes the specified Rule Label.

        Args:
            label_id (str): The unique identifier of the Rule Label.
            query_params (dict, optional): Optional query parameters for the request.
            keep_empty_params (bool, optional): Whether to include empty parameters in the request.

        Returns:
            tuple: A tuple containing the response object and error (if any).
        """
        http_method = "delete".upper()
        api_url = format_url(f"{self._base_url}/ruleLabels/{label_id}")

        # Handle query parameters if provided
        if query_params:
            encoded_query_params = urlencode(query_params)
            api_url += f"?{encoded_query_params}"

        body = {}
        headers = {}
        form = {}

        # Create the request
        request, error = self._request_executor.create_request(
            http_method, api_url, body, headers, form, keep_empty_params=keep_empty_params
        )

        if error:
            return (None, error)

        # Execute the request
        response, error = self._request_executor.execute(request)

        if error:
            return (response, error)

        return (response, None)
