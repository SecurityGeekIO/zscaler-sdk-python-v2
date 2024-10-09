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
from zscaler.zia.models.cloud_browser_isolation import CBIProfile
from zscaler.utils import format_url
from urllib.parse import urlencode


class CBIProfileAPI(APIClient):
    """
    A Client object for the Cloud Browser Isolation Profile resource.
    """
    def __init__(self):
        super().__init__()
        self._base_url = ""

    def list_isolation_profiles(
            self, query_params=None,
            keep_empty_params=False
    ) -> tuple:
        """
        Enumerates isolation profiles in your organization with pagination.
        A subset of isolation profiles  can be returned that match a supported
        filter expression or query.

        Args:
            query_params {dict}: Map of query parameters for the request.
                [query_params.pagesize] {int}: Page size for pagination.
                [query_params.search] {str}: Search string for filtering results.
                [query_params.max_items] {int}: Maximum number of items to fetch before stopping.
                [query_params.max_pages] {int}: Maximum number of pages to request before stopping.
            keep_empty_params {bool}: Whether to include empty parameters in the query string.

        Returns:
            tuple: A tuple containing (list of isolation profiles instances, Response, error)

        Examples:
            >>> isolation_profiles = zia.isolation_profiles.list_isolation_profiles()

        """
        http_method = "get".upper()
        api_url = format_url(f"{self._base_url}/browserIsolation/profiles")

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
        response, error = self._request_executor.execute(request, CBIProfile)

        if error:
            return (None, response, error)

        try:
            result = []
            for item in response.get_body():
                result.append(CBIProfile(
                    self.form_response_body(item)
                ))
        except Exception as error:
            return (None, response, error)

        return (result, response, None)