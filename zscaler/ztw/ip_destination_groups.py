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
from zscaler.ztw.models.ip_destination_groups import IPDestinationGroups
from zscaler.utils import format_url

class IPDestinationGroupsAPI(APIClient):

    _ztw_base_endpoint = "/ztw/api/v1"

    def __init__(self, request_executor):
        super().__init__()
        self._request_executor: RequestExecutor = request_executor
        
    def list_ip_destination_groups(
        self,
        exclude_type: str = None,
        query_params=None
    ) -> tuple:
        """
        Returns a list of IP Destination Groups.

        Args:
            query_params (dict):
                Map of query parameters for the request.

                ``[query_params.exclude_type]`` (str):
                    Exclude all groups that match the specified IP destination group's type.
                    Accepted values: ``DSTN_IP``, ``DSTN_FQDN``, ``DSTN_DOMAIN``, ``DSTN_OTHER``.

        Returns:
            tuple:
                A tuple containing (list of IPDestinationGroups instances, Response, error)

        Examples:
            Gets a list of all IP destination groups.
            
            >>> group_list, response, error = zia.cloud_firewall.list_ip_destination_groups():
            ... if error:
            ...     print(f"Error listing ip destination groups: {error}")
            ...     return
            ... print(f"Total groups found: {len(group_list)}")
            ... for group in group_list:
            ...     print(group.as_dict())
            
            Gets a list of all IP destination groups by excluding specific type.
            
            >>> group_list, response, error = zia.cloud_firewall.list_ip_destination_groups(query_params={"exclude_type": 'DSTN_DOMAIN'}):
            ... if error:
            ...     print(f"Error listing ip destination groups: {error}")
            ...     return
            ... print(f"Total groups found: {len(group_list)}")
            ... for group in group_list:
            ...     print(group.as_dict())

        """
        
        # Define supported values for exclude_type
        valid_exclude_types = {"DSTN_IP", "DSTN_FQDN", "DSTN_DOMAIN", "DSTN_OTHER"}

        # Validate exclude_type if provided
        if exclude_type and exclude_type not in valid_exclude_types:
            raise ValueError(f"Invalid exclude_type: {exclude_type}. \
                Supported values are: {', '.join(valid_exclude_types)}")

        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._ztw_base_endpoint}
            /ipDestinationGroups
        """
        )

        query_params = query_params or {}

        # Add excludeType to query_params if it's provided
        if exclude_type:
            query_params["excludeType"] = exclude_type

        # Prepare request body and headers
        body = {}
        headers = {}

        # Create the request
        request, error = self._request_executor\
            .create_request(http_method, api_url, body, headers, params=query_params)

        if error:
            return (None, None, error)

        # Execute the request
        response, error = self._request_executor\
            .execute(request)

        if error:
            return (None, response, error)

        # Parse the response into IPDestinationGroups instances
        try:
            result = []
            for item in response.get_results():
                result.append(IPDestinationGroups(
                    self.form_response_body(item))
                )
        except Exception as error:
            return (None, response, error)
        return (result, response, None)

    def list_ipv6_destination_groups(
        self, 
        exclude_type: str = None, 
        query_params=None
    ) -> tuple:
        """
        Lists IPv6 Destination Groups name and ID  all IPv6 Source Groups.
        `Note`: User-defined groups for IPv6 addresses are currently not supported, 
        so this endpoint retrieves only the predefined group that includes all IPv6 addresses.
        If the `search` parameter is provided, the function filters the rules client-side.

        Args:
            query_params (dict):
                Map of query parameters for the request.

                ``[query_params.exclude_type]`` (str):
                    Exclude all groups that match the specified IP destination group's type.
                    Accepted values: ``DSTN_IP``, ``DSTN_FQDN``, ``DSTN_DOMAIN``, ``DSTN_OTHER``.

        Returns:
            tuple:
                A tuple containing (list of IPDestinationGroups instances, Response, error)

        Examples:
            Gets a list of all IP destination groups.
            
            >>> group_list, response, error = zia.cloud_firewall.list_ipv6_destination_groups():
            ... if error:
            ...     print(f"Error listing ip destination groups: {error}")
            ...     return
            ... print(f"Total groups found: {len(group_list)}")
            ... for group in group_list:
            ...     print(group.as_dict())
            
            Gets a list of all IP destination groups by excluding specific type.
            
            >>> group_list, response, error = zia.cloud_firewall.list_ipv6_destination_groups(query_params={"exclude_type": 'DSTN_DOMAIN'}):
            ... if error:
            ...     print(f"Error listing ip destination groups: {error}")
            ...     return
            ... print(f"Total groups found: {len(group_list)}")
            ... for group in group_list:
            ...     print(group.as_dict())
        """
        
        # Define supported values for exclude_type
        valid_exclude_types = {"DSTN_IP", "DSTN_FQDN", "DSTN_DOMAIN", "DSTN_OTHER"}

        # Validate exclude_type if provided
        if exclude_type and exclude_type not in valid_exclude_types:
            raise ValueError(f"Invalid exclude_type: {exclude_type}. \
                Supported values are: {', '.join(valid_exclude_types)}")

        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._ztw_base_endpoint}
            /ipDestinationGroups/ipv6DestinationGroups
        """
        )

        query_params = query_params or {}

        # Add excludeType to query_params if it's provided
        if exclude_type:
            query_params["excludeType"] = exclude_type

        # Prepare request body and headers
        body = {}
        headers = {}

        # Create the request
        request, error = self._request_executor\
            .create_request(http_method, api_url, body, headers, params=query_params)

        if error:
            return (None, None, error)

        # Execute the request
        response, error = self._request_executor\
            .execute(request)

        if error:
            return (None, response, error)

        try:
            result = []
            for item in response.get_results():
                result.append(IPDestinationGroups(
                    self.form_response_body(item))
                )
        except Exception as error:
            return (None, response, error)
        return (result, response, None)
    
    def list_ip_destination_groups_lite(
        self, 
        exclude_type: str = None, 
        query_params=None
    ) -> tuple:
        """
        Lists IP Destination Groups name and ID  all IP Destination Groups.
        This endpoint retrieves only IPv4 destination address groups.
        If the `search` parameter is provided, the function filters the rules client-side.

        Args:
            query_params (dict):
                Map of query parameters for the request.

                ``[query_params.exclude_type]`` (str):
                    Exclude all groups that match the specified IP destination group's type.
                    Accepted values: ``DSTN_IP``, ``DSTN_FQDN``, ``DSTN_DOMAIN``, ``DSTN_OTHER``.

        Returns:
            tuple: List of IP Destination Groups resource records.

        Examples:
            Gets a list of all IP destination groups.
            
            >>> group_list, response, error = zia.cloud_firewall.list_ip_destination_groups_lite():
            ... if error:
            ...     print(f"Error listing ip destination groups: {error}")
            ...     return
            ... print(f"Total groups found: {len(group_list)}")
            ... for group in group_list:
            ...     print(group.as_dict())
            
            Gets a list of all IP destination groups by excluding specific type.
            
            >>> group_list, response, error = zia.cloud_firewall.list_ip_destination_groups_lite(query_params={"exclude_type": 'DSTN_DOMAIN'}):
            ... if error:
            ...     print(f"Error listing ip destination groups: {error}")
            ...     return
            ... print(f"Total groups found: {len(group_list)}")
            ... for group in group_list:
            ...     print(group.as_dict())

        """
        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._ztw_base_endpoint}
            /ipDestinationGroups/lite
        """
        )

        # Define supported values for exclude_type
        valid_exclude_types = {"DSTN_IP", "DSTN_FQDN", "DSTN_DOMAIN", "DSTN_OTHER"}

        # Validate exclude_type if provided
        if exclude_type and exclude_type not in valid_exclude_types:
            raise ValueError(f"Invalid exclude_type: {exclude_type}. \
                Supported values are: {', '.join(valid_exclude_types)}")

        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._ztw_base_endpoint}
            /ipDestinationGroups
        """
        )

        query_params = query_params or {}

        # Add excludeType to query_params if it's provided
        if exclude_type:
            query_params["excludeType"] = exclude_type

        # Prepare request body and headers
        body = {}
        headers = {}

        # Create the request
        request, error = self._request_executor\
            .create_request(http_method, api_url, body, headers, params=query_params)

        if error:
            return (None, None, error)

        # Execute the request
        response, error = self._request_executor\
            .execute(request)

        if error:
            return (None, response, error)

        # Parse the response into IPDestinationGroups instances
        try:
            result = []
            for item in response.get_results():
                result.append(IPDestinationGroups(
                    self.form_response_body(item))
                )
        except Exception as error:
            return (None, response, error)
        return (result, response, None)

    def list_ipv6_destination_groups_lite(
        self, 
        exclude_type: str = None, 
        query_params=None
    ) -> tuple:
        """
        Lists IPv6 Destination Groups name and ID  all IPv6 Source Groups.
        `Note`: User-defined groups for IPv6 addresses are currently not supported, 
        so this endpoint retrieves only the predefined group that includes all IPv6 addresses.
        If the `search` parameter is provided, the function filters the rules client-side.

        Args:
            query_params (dict):
                Map of query parameters for the request.

                ``[query_params.exclude_type]`` (str):
                    Exclude all groups that match the specified IP destination group's type.
                    Accepted values: ``DSTN_IP``, ``DSTN_FQDN``, ``DSTN_DOMAIN``, ``DSTN_OTHER``.

        Returns:
            tuple: List of IP Destination Groups resource records.

        Examples:
            Gets a list of all IP destination groups.
            
            >>> group_list, response, error = zia.cloud_firewall.list_ipv6_destination_groups_lite():
            ... if error:
            ...     print(f"Error listing ip destination groups: {error}")
            ...     return
            ... print(f"Total groups found: {len(group_list)}")
            ... for group in group_list:
            ...     print(group.as_dict())
            
            Gets a list of all IP destination groups by excluding specific type.
            
            >>> group_list, response, error = zia.cloud_firewall.list_ipv6_destination_groups_lite(query_params={"exclude_type": 'DSTN_DOMAIN'}):
            ... if error:
            ...     print(f"Error listing ip destination groups: {error}")
            ...     return
            ... print(f"Total groups found: {len(group_list)}")
            ... for group in group_list:
            ...     print(group.as_dict())

        """
        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._ztw_base_endpoint}
            /ipDestinationGroups/ipv6DestinationGroups/lite
        """
        )

        # Define supported values for exclude_type
        valid_exclude_types = {"DSTN_IP", "DSTN_FQDN", "DSTN_DOMAIN", "DSTN_OTHER"}

        # Validate exclude_type if provided
        if exclude_type and exclude_type not in valid_exclude_types:
            raise ValueError(f"Invalid exclude_type: {exclude_type}. \
                Supported values are: {', '.join(valid_exclude_types)}")

        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._ztw_base_endpoint}
            /ipDestinationGroups
        """
        )

        query_params = query_params or {}

        # Add excludeType to query_params if it's provided
        if exclude_type:
            query_params["excludeType"] = exclude_type

        # Prepare request body and headers
        body = {}
        headers = {}

        # Create the request
        request, error = self._request_executor\
            .create_request(http_method, api_url, body, headers, params=query_params)

        if error:
            return (None, None, error)

        # Execute the request
        response, error = self._request_executor\
            .execute(request)

        if error:
            return (None, response, error)

        try:
            result = []
            for item in response.get_results():
                result.append(IPDestinationGroups(
                    self.form_response_body(item))
                )
        except Exception as error:
            return (None, response, error)
        return (result, response, None)

    def get_ip_destination_group(self, group_id: int) -> tuple:
        """
        Returns information on the specified IP Destination Group.

        Args:
            group_id (str): The unique ID of the IP Destination Group.

        Returns:
            tuple: The IP Destination Group resource record.

        Examples:
            >>> fetched_group, response, error = client.zia.cloud_firewall.get_ip_destination_group('18382907')
            ... if error:
            ...     print(f"Error fetching group by ID: {error}")
            ...     return
            ... print(f"Fetched group by ID: {fetched_group.as_dict()}")

        """
        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._ztw_base_endpoint}
            /ipDestinationGroups/{group_id}
        """
        )

        body = {}
        headers = {}

        request, error = self._request_executor\
            .create_request(http_method, api_url, body, headers)

        if error:
            return (None, None, error)

        response, error = self._request_executor\
            .execute(request, IPDestinationGroups)

        if error:
            return (None, response, error)

        try:
            result = IPDestinationGroups(
                self.form_response_body(response.get_body())
            )
        except Exception as error:
            return (None, response, error)
        return (result, response, None)

    def add_ip_destination_group(self, **kwargs) -> tuple:
        """
        Adds a new IP Destination Group.

        Args:
            name (str): The name of the IP Destination Group.
            **kwargs: Optional keyword args.

        Keyword Args:
            type (str): Destination IP group type. Allowed values are DSTN_IP and DSTN_FQDN.
            addresses (list): Destination IP addresses or FQDNs within the group.
            description (str): Additional information about the destination IP group.
            ip_categories (list): Destination IP address URL categories.
            countries (list): Destination IP address counties.

        Returns:
            :obj:`Tuple`: The newly created IP Destination Group resource record.

        Examples:
            Add a Destination IP Group with IP addresses:

            >>> zia.cloud_firewall.add_ip_destination_group(name='Destination Group - IP',
            ...    addresses=['203.0.113.0/25', '203.0.113.131'],
            ...    type='DSTN_IP')

            Add a Destination IP Group with FQDN:

            >>> zia.cloud_firewall.add_ip_destination_group(name='Destination Group - FQDN',
            ...    description='Covers domains for Example Inc.',
            ...    addresses=['example.com', 'example.edu'],
            ...    type='DSTN_FQDN')

            Add a Destionation IP Group for the US:

            >>> zia.cloud_firewall.add_ip_destination_group(name='Destination Group - US',
            ...    description='Covers the US',
            ...    countries=['COUNTRY_US'])

        """
        http_method = "post".upper()
        api_url = format_url(
            f"""
            {self._ztw_base_endpoint}
            /ipDestinationGroups
        """
        )

        body = kwargs

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
            .execute(request, IPDestinationGroups)

        if error:
            return (None, response, error)

        try:
            result = IPDestinationGroups(
                self.form_response_body(response.get_body())
            )
        except Exception as error:
            return (None, response, error)
        return (result, response, None)

    def update_ip_destination_group(
        self,
        group_id: str,
        **kwargs
    ) -> tuple:
        """
        Updates the specified IP Destination Group.

        Args:
            group_id (str): The unique ID of the IP Destination Group.
            **kwargs: Optional keyword args.

        Keyword Args:
            name (str): The name of the IP Destination Group.
            addresses (list): Destination IP addresses or FQDNs within the group.
            description (str): Additional information about the IP Destination Group.
            ip_categories (list): Destination IP address URL categories.
            countries (list): Destination IP address countries.

        Returns:
            :obj:`Tuple`: The updated IP Destination Group resource record.

        Examples:
            Update the name of an IP Destination Group:

            >>> zia.cloud_firewall.update_ip_destination_group('9032667',
            ...    name="Updated IP Destination Group")

            Update the description and FQDNs for an IP Destination Group:

            >>> zia.cloud_firewall.update_ip_destination_group('9032668',
            ...    description="Tech News",
            ...    addresses=['arstechnica.com', 'slashdot.org'])

        """
        http_method = "put".upper()
        api_url = format_url(
            f"""
            {self._ztw_base_endpoint}
            /ipDestinationGroups/{group_id}
        """
        )

        body = {}

        body.update(kwargs)

        # Create the request
        request, error = self._request_executor\
            .create_request(http_method, api_url, body, {}, {})
        if error:
            return (None, None, error)

        # Execute the request
        response, error = self._request_executor\
            .execute(request, IPDestinationGroups)
        if error:
            return (None, response, error)

        try:
            result = IPDestinationGroups(
                self.form_response_body(response.get_body())
            )
        except Exception as error:
            return (None, response, error)
        return (result, response, None)

    def delete_ip_destination_group(self, group_id: int) -> tuple:
        """
        Deletes the specified IP Destination Group.

        Args:
            group_id (str): The unique ID of the IP Destination Group.

        Returns:
            :obj:`int`: The status code of the operation.

        Examples:
            >>> _, response, error = client.zia.cloud_firewall.delete_ip_destination_group(updated_group.id)
            ... if error:
            ...     print(f"Error deleting group: {error}")
            ... return

        """
        http_method = "delete".upper()
        api_url = format_url(
            f"""
            {self._ztw_base_endpoint}
            /ipDestinationGroups/{group_id}
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
