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
from zscaler.zpa.models.idp import IDP
from urllib.parse import urlencode
from zscaler.utils import format_url


class IDPControllerAPI(APIClient):
    """
    A Client object for the Identity Provider (IdP) resource.
    """

    def __init__(self):
        super().__init__()  # Inherit initialization from APIClient
        self._base_url = ""

    def list_idps(
            self, query_params=None,
            keep_empty_params=False
    ) -> tuple:
        """
        Enumerates identity provider in your organization with pagination.
        A subset of identity provider can be returned that match a supported
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
            tuple: A tuple containing (list of IDP instances, Response, error)
        """
        http_method = "get".upper()
        api_url = format_url(f"{self._base_url}/idp")

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
        response, error = self._request_executor.execute(request, IDP)

        if error:
            return (None, response, error)

        # Parse the response into IDP instances
        try:
            result = []
            for item in response.get_body():
                result.append(IDP(
                    self.form_response_body(item)
                ))
        except Exception as error:
            return (None, response, error)

        return (result, response, None)

    def get_idp(self, idp_id: str, **kwargs) -> IDP:
        """
        Returns information on the specified identity provider (IdP).

        Args:
            idp_id (str): The unique identifier for the identity provider.

        Returns:
            IDP: The corresponding identity provider object.
        """
        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._base_url}/idp/{idp_id}
        """
        )

        response, error = self._request_executor.execute(self._request_executor.create_request(http_method, api_url), IDP)

        if error:
            raise Exception(f"API request failed: {error}")

        return IDP(response.get_body())

    def get_idp_by_name(self, name: str, **kwargs) -> IDP:
        """
        Returns information on the identity provider with the specified name.

        Args:
            name (str): The name of the identity provider.

        Returns:
            IDP or None: The resource record for the identity provider if found, otherwise None.
        """
        idps = self.list_idps(**kwargs)
        for idp in idps:
            if idp.name == name:
                return idp
        return None


# from box import Box, BoxList
# from requests import Response

# from zscaler.api_client import APIClient


# class IDPControllerAPI(APIClient):

#     def list_idps(self, **kwargs) -> BoxList:
#         """
#         Returns a list of all configured IdPs.

#         Keyword Args:
#             **max_items (int):
#                 The maximum number of items to request before stopping iteration.
#             **max_pages (int):
#                 The maximum number of pages to request before stopping iteration.
#             **pagesize (int):
#                 Specifies the page size. The default size is 20, but the maximum size is 500.
#             **scim_enabled (bool):
#                 Returns all SCIM IdPs if ``True``. Returns all non-SCIM IdPs if ``False``.
#             **search (str, optional):
#                 The search string used to match against features and fields.

#         Returns:
#             :obj:`BoxList`: A list of all configured IdPs.

#         Examples:
#             >>> for idp in zpa.idp.list_idps():
#             ...    pprint(idp)

#         """
#         list, _ = self.rest.get_paginated_data(path="/idp", **kwargs, api_version="v2")
#         return list

#     def get_idp_by_name(self, name: str, **kwargs) -> Box:
#         """
#         Returns information on the identity provider with the specified name.

#         Args:
#             name (str): The name of the identity provider.

#         Returns:
#             :obj:`Box` or None: The resource record for the identity provider if found, otherwise None.

#         Examples:
#             >>> idp = zpa.idp.get_idp_by_name('example_name')
#             >>> if idp:
#             ...     pprint(idp)
#             ... else:
#             ...     print("identity provider not found")
#         """
#         idps = self.list_idps(**kwargs)
#         for idp in idps:
#             if idp.get("name") == name:
#                 return idp
#         return None

#     def get_idp(self, idp_id: str) -> Box:
#         """
#         Returns information on the specified IdP.

#         Args:
#             idp_id (str):
#                 The unique identifier for the IdP.

#         Returns:
#             :obj:`Box`: The resource record for the IdP.

#         Examples:
#             >>> pprint(zpa.idp.get_idp('99999'))

#         """
#         response = self.rest.get("/idp/%s" % (idp_id))
#         if isinstance(response, Response):
#             status_code = response.status_code
#             if status_code != 200:
#                 return None
#         return response
