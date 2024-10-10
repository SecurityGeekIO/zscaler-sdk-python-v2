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
from zscaler.zia.models.workload_groups import WorkloadGroups
from zscaler.utils import format_url
from urllib.parse import urlencode

class WorkloadGroupsAPI(APIClient):
    """
    A Client object for the Workload Groups API resource.
    """

    def __init__(self):
        super().__init__()
        self._base_url = ""

    def list_groups(
            self, query_params=None,
            keep_empty_params=False
    ) -> tuple:
        """
        Returns the list of workload groups configured in the ZIA Admin Portal.

        Args:
            query_params {dict}: Map of query parameters for the request.
                [query_params.page] {int}: Specifies the page offset.
                [query_params.pagesize] {int}: Specifies the page size. The default size is 100, but the maximum size is 1000.
                [query_params.max_items] {int}: Maximum number of items to fetch before stopping.
                [query_params.max_pages] {int}: Maximum number of pages to request before stopping.
            keep_empty_params {bool}: Whether to include empty parameters in the query string.

        Returns:
            tuple: A tuple containing (list of WorkloadGroups instances, Response, error)


        Examples:
            >>> for workloads in zia.workload_groups.list_groups():
            ...    pprint(workloads)

        """
        http_method = "get".upper()
        api_url = format_url(f"{self._base_url}/zia/api/v1/workloadGroups")

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
        response, error = self._request_executor.execute(request, WorkloadGroups)

        if error:
            return (None, response, error)

        # Parse the response into AdminUser instances
        try:
            result = []
            for item in response.get_body():
                result.append(WorkloadGroups(
                    self.form_response_body(item)
                ))
        except Exception as error:
            return (None, response, error)

        return (result, response, None)
