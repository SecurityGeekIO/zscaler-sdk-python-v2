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
from zscaler.zpa.models.enrollment_certificates import EnrollmentCertificate
from urllib.parse import urlencode
from zscaler.utils import format_url


class EnrollmentCertificateAPI(APIClient):
    """
    A Client object for the Enrollment Certificates resource.
    """

    def __init__(self):
        super().__init__()
        self._base_url = ""

    def list_enrolment(
            self, query_params=None,
            keep_empty_params=False
    ) -> tuple:
        """
        Enumerates Enrollment Certificates in your organization with pagination.
        A subset of Enrollment Certificates can be returned that match a supported
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
            tuple: A tuple containing (list of EnrollmentCertificate instances, Response, error)
        """
        http_method = "get".upper()
        api_url = format_url(f"{self._base_url}/enrollmentCert")

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
        response, error = self._request_executor.execute(request, EnrollmentCertificate)

        if error:
            return (None, response, error)

        # Parse the response into AppConnectorGroup instances
        try:
            result = []
            for item in response.get_body():
                result.append(EnrollmentCertificate(
                    self.form_response_body(item)
                ))
        except Exception as error:
            return (None, response, error)

        return (result, response, None)

    def get_enrolment(self, certificate_id: str, **kwargs) -> tuple:
        """
        Returns information on the specified enrollment certificate.

        Args:
            certificate_id (str): The unique ID of the enrollment certificate.

        Keyword Args:
            microtenant_id (str, optional): ID of the microtenant, if applicable.

        Returns:
            tuple: A tuple containing the `EnrollmentCertificate` instance, response object, and error if any.
        """
        api_url = format_url(f"{self._base_url}/enrollmentCert/{certificate_id}")

        # Handle microtenant_id if provided
        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request("GET", api_url, {}, params)
        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request, EnrollmentCertificate)
        if error:
            return (None, response, error)

        return (EnrollmentCertificate(response.get_body()), response, None)

    def get_enrolment_cert_by_name(self, name: str, **kwargs) -> tuple:
        """
        Returns information on the certificate with the specified name.

        Args:
            name (str): The name of the certificate.

        Keyword Args:
            microtenant_id (str, optional): ID of the microtenant, if applicable.

        Returns:
            tuple: A tuple containing the `EnrollmentCertificate` instance, response object, and error if any.
        """
        certs, response, error = self.list_enrolment(**kwargs)
        if error:
            return (None, response, error)

        for cert in certs:
            if cert.name == name:
                return (cert, response, None)

        return (None, response, "Certificate not found.")
