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

    def list_certificates(self, **kwargs) -> list:
        """
        Fetches a list of all certificates with pagination support.

        Keyword Args:
            max_items (int): The maximum number of items to request before stopping iteration.
            max_pages (int): The maximum number of pages to request before stopping iteration.
            pagesize (int): The page size, default is 20 and maximum is 500.
            search (str, optional): The search string used to match against features and fields.
            keep_empty_params (bool): Whether to include empty parameters in the query string.

        Returns:
            list: A list of `Certificate` instances.

        Example:
            >>> certificates = zpa.certificates.list_certificates(search="example")
        """
        api_url = format_url(f"{self._base_url}/certificate")

        # Fetch paginated data using the request_executor
        list_data, error = get_paginated_data(
            request_executor=self._request_executor,
            path=api_url,
            **kwargs  # Pass additional pagination/filter params
        )

        if error:
            raise Exception(f"Error fetching certificates data: {error}")

        # Convert the raw certificate data into Certificate objects
        return [Certificate(cert) for cert in list_data]

    def list_issued_certificates(self, **kwargs) -> list:
        """
        Fetches a list of all issued certificates with pagination support.

        Keyword Args:
            max_items (int): The maximum number of items to request before stopping iteration.
            max_pages (int): The maximum number of pages to request before stopping iteration.
            pagesize (int): The page size, default is 20 and maximum is 500.
            search (str, optional): The search string used to match against features and fields.
            keep_empty_params (bool): Whether to include empty parameters in the query string.

        Returns:
            list: A list of `IssuedCertificate` instances.

        Example:
            >>> certificates = zpa.certificates.list_issued_certificates(search="example")
        """
        api_url = format_url(f"{self._base_url}/clientlessCertificate/issued")

        # Fetch paginated data using the request_executor
        list_data, error = get_paginated_data(
            request_executor=self._request_executor,
            path=api_url,
            **kwargs  # Pass additional pagination/filter params
        )

        if error:
            raise Exception(f"Error fetching issued certificates data: {error}")

        # Convert the raw issued certificate data into IssuedCertificate objects
        return [Certificate(cert) for cert in list_data]

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



# from box import Box, BoxList
# from requests import Response

# from zscaler.utils import snake_to_camel
# from zscaler.api_client import APIClient


# class CertificatesAPI(APIClient):
#     # def __init__(self, client: ZPAClient):
#     #     self.rest = client

#     def list_issued_certificates(self, **kwargs) -> BoxList:
#         """
#         Returns a list of all Browser Access certificates.

#         Args:
#             **kwargs: Optional keyword args.

#         Keyword Args:
#             max_items (int, optional):
#                 The maximum number of items to request before stopping iteration.
#             max_pages (int, optional):
#                 The maximum number of pages to request before stopping iteration.
#             pagesize (int, optional):
#                 Specifies the page size. The default size is 20, but the maximum size is 500.
#             search (str, optional):
#                 The search string used to match against features and fields.

#         Returns:
#             :obj:`BoxList`: List of all Browser Access certificates.

#         Examples:
#             >>> for cert in zpa.certificates.list_issued_certificates():
#             ...    print(cert)

#         """
#         list, _ = self.rest.get_paginated_data(path="/clientlessCertificate/issued", **kwargs, api_version="v2")
#         return list

#     def list_all_certificates(self, **kwargs) -> BoxList:
#         """
#         Returns a list of all Browser Access certificates.

#         Args:
#             **kwargs: Optional keyword args.

#         Keyword Args:
#             **max_items (int, optional):
#                 The maximum number of items to request before stopping iteration.
#             **max_pages (int, optional):
#                 The maximum number of pages to request before stopping iteration.
#             **pagesize (int, optional):
#                 Specifies the page size. The default size is 20, but the maximum size is 500.
#             **search (str, optional):
#                 The search string used to match against features and fields.

#         Returns:
#             :obj:`BoxList`: List of all Browser Access certificates.

#         Examples:
#             >>> for cert in zpa.certificates.list_all_certificates():
#             ...    print(cert)

#         """
#         list, _ = self.rest.get_paginated_data(path="/certificate", **kwargs, api_version="v1")
#         return list

#     def get_certificate_by_name(self, name: str, **kwargs) -> Box:
#         """
#         Returns information on the certificate with the specified name.

#         Args:
#             name (str): The name of the certificate.

#         Returns:
#             :obj:`Box` or None: The resource record for the certificate if found, otherwise None.

#         Examples:
#             >>> certificate = zpa.certificates.get_certificate_by_name('example_name')
#             >>> if certificate:
#             ...     pprint(certificate)
#             ... else:
#             ...     print("Certificate not found")

#         """
#         certs = self.list_all_certificates(**kwargs)
#         for cert in certs:
#             if cert.get("name") == name:
#                 return cert
#         return None

#     def get_certificate(self, certificate_id: str, **kwargs) -> Box:
#         """
#         Returns information on a specified Browser Access certificate.

#         Args:
#             certificate_id (str):
#                 The unique identifier for the Browser Access certificate.

#         Returns:
#             :obj:`Box`:
#                 The Browser Access certificate resource record.

#         Examples:
#             >>> ba_certificate = zpa.certificates.get_certificate('99999')

#         """
#         params = {}
#         if "microtenant_id" in kwargs:
#             params["microtenantId"] = kwargs.pop("microtenant_id")
#         return self.rest.get(f"clientlessCertificate/{certificate_id}", params=params)

#     def add_certificate(self, name: str, cert_blob: str, **kwargs) -> Box:
#         """
#         Add a new Certificate.

#         Args:
#             name (str): The name of the certificate.
#             cert_blob (str): The content of the certificate. Must include the certificate and private key (in PEM format).
#             **kwargs: Optional keyword args.

#         Keyword Args:
#             description (str): The description of the certificate.

#         Returns:
#             :obj:`Box`: The resource record for the newly created server.

#         Examples:
#             Create a certificate with minimum required parameters:

#             >>> zpa.certificates.add_certificate(
#             ...   name='myserver.example',
#             ...   cert_blob=-----BEGIN CERTIFICATE-----\\n"
#             ...              "MIIFNzCCBIHNIHIO==\\n"
#             ...              "-----END CERTIFICATE-----"),
#             )
#         """
#         payload = {"name": name, "certBlob": cert_blob}

#         for key, value in kwargs.items():
#             payload[snake_to_camel(key)] = value

#         microtenant_id = kwargs.pop("microtenant_id", None)
#         params = {"microtenantId": microtenant_id} if microtenant_id else {}

#         response = self.rest.post("/certificate", json=payload, params=params)
#         if isinstance(response, Response):
#             status_code = response.status_code
#             if status_code > 299:
#                 return None
#         return self.get_certificate(response.get("id"))

#     def delete_certificate(self, certificate_id: str, **kwargs) -> Box:
#         """
#         Returns information on a specified Browser Access certificate.

#         Args:
#             certificate_id (str):
#                 The unique identifier for the Browser Access certificate.

#         Returns:
#             :obj:`Box`:
#                 The Browser Access certificate resource record.

#         Examples:
#             >>> ba_certificate = zpa.certificates.delete_certificate('99999')

#         """
#         params = {}
#         if "microtenant_id" in kwargs:
#             params["microtenantId"] = kwargs.pop("microtenant_id")
#         return self.rest.delete(f"certificate/{certificate_id}", params=params).status_code
