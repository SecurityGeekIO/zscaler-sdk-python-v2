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

    def __init__(self):
        self._base_url = ""

    def get_auth_domains(self, query_params={}, keep_empty_params=False):
        """
        Returns information on authentication domains.

        Args:
            query_params (dict): Optional query parameters for the request.
            keep_empty_params (bool): Whether to include empty query parameters.

        Returns:
            dict: The resource record for the authentication domains.

        Example:
            >>> auth_domains, response, error = zpa.authdomains.get_auth_domains()
            >>> if error is None:
            ...     pprint(auth_domains)
        """
        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._base_url}
            /authDomains
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
