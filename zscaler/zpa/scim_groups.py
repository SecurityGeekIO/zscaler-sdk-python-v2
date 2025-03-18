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
from zscaler.zpa.models.scim_groups import SCIMGroup
from zscaler.utils import format_url


class SCIMGroupsAPI(APIClient):
    """
    A client object for the SCIM Groups resource.
    """

    def __init__(self, request_executor, config):
        super().__init__()
        self._request_executor: RequestExecutor = request_executor
        customer_id = config["client"].get("customerId")
        self._zpa_base_endpoint_userconfig = f"/zpa/userconfig/v1/customers/{customer_id}"

    def list_scim_groups(self, idp_id: str, query_params=None) -> tuple:
        """
        Returns a list of all configured SCIM groups for the specified IdP.

        Args:
            idp_id (str):
                The unique id of the IdP.

        Keyword Args:
            query_params {dict}: Map of query parameters for the request.
 
                ``[query_params.page]`` (str): Specifies the page number. Default value : 1
                ``[query_params.page_size]`` (str): Specifies the page size. The default size is 20, but the maximum size is 500.
                ``[query_params.end_time]`` (str):
                    The end of a time range for requesting last updated data (modified_time) for the SCIM group.
                    This requires setting the ``start_time`` parameter as well.
                ``[query_params.start_time]`` (str):
                    The start of a time range for requesting last updated data (modified_time) for the SCIM group.
                    This requires setting the ``end_time`` parameter as well.
                ``[query_params.idp_group_id]`` (str): The unique id of the IdP group.
                ``[query_params.scim_user_id]`` (str): The unique id for the SCIM user.
                ``[query_params.scim_user_name]`` (str): Name of the SCIM user.
                ``[query_params.search]`` (str): The search string used to match against features and fields.
                ``[query_params.sort_order]`` (str):
                    Sort the last updated time (modified_time) by ascending ``ASC`` or descending ``DSC`` order. Defaults to
                    ``DSC``.
                ``[query_params.sort_by]`` (str):
                    Specifies the field name to sort the results. Supported Sort fields are (id, name, creation_time, modified_time).
                    If not provided, results are sorted by modified_time
                ``[query_params.all_entries]`` (bool): Return all SCIM groups including the deleted ones if set to true
                    Default value : false
                    
        Returns:
            list: A list of SCIM Group instances.

        Examples:
            >>> for scim_group in zpa.scim_groups.list_scim_groups("999999"):
            ...    pprint(scim_group)
        """
        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._zpa_base_endpoint_userconfig}
            /scimgroup/idpId/{idp_id}
        """
        )

        query_params = query_params or {}

        body = {}
        headers = {}

        request, error = self._request_executor\
            .create_request(http_method, api_url, body, headers, params=query_params)
        if error:
            return (None, None, error)

        response, error = self._request_executor\
            .execute(request)
        if error:
            return (None, response, error)
    
        try:
            result = []
            for item in response.get_results():
                result.append(SCIMGroup(
                    self.form_response_body(item))
                )
        except Exception as error:
            return (None, response, error)
        return (result, response, None)

    def get_scim_group(self, group_id: str, query_params=None) -> tuple:
        """
        Returns information on the specified SCIM group.

        Args:
            group_id (str): The unique identifier for the SCIM group.

        Keyword Args:
            query_params {dict}: Map of query parameters for the request.
                ``[query_params.all_entries]`` (bool): Return all SCIM groups including the deleted ones if set to true
                    Default value : false

        Returns:
            SCIMGroup: The SCIMGroup resource object.

        Examples:
            >>> group = zpa.scim_groups.get_scim_group('99999')
        """
        http_method = "get".upper()
        api_url = format_url(
            f"""{
            self._zpa_base_endpoint_userconfig}
            /scimgroup/{group_id}
        """
        )

        query_params = query_params or {}

        request, error = self._request_executor.\
            create_request(http_method, api_url, params=query_params)
        if error:
            return (None, None, error)

        response, error = self._request_executor.\
            execute(request, SCIMGroup)
        if error:
            return (None, response, error)

        try:
            result = SCIMGroup(
                self.form_response_body(response.get_body())
            )
        except Exception as error:
            return (None, response, error)
        return (result, response, None)
