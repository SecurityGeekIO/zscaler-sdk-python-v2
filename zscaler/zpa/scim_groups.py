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
from zscaler.zpa.models.scim_groups import SCIMGroup
from zscaler.api_response import get_paginated_data
from zscaler.utils import format_url


class SCIMGroupsAPI(APIClient):
    """
    A client object for the SCIM Groups resource.
    """

    def __init__(self):
        super().__init__()
        self._base_url = ""

    def list_groups(self, idp_id: str, **kwargs) -> list:
        """
        Returns a list of all configured SCIM groups for the specified IdP.

        Args:
            idp_id (str):
                The unique id of the IdP.
            sort_by (str):
                The field name to sort by, supported values: id, name, creationTime or modifiedTime (default to name)
            sort_order (str):
                The sort order, values: ASC or DSC (default DSC)

        Keyword Args:
            **end_time (str):
                The end of a time range for requesting last updated data (modified_time) for the SCIM group.
                This requires setting the ``start_time`` parameter as well.
            **idp_group_id (str):
                The unique id of the IdP group.
            **max_items (int):
                The maximum number of items to request before stopping iteration.
            **max_pages (int):
                The maximum number of pages to request before stopping iteration.
            **pagesize (int):
                Specifies the page size. The default size is 20, but the maximum size is 500.
            **scim_user_id (str):
                The unique id for the SCIM user.
            **search (str, optional):
                The search string used to match against features and fields.
            **sort_order (str):
                Sort the last updated time (modified_time) by ascending ``ASC`` or descending ``DSC`` order. Defaults to
                ``DSC``.
            **start_time (str):
                The start of a time range for requesting last updated data (modified_time) for the SCIM group.
                This requires setting the ``end_time`` parameter as well.
            **keep_empty_params (bool): Whether to include empty parameters in the query string.

        Returns:
            list: A list of SCIMGroup instances.

        Examples:
            >>> for scim_group in zpa.scim_groups.list_groups("999999"):
            ...    pprint(scim_group)
        """
        api_url = format_url(f"{self._base_url}/scimgroup/idpId/{idp_id}", api_version="userconfig_v1")

        # Fetch paginated data using the get_paginated_data utility
        list_data, error = get_paginated_data(
            request_executor=self._request_executor,
            path=api_url, 
            **kwargs
        )

        if error:
            return None

        # Convert the raw data into SCIMGroup objects
        return [SCIMGroup(group) for group in list_data]


    def get_group(self, group_id: str, **kwargs) -> SCIMGroup:
        """
        Returns information on the specified SCIM group.

        Args:
            group_id (str): The unique identifier for the SCIM group.

        Returns:
            SCIMGroup: The SCIMGroup resource object.

        Examples:
            >>> group = zpa.scim_groups.get_group('99999')
        """
        api_url = format_url(f"{self._base_url}/scimgroup/{group_id}", api_version="userconfig_v1")

        # Fetch SCIM group data
        request, error = self._request_executor.create_request("get", api_url, params=kwargs)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        # Convert the response to SCIMGroup object
        return SCIMGroup(response.get_body())


# from box import Box, BoxList
# import time
# from zscaler.api_client import APIClient


# class SCIMGroupsAPI(APIClient):

#     def list_groups(self, idp_id: str, **kwargs) -> BoxList:
#         """
#         Returns a list of all configured SCIM groups for the specified IdP.

#         Args:
# idp_id (str):
#     The unique id of the IdP.
# sort_by (str):
#     The field name to sort by, supported values: id, name, creationTime or modifiedTime (default to name)
# sort_order (str):
#     The sort order, values: ASC or DSC (default DSC)


# Keyword Args:
#     **end_time (str):
#         The end of a time range for requesting last updated data (modified_time) for the SCIM group.
#         This requires setting the ``start_time`` parameter as well.
#     **idp_group_id (str):
#         The unique id of the IdP group.
#     **max_items (int):
#         The maximum number of items to request before stopping iteration.
#     **max_pages (int):
#         The maximum number of pages to request before stopping iteration.
#     **pagesize (int):
#         Specifies the page size. The default size is 20, but the maximum size is 500.
#     **scim_user_id (str):
#         The unique id for the SCIM user.
#     **search (str, optional):
#         The search string used to match against features and fields.
#     **sort_order (str):
#         Sort the last updated time (modified_time) by ascending ``ASC`` or descending ``DSC`` order. Defaults to
#         ``DSC``.
#     **start_time (str):
#         The start of a time range for requesting last updated data (modified_time) for the SCIM group.
#         This requires setting the ``end_time`` parameter as well.

#         Returns:
#             :obj:`list`: A list of all configured SCIM groups.

#         Examples:
#             >>> for scim_group in zpa.scim_groups.list_groups("999999"):
#             ...    pprint(scim_group)

#         """
#         list, _ = self.rest.get_paginated_data(
#             path=f"/scimgroup/idpId/{idp_id}",
#             **kwargs,
#             api_version="userconfig_v1",
#         )
#         return list

#     def get_group(self, group_id: str, **kwargs) -> Box:
#         """
#         Returns information on the specified SCIM group.

#         Args:
#             group_id (str):
#                 The unique identifier for the SCIM group.
#             **kwargs:
#                 Optional keyword args.

#         Returns:
#             :obj:`dict`: The resource record for the SCIM group.

#         Examples:
#             >>> pprint(zpa.scim_groups.get_group('99999'))

#         """
#         response = self.rest.get(f"/scimgroup/{group_id}", **kwargs, api_version="userconfig_v1")
#         return response
