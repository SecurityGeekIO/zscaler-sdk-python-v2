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

from zscaler.request_executor import RequestExecutor
from zscaler.api_client import APIClient
from zscaler.ztw.models.nw_service_groups import NetworkServiceGroups
from zscaler.utils import format_url, transform_common_id_fields, reformat_params

class NWServiceGroupsAPI(APIClient):

    _ztw_base_endpoint = "/ztw/api/v1"

    def __init__(self, request_executor):
        super().__init__()
        self._request_executor: RequestExecutor = request_executor
        
    def list_network_svc_groups(
        self,
        query_params=None,
    ) -> tuple:
        """
        Lists network service groups in your organization with pagination.
        A subset of network service groups can be returned that match a supported
        filter expression or query.

        Args:
            query_params {dict}: Map of query parameters for the request.
                ``[query_params.search]`` {str}: The search string used to match against a group's name or description attributes.

        Returns:
            tuple: List of Network Service Group resource records.

        Examples:
            Gets a list of all network services group.
            
            >>> group_list, response, error = zia.cloud_firewall.list_network_svc_groups():
            ... if error:
            ...     print(f"Error listing network services group: {error}")
            ...     return
            ... print(f"Total groups found: {len(group_list)}")
            ... for group in group_list:
            ...     print(group.as_dict())
            
            Gets a list of all network services group.
            
            >>> group_list, response, error = zia.cloud_firewall.list_network_svc_groups(query_params={"search": 'Group01'}):
            ... if error:
            ...     print(f"Error listing network services group: {error}")
            ...     return
            ... print(f"Total groups found: {len(group_list)}")
            ... for group in group_list:
            ...     print(group.as_dict())

        """
        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._ztw_base_endpoint}
            /networkServiceGroups
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
                result.append(NetworkServiceGroups(
                    self.form_response_body(item))
                )
        except Exception as error:
            return (None, response, error)

        return (result, response, None)

    def list_network_svc_groups_lite(
        self,
        query_params=None,
    ) -> tuple:
        """
        Lists Network Service Groups name and ID  all network service groups.
        If the `search` parameter is provided, the function filters the rules client-side.

        Args:
            query_params (dict): Map of query parameters for the request.
                ``[query_params.search]`` (str): Search string for filtering results.

        Returns:
            tuple:
                A tuple containing (list of network service groups instances, Response, error).

        Examples:
            Gets a list of all network services group.
            
            >>> group_list, response, error = zia.cloud_firewall.list_network_svc_groups():
            ... if error:
            ...     print(f"Error listing network services group: {error}")
            ...     return
            ... print(f"Total groups found: {len(group_list)}")
            ... for group in group_list:
            ...     print(group.as_dict())
            
            Gets a list of all network services group.
            
            >>> group_list, response, error = zia.cloud_firewall.list_network_svc_groups(query_params={"search": 'Group01'}):
            ... if error:
            ...     print(f"Error listing network services group: {error}")
            ...     return
            ... print(f"Total groups found: {len(group_list)}")
            ... for group in group_list:
            ...     print(group.as_dict())

        """
        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._ztw_base_endpoint}
            /networkServiceGroups/lite
        """
        )

        query_params = query_params or {}

        local_search = query_params.pop("search", None)

        body = {}
        headers = {}

        request, error = self._request_executor.\
            create_request(
            http_method,
            api_url,
            body,
            headers,
            params=query_params
        )
        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request)
        if error:
            return (None, response, error)

        try:
            results = []
            for item in response.get_results():
                results.append(NetworkServiceGroups(
                    self.form_response_body(item))
                )
        except Exception as exc:
            return (None, response, exc)

        if local_search:
            lower_search = local_search.lower()
            results = [
                r for r in results
                if lower_search in (r.name.lower() if r.name else "")
            ]

        return (results, response, None)

    def get_network_svc_group(self, group_id: int) -> tuple:
        """
        Returns information for the specified Network Service Group.

        Args:
            group_id (str): The unique ID for the Network Service Group.

        Examples:
            >>> fetched_group, response, error = client.zia.cloud_firewall.get_network_svc_group('18382907')
            ... if error:
            ...     print(f"Error fetching group by ID: {error}")
            ...     return
            ... print(f"Fetched group by ID: {fetched_group.as_dict()}")

        """
        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._ztw_base_endpoint}
            /networkServiceGroups/{group_id}
        """
        )

        body = {}
        headers = {}

        request, error = self._request_executor\
            .create_request(http_method, api_url, body, headers)

        if error:
            return (None, None, error)

        response, error = self._request_executor\
            .execute(request, NetworkServiceGroups)

        if error:
            return (None, response, error)

        try:
            result = NetworkServiceGroups(
                self.form_response_body(response.get_body())
            )
        except Exception as error:
            return (None, response, error)

        return (result, response, None)

    def add_network_svc_group(
        self,
        **kwargs
    ) -> tuple:
        """
        Adds a new Network Service Group.

        Args:
            name (str): The name of the Network Service Group.
            service_ids (list): A list of Network Service IDs to add to the group.
            description (str): Additional information about the Network Service Group.

        Returns:
            :obj:`Tuple`: The newly created Network Service Group resource record.

        Examples:
            Add a new Network Service Group:

            >>> zia.cloud_firewall.add_network_svc_group(name='New Network Service Group',
            ...    service_ids=['159143', '159144', '159145'],
            ...    description='Group for the new Network Service.')

        """
        http_method = "post".upper()
        api_url = format_url(
            f"""
            {self._ztw_base_endpoint}
            /networkServiceGroups
        """
        )

        body = kwargs

        transform_common_id_fields(reformat_params, body, body)
        
        request, error = self._request_executor\
            .create_request(
            method=http_method,
            endpoint=api_url,
            body=body,
        )

        if error:
            return (None, None, error)

        # Execute the request
        response, error = self._request_executor\
            .execute(request, NetworkServiceGroups)

        if error:
            return (None, response, error)

        try:
            result = NetworkServiceGroups(
                self.form_response_body(response.get_body())
            )
        except Exception as error:
            return (None, response, error)
        return (result, response, None)

    def update_network_svc_group(
        self,
        group_id: int,
        **kwargs
    ) -> tuple:
        """
        Update a Network Service Group.

        Args:
            group_id (str): The unique ID of the Network Service Group.
            **kwargs: Optional keyword args.

        Keyword Args:
            name (str): The name of the Network Service Group.
            service_ids (list): A list of Network Service IDs to add to the group.
            description (str): Additional information about the Network Service Group.

        Returns:
            :obj:`Tuple`: The updated Network Service Group resource record.

        Examples:
            Update the name Network Service Group:

            >>> zia.cloud_firewall.update_network_svc_group(name='Update Network Service Group',
            ...    service_ids=['159143', '159144', '159145'],
            ...    description='Group for the new Network Service.')

        """
        http_method = "put".upper()
        api_url = format_url(
            f"""
            {self._ztw_base_endpoint}
            /networkServiceGroups/{group_id}
        """
        )

        body = kwargs

        transform_common_id_fields(reformat_params, body, body)

        # Create the request
        request, error = self._request_executor\
            .create_request(
            method=http_method,
            endpoint=api_url,
            body=body,
        )

        response, error = self._request_executor\
            .execute(request, NetworkServiceGroups)
        if error:
            return (None, response, error)

        try:
            result = NetworkServiceGroups(
                self.form_response_body(response.get_body())
            )
        except Exception as error:
            return (None, response, error)
        return (result, response, None)

    def delete_network_svc_group(
        self,
        group_id: int,
    ) -> tuple:
        """
        Deletes the specified Network Service Group.

        Args:
            group_id (str): The unique identifier for the Network Service Group.

        Returns:
            :obj:`int`: The response code for the operation.

        Examples:
            >>> _, response, error = client.zia.cloud_firewall.delete_network_svc_group(updated_group.id)
            ... if error:
            ...     print(f"Error deleting group: {error}")
            ... return

        """
        http_method = "delete".upper()
        api_url = format_url(
            f"""
            {self._ztw_base_endpoint}
            /networkServiceGroups/{group_id}
        """
        )

        params = {}

        request, error = self._request_executor\
            .create_request(http_method, api_url, params=params)
        if error:
            return (None, None, error)

        response, error = self._request_executor\
            .execute(request)
        if error:
            return (None, response, error)
        return (None, response, None)