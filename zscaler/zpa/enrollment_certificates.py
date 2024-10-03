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
from zscaler.api_response import get_paginated_data
from zscaler.utils import format_url


class EnrollmentCertificateAPI(APIClient):
    """
    A Client object for the Enrollment Certificates resource.
    """

    def __init__(self):
        super().__init__()
        self._base_url = ""

    def list_enrolment(self, **kwargs) -> tuple:
        """
        Returns a list of all configured enrollment certificates with pagination support.

        Keyword Args:
            max_items (int): The maximum number of items to request before stopping iteration.
            max_pages (int): The maximum number of pages to request before stopping iteration.
            pagesize (int): Specifies the page size. The default size is 20, but the maximum size is 500.
            search (str, optional): The search string used to match against features and fields.
            microtenant_id (str, optional): ID of the microtenant, if applicable.
            keep_empty_params (bool, optional): Whether to include empty parameters in the query string.

        Returns:
            tuple: A tuple containing a list of `EnrollmentCertificate` instances, response object, and error if any.
        """
        api_url = format_url(f"{self._base_url}/enrollmentCert")

        # Handle microtenant_id if provided
        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        # Fetch paginated data
        list_data, response, error = get_paginated_data(
            request_executor=self._request_executor,
            path=api_url,
            params=params,
            **kwargs
        )

        if error:
            return (None, response, error)

        return ([EnrollmentCertificate(cert) for cert in list_data], response, None)

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
