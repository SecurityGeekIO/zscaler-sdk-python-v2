# -*- coding: utf-8 -*-

# Copyright (c) 2023, Zscaler Inc.
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

from zscaler.api_client import APIClient
from zscaler.utils import format_url
from urllib.parse import urlencode


class AuthDomainsAPI(APIClient):
    """
    A Client object for the Auth Domains resource.
    """

    def __init__(self, request_executor, config):
        super().__init__()
        self._request_executor = request_executor
        customer_id = config["client"].get("customerId")
        self._base_endpoint = f"/zpa/mgmtconfig/v1/admin/customers/{customer_id}"

    def get_auth_domains(self):
        """
        Returns information on authentication domains.

        Returns:
            tuple: A dictionary containing custom ZPA Inspection Control HTTP Methods.

        Example:
            >>> auth_domains, response, error = zpa.authdomains.get_auth_domains()
            >>> if error is None:
            ...     pprint(auth_domains)
        """
        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._base_endpoint}
            /authDomains
            """
        )

        body = {}
        headers = {}
        form = {}

        # Create the request
        request, error = self._request_executor.create_request(http_method, api_url, body, headers, form)

        if error:
            return (None, None, error)

        # Execute the request
        response, error = self._request_executor.execute(request, str)  # Expecting a list of strings

        if error:
            return (None, response, error)

        # Parse the response
        try:
            result = response.get_body()  # In this case, response is a list of strings like ["PASS", "BLOCK", "REDIRECT"]
        except Exception as error:
            return (None, response, error)

        return (result, response, None)


# from box import Box
# from zscaler.api_client import APIClient


# class AuthDomainsAPI(APIClient):

#     def get_auth_domains(self) -> Box:
#         """
#         Returns information on authentication domains.

#         Args:
#             group_id (str):
#                 The unique identifier for the authentication domains.

#         Returns:
#             :obj:`Box`: The resource record for the authentication domains.

#         Examples:
#             >>> pprint(zpa.authdomains.get_auth_domains())

#         """
#         return self.rest.get("authDomains")
