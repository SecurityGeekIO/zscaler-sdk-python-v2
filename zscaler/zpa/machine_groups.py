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
from zscaler.zpa.models.machine_groups import MachineGroup
from zscaler.utils import format_url
from zscaler.api_response import get_paginated_data
from urllib.parse import urlencode

class MachineGroupsAPI(APIClient):
    """
    A Client object for the Machine Groups resource.
    """

    def __init__(self):
        super().__init__()  # Inherit the request executor from APIClient
        self._base_url = ""

    def list_machine_groups(self, **kwargs) -> list:
        """
        Fetches all configured machine groups with pagination support.

        Keyword Args:
            max_items (int): The maximum number of items to request before stopping iteration.
            max_pages (int): The maximum number of pages to request before stopping iteration.
            pagesize (int): The page size, default is 20 and maximum is 500.
            search (str, optional): The search string used to match against features and fields.
            keep_empty_params (bool): Whether to include empty parameters in the query string.

        Returns:
            list: A list of `MachineGroup` instances.
        
        Example:
            >>> machine_groups = zpa.machine_groups.list_machine_groups(search="example")
        """
        api_url = f"/machineGroup"  # The relative endpoint path without base URL
        print(f"Requesting URL: {self._base_url}{api_url}")  # Debugging the constructed URL

        # Fetch paginated data using the request_executor
        list_data, error = get_paginated_data(
            request_executor=self._request_executor,
            path=api_url,  # Pass the relative path
            api_version="v1",  # Specify the API version for ZPA
            **kwargs  # Pass any additional pagination/filter params
        )

        if error:
            raise Exception(f"Error fetching machine groups data: {error}")

        if list_data:
            return [MachineGroup(group) for group in list_data]
        else:
            print("No machine groups found.")
            return []

    def get_group(self, group_id, query_params={}, keep_empty_params=False):
        """
        Fetches information on the specified machine group.

        Args:
            group_id (str): The ID of the machine group.
            query_params (dict): Optional query parameters for the request.

        Returns:
            dict: The machine group object.
        """

        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._base_url}
            /machineGroup/{group_id}
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

    def get_machine_group_by_name(self, name, query_params={}, keep_empty_params=False):
        """
        Fetches information on the machine group with the specified name.

        Args:
            name (str): The name of the machine group.
            query_params (dict): Optional query parameters for the request.

        Returns:
            dict or None: The machine group object if found, otherwise None.
        """
        groups, response, error = self.list_machine_groups(query_params, keep_empty_params)
        if error:
            return (None, response, error)

        for group in groups:
            if group.get("name") == name:
                return group, response, None

        return None, response, None


# from box import Box, BoxList
# from requests import Response

# from zscaler.api_client import APIClient


# class MachineGroupsAPI(APIClient):

#     def list_groups(self, **kwargs) -> BoxList:
#         """
#         Returns a list of all configured machine groups.

#         Keyword Args:
#             **max_items (int):
#                 The maximum number of items to request before stopping iteration.
#             **max_pages (int):
#                 The maximum number of pages to request before stopping iteration.
#             **pagesize (int):
#                 Specifies the page size. The default size is 20, but the maximum size is 500.
#             **search (str, optional):
#                 The search string used to match against features and fields.

#         Returns:
#             :obj:`list`: A list of all configured machine groups.

#         Examples:
#             >>> for machine_group in zpa.machine_groups.list_groups():
#             ...    pprint(machine_group)

#         """
#         list, _ = self.rest.get_paginated_data(path="/machineGroup", **kwargs)
#         return list

#     def get_group(self, group_id: str, **kwargs) -> Box:
#         """
#         Returns information on the specified machine group.

#         Args:
#             group_id (str):
#                 The unique identifier for the machine group.

#         Returns:
#             :obj:`Box`: The resource record for the machine group.

#         Examples:
#             >>> pprint(zpa.machine_groups.get_group('99999'))

#         """
#         params = {}
#         if "microtenant_id" in kwargs:
#             params["microtenantId"] = kwargs.pop("microtenant_id")
#         return self.rest.get(f"machineGroup/{group_id}", params=params)

#     def get_machine_group_by_name(self, name: str, **kwargs) -> Box:
#         """
#         Returns information on the machine group with the specified name.

#         Args:
#             name (str): The name of the machine group.

#         Returns:
#             :obj:`Box` or None: The resource record for the machine group if found, otherwise None.

#         Examples:
#             >>> group = zpa.machine_groups.get_machine_group_by_name('example_name')
#             >>> if group:
#             ...     pprint(group)
#             ... else:
#             ...     print("machine group not found")
#         """
#         apps = self.list_groups(**kwargs)
#         for app in apps:
#             if app.get("name") == name:
#                 return app
#         return None
