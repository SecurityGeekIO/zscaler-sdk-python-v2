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


class SSLInspectionAPI(APIClient):
    """
    A Client object for the SSL Inspection resource.
    """

    _zia_base_endpoint = "/zia/api/v1"

    def __init__(self, request_executor):
        super().__init__()
        self._request_executor: RequestExecutor = request_executor

    def get_csr(self) -> tuple:
        """
        Downloads a CSR after it has been generated.
        """
        http_method = "get".upper()
        api_url = f"{self._zia_base_endpoint}/sslSettings/downloadcsr"

        request, error = self._request_executor.create_request(http_method, api_url, {}, {})
        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request)
        if error:
            return (None, response, error)

        return (response.get_body().text, response, None)

    def get_intermediate_ca(self) -> tuple:
        """
        Returns information on the signed Intermediate Root CA certificate.
        """
        http_method = "get".upper()
        api_url = f"{self._zia_base_endpoint}/sslSettings/showcert"

        request, error = self._request_executor.create_request(http_method, api_url, {}, {})
        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request)
        if error:
            return (None, response, error)

        return (self.form_response_body(response.get_body()), response, None)

    def generate_csr(
        self,
        cert_name: str,
        cn: str,
        org: str,
        dept: str,
        city: str,
        state: str,
        country: str,
        signature: str,
    ) -> tuple:
        """
        Generates a Certificate Signing Request.
        """
        http_method = "post".upper()
        api_url = f"{self._zia_base_endpoint}/sslSettings/generatecsr"

        payload = {
            "certName": cert_name,
            "commName": cn,
            "orgName": org,
            "deptName": dept,
            "city": city,
            "state": state,
            "country": country,
            "signatureAlgorithm": signature,
        }

        request, error = self._request_executor.create_request(http_method, api_url, payload, {}, {})
        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request)
        if error:
            return (None, response, error)

        return (response.get_body(), response, None)

    def upload_int_ca_cert(self, cert: tuple) -> tuple:
        """
        Uploads a signed Intermediate Root CA certificate.
        """
        http_method = "post".upper()
        api_url = f"{self._zia_base_endpoint}/sslSettings/uploadcert/text"

        payload = {"fileUpload": cert}

        request, error = self._request_executor.create_request(http_method, api_url, payload, {}, {}, files=True)
        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request)
        if error:
            return (None, response, error)

        return (response.get_body(), response, None)

    def upload_int_ca_chain(self, cert: tuple) -> tuple:
        """
        Uploads the Intermediate Root CA certificate chain.
        """
        http_method = "post".upper()
        api_url = f"{self._zia_base_endpoint}/sslSettings/uploadcertchain/text"

        payload = {"fileUpload": cert}

        request, error = self._request_executor.create_request(http_method, api_url, payload, {}, {}, files=True)
        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request)
        if error:
            return (None, response, error)

        return (response.get_body(), response, None)

    def delete_int_chain(self) -> tuple:
        """
        Deletes the Intermediate Root CA certificate chain.
        """
        http_method = "delete".upper()
        api_url = f"{self._zia_base_endpoint}/sslSettings/certchain"

        request, error = self._request_executor.create_request(http_method, api_url, {}, {})
        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request)
        if error:
            return (None, response, error)

        return (response.get_body(), response, None)
