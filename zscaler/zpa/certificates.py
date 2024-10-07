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
from zscaler.zpa.models.certificates import Certificate
from zscaler.utils import snake_to_camel, format_url
from zscaler.api_response import get_paginated_data
from urllib.parse import urlencode

class CertificatesAPI(APIClient):
    """
    A Client object for the Certificates resource.
    """

    def __init__(self):
        super().__init__()  # Inherit the request executor from APIClient
        self._base_url = ""

    def list_certificates(
            self, query_params=None,
            keep_empty_params=False
    ) -> tuple:
        """
        Fetches a list of all certificates with pagination support.

        Keyword Args:
            query_params {dict}: Map of query parameters for the request.
                [query_params.pagesize] {int}: Page size for pagination.
                [query_params.search] {str}: Search string for filtering results.
                [query_params.microtenant_id] {str}: ID of the microtenant, if applicable.
                [query_params.max_items] {int}: Maximum number of items to fetch before stopping.
                [query_params.max_pages] {int}: Maximum number of pages to request before stopping.
            keep_empty_params {bool}: Whether to include empty parameters in the query string.

        Returns:
            list: A list of `Certificate` instances.

        Example:
            >>> certificates = zpa.certificates.list_certificates(search="example")
        """
        # Initialize URL and HTTP method
        http_method = "get".upper()
        api_url = format_url(f"{self._base_url}/certificate")

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
        response, error = self._request_executor.execute(request, Certificate)

        if error:
            return (None, response, error)

        # Parse the response into AppConnectorGroup instances
        try:
            result = []
            for item in response.get_body():
                result.append(Certificate(
                    self.form_response_body(item)
                ))
        except Exception as error:
            return (None, response, error)

        return (result, response, None)

    def list_issued_certificates(
            self, query_params=None,
            keep_empty_params=False
    ) -> tuple:
        """
        Fetches a list of all issued certificates with pagination support.

        Keyword Args:
            query_params {dict}: Map of query parameters for the request.
                [query_params.pagesize] {int}: Page size for pagination.
                [query_params.search] {str}: Search string for filtering results.
                [query_params.microtenant_id] {str}: ID of the microtenant, if applicable.
                [query_params.max_items] {int}: Maximum number of items to fetch before stopping.
                [query_params.max_pages] {int}: Maximum number of pages to request before stopping.
            keep_empty_params {bool}: Whether to include empty parameters in the query string.

        Returns:
            list: A list of `IssuedCertificate` instances.

        Example:
            >>> certificates = zpa.certificates.list_issued_certificates(search="example")
        """
        http_method = "get".upper()
        api_url = format_url(f"{self._base_url}/clientlessCertificate/issued")

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
        response, error = self._request_executor.execute(request, Certificate)

        if error:
            return (None, response, error)

        # Parse the response into AppConnectorGroup instances
        try:
            result = []
            for item in response.get_body():
                result.append(Certificate(
                    self.form_response_body(item)
                ))
        except Exception as error:
            return (None, response, error)

        return (result, response, None)

    def get_certificate(self, certificate_id, query_params={}, keep_empty_params=False):
        """
        Fetches a specific certificate by ID.

        Args:
            certificate_id (str): The ID of the certificate to retrieve.
            query_params (dict): Optional query parameters for the request.

        Returns:
            dict: The certificate object.
        """
        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._base_url}
            /certificate/{certificate_id}
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

        return response.get_body(), response, None

    def add_certificate(self, certificate_data, keep_empty_params=False):
        """
        Adds a new certificate.

        Args:
            certificate_data (dict): Data for the certificate to be added.

        Returns:
            dict: The newly created certificate object.
        """
        http_method = "post".upper()
        api_url = format_url(
            f"""
            {self._base_url}
            /certificate
        """
        )

        if isinstance(certificate_data, dict):
            body = certificate_data
        else:
            body = certificate_data.as_dict()

        body = {snake_to_camel(k): v for k, v in body.items()}

        request, error = self._request_executor.create_request(
            http_method, api_url, body, keep_empty_params=keep_empty_params
        )
        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request)
        if error:
            return (None, response, error)

        return response.get_body(), response, None

    def update_certificate(self, certificate_id, certificate_data, keep_empty_params=False):
        """
        Updates a specific certificate.

        Args:
            certificate_id (str): The ID of the certificate to update.
            certificate_data (dict): The new data for the certificate.

        Returns:
            dict: The updated certificate object.
        """
        http_method = "put".upper()
        api_url = format_url(
            f"""
            {self._base_url}
            /certificate/{certificate_id}
        """
        )

        if isinstance(certificate_data, dict):
            body = certificate_data
        else:
            body = certificate_data.as_dict()

        body = {snake_to_camel(k): v for k, v in body.items()}

        request, error = self._request_executor.create_request(
            http_method, api_url, body, keep_empty_params=keep_empty_params
        )
        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request)
        if error:
            return (None, response, error)

        return response.get_body(), response, None

    def delete_certificate(self, certificate_id, keep_empty_params=False):
        """
        Deletes a certificate by its ID.

        Args:
            certificate_id (str): The ID of the certificate to delete.

        Returns:
            Response: The response object for the delete operation.
        """
        http_method = "delete".upper()
        api_url = format_url(
            f"""
            {self._base_url}
            /certificate/{certificate_id}
        """
        )

        body, headers, form = {}, {}, {}

        request, error = self._request_executor.create_request(
            http_method, api_url, body, headers, form, keep_empty_params=keep_empty_params
        )
        if error:
            return (None, error)

        response, error = self._request_executor.execute(request)
        if error:
            return (response, error)

        return response, None
