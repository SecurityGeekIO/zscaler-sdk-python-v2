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


from box import Box, BoxList
from requests import Response


from zscaler.api_client import APIClient

class TrafficForwardingAPI(APIClient):
    """
    A Client object for the Traffic Forwarding resources.
    """

    _zia_base_endpoint = "/zia/api/v1"
    
    def __init__(self, request_executor):
        super().__init__()
        self._request_executor = request_executor

    def list_gre_tunnels(self, **kwargs) -> BoxList:
        """
        Returns the list of all configured GRE tunnels.

        Keyword Args:
            **max_items (int, optional):
                The maximum number of items to request before stopping iteration.
            **max_pages (int, optional):
                The maximum number of pages to request before stopping iteration.
            **page_size (int, optional):
                Specifies the page size. The default size is 100, but the maximum size is 1000.

        Returns:
            :obj:`BoxList`: A list of GRE tunnels configured in ZIA.

        Examples:
            List GRE tunnels with default settings:

            >>> for tunnel in zia.traffic.list_gre_tunnels():
            ...    print(tunnel)

            List GRE tunnels, limiting to a maximum of 10 items:

            >>> for tunnel in zia.traffic.list_gre_tunnels(max_items=10):
            ...    print(tunnel)

            List GRE tunnels, returning 200 items per page for a maximum of 2 pages:

            >>> for tunnel in zia.traffic.list_gre_tunnels(page_size=200, max_pages=2):
            ...    print(tunnel)

        """
        return BoxList(Iterator(self.rest, "greTunnels", **kwargs))

    def get_gre_tunnel(self, tunnel_id: str) -> tuple:
        """
        Returns information for the specified GRE tunnel.

        Args:
            tunnel_id (str):
                The unique identifier for the GRE tunnel.

        Returns:
            :obj:`tuple`: The GRE tunnel resource record.

        Examples:
            >>> gre_tunnel = zia.traffic.get_gre_tunnel('967134')

        """
        return self.rest.get(f"greTunnels/{tunnel_id}")

    def list_gre_ranges(self, **kwargs) -> BoxList:
        """
        Returns a list of available GRE tunnel ranges.

        Keyword Args:
            **internal_ip_range (str, optional):
                Internal IP range information.
            **static_ip (str, optional):
                Static IP information.
            **limit (int, optional):
                The maximum number of GRE tunnel IP ranges that can be added. Defaults to `10`.

        Returns:
            :obj:`BoxList`: A list of available GRE tunnel ranges.

        Examples:
            >>> gre_tunnel_ranges = zia.traffic.list_gre_ranges()

        """
        payload = {snake_to_camel(key): value for key, value in kwargs.items()}

        response = self.rest.get("greTunnels/availableInternalIpRanges", params=payload)
        if isinstance(response, Response):
            return None
        return response

    def list_vips_recommended(self, source_ip: str, **kwargs) -> BoxList:
        """
        Returns a list of recommended virtual IP addresses (VIPs) based on parameters.

        Args:
            source_ip (str):
                The source IP address.
            **kwargs:
                Optional keywords args.

        Keyword Args:
            routable_ip (bool):
                The routable IP address. Default: True.
            within_country_only (bool):
                Search within country only. Default: False.
            include_private_service_edge (bool):
                Include ZIA Private Service Edge VIPs. Default: True.
            include_current_vips (bool):
                Include currently assigned VIPs. Default: True.
            latitude (str):
                Latitude coordinate of GRE tunnel source.
            longitude (str):
                Longitude coordinate of GRE tunnel source.
            geo_override (bool):
                Override the geographic coordinates. Default: False.

        Returns:
            :obj:`BoxList`: List of VIP resource records.

        Examples:
            Return recommended VIPs for a given source IP:

            >>> for vip in zia.traffic.list_vips_recommende(source_ip='203.0.113.30'):
            ...    pprint(vip)

        """
        payload = {"sourceIp": source_ip}

        # Add optional parameters to payload
        for key, value in kwargs.items():
            payload[snake_to_camel(key)] = value

        response = self.rest.get("vips/recommendedList", params=payload, **kwargs)
        if isinstance(response, Response):
            return None
        return response

    def get_closest_diverse_vip_ids(self, ip_address: str) -> tuple:
        """
        Returns the closest diverse Zscaler destination VIPs for a given IP address.

        Args:
            ip_address (str):
                The IP address used for locating the closest diverse VIPs.

        Returns:
            :obj:`tuple`: Tuple containing the preferred and secondary VIP IDs.

        Examples:
            >>> closest_vips = zia.traffic.get_closest_diverse_vip_ids('203.0.113.20')

        """
        vips_list = self.list_vips_recommended(source_ip=ip_address)
        preferred_vip = vips_list[0]  # First entry is closest vip

        # Generator to find the next closest vip not in the same city as our preferred
        secondary_vip = next((vip for vip in vips_list if vip.city != preferred_vip.city))
        recommended_vips = (preferred_vip.id, secondary_vip.id)

        return recommended_vips

    def list_vip_group_by_dc(self, source_ip: str, **kwargs) -> BoxList:
        """
        Returns a list of recommended GRE tunnel (VIPs) grouped by data center.

        Args:
            source_ip (str):
                The source IP address.
            **kwargs:
                Optional keywords args.

        Keyword Args:
            routable_ip (bool):
                The routable IP address. Default: True.
            within_country_only (bool):
                Search within country only. Default: False.
            include_private_service_edge (bool):
                Include ZIA Private Service Edge VIPs. Default: True.
            include_current_vips (bool):
                Include currently assigned VIPs. Default: True.
            latitude (str):
                Latitude coordinate of GRE tunnel source.
            longitude (str):
                Longitude coordinate of GRE tunnel source.
            geo_override (bool):
                Override the geographic coordinates. Default: False.
        Returns:
            :obj:`BoxList`: List of VIP resource records.

        Examples:
            Return recommended VIPs for a given source IP:

            >>> for vip in zia.vips.list_vip_group_by_dc(source_ip='203.0.113.30'):
            ...    pprint(vip)

        """
        params = {"sourceIp": source_ip}

        for key, value in kwargs.items():
            params[snake_to_camel(key)] = value
        response = self.rest.get("/vips/groupByDatacenter", params=params)
        if response is not None:
            return response
        else:
            print("Failed to fetch VIP groups by data center. No response or error received.")
            return BoxList([])

    def list_vips(self, **kwargs) -> BoxList:
        """
        Returns a list of virtual IP addresses (VIPs) available in the Zscaler cloud.

        Keyword Args:
            **dc (str, optional):
                Filter based on data center.
            **include (str, optional):
                Include all, private, or public VIPs in the list. Available choices are `all`, `private`, `public`.
                Defaults to `public`.
            **max_items (int, optional):
                The maximum number of items to request before stopping iteration.
            **max_pages (int, optional):
                The maximum number of pages to request before stopping iteration.
            **page_size (int, optional):
                Specifies the page size. The default size is 100, but the maximum size is 1000.
            **region (str, optional):
                Filter based on region.

        Returns:
            :obj:`BoxList`: List of VIP resource records.

        Examples:
            List VIPs using default settings:

            >>> for vip in zia.vips.list_vips():
            ...    pprint(vip)

            List VIPs, limiting to a maximum of 10 items:

            >>> for vip in zia.vips.list_vips(max_items=10):
            ...    print(vip)

            List VIPs, returning 200 items per page for a maximum of 2 pages:

            >>> for vip in zia.traffic.list_vips(page_size=200, max_pages=2):
            ...    print(vip)

        """
        return BoxList(Iterator(self.rest, "vips", **kwargs))

    def add_gre_tunnel(
        self,
        source_ip: str,
        primary_dest_vip_id: str = None,
        secondary_dest_vip_id: str = None,
        **kwargs,
    ) -> tuple:
        """
        Add a new GRE tunnel.

        Note: If the `primary_dest_vip_id` and `secondary_dest_vip_id` aren't specified then the closest recommended
        VIPs will be automatically chosen.

        Args:
            source_ip (str):
                The source IP address of the GRE tunnel. This is typically a static IP address in the organisation
                or SD-WAN.
            primary_dest_vip_id (str):
                The unique identifier for the primary destination virtual IP address (VIP) of the GRE tunnel.
                Defaults to the closest recommended VIP.
            secondary_dest_vip_id (str):
                The unique identifier for the secondary destination virtual IP address (VIP) of the GRE tunnel.
                Defaults to the closest recommended VIP that isn't in the same city as the primary VIP.

        Keyword Args:
             **comment (str):
                Additional information about this GRE tunnel
             **ip_unnumbered (bool):
                This is required to support the automated SD-WAN provisioning of GRE tunnels, when set to true
                gre_tun_ip and gre_tun_id are set to null
             **internal_ip_range (str):
                The start of the internal IP address in /29 CIDR range.
             **within_country (bool):
                Restrict the data center virtual IP addresses (VIPs) only to those within the same country as the
                source IP address.

        Returns:
            :obj:`tuple`: The resource record for the newly created GRE tunnel.

        Examples:
            Add a GRE tunnel with closest recommended VIPs:

            >>> zia.traffic.add_gre_tunnel('203.0.113.10')

            Add a GRE tunnel with explicit VIPs:

            >>> zia.traffic.add_gre_tunnel('203.0.113.11',
            ...    primary_dest_vip_id='88088',
            ...    secondary_dest_vip_id='54590',
            ...    comment='GRE Tunnel for Manufacturing Plant')

        """

        # If primary/secondary VIPs not provided, add the closest diverse VIPs
        if primary_dest_vip_id is None and secondary_dest_vip_id is None:
            recommended_vips = self.get_closest_diverse_vip_ids(source_ip)
            primary_dest_vip_id = recommended_vips[0]
            secondary_dest_vip_id = recommended_vips[1]

        payload = {
            "sourceIp": source_ip,
            "primaryDestVip": {"id": primary_dest_vip_id},
            "secondaryDestVip": {"id": secondary_dest_vip_id},
        }

        # Add optional parameters to payload
        for key, value in kwargs.items():
            payload[snake_to_camel(key)] = value

        response = self.rest.post("greTunnels", json=payload)
        if isinstance(response, Response):
            # this is only true when the creation failed (status code is not 2xx)
            status_code = response.status_code
            # Handle error response
            raise Exception(f"API call failed with status {status_code}: {response.json()}")
        return response

    def update_gre_tunnel(
        self,
        tunnel_id: str,
        source_ip: str = None,
        primary_dest_vip_id: str = None,
        secondary_dest_vip_id: str = None,
        **kwargs,
    ) -> tuple:
        """
        Update an existing GRE tunnel.
        """

        if tunnel_id is None:
            raise ValueError("tunnel_id is a required parameter for updating a GRE tunnel.")

        # Determine VIPs based on source_ip if not provided
        if primary_dest_vip_id is None or secondary_dest_vip_id is None:
            recommended_vips = self.get_closest_diverse_vip_ids(source_ip)
            primary_dest_vip_id = primary_dest_vip_id or recommended_vips[0]
            secondary_dest_vip_id = secondary_dest_vip_id or recommended_vips[1]

        payload = {
            "sourceIp": source_ip,
            "primaryDestVip": {"id": primary_dest_vip_id},
            "secondaryDestVip": {"id": secondary_dest_vip_id},
        }

        # Include additional optional parameters
        for key, value in kwargs.items():
            payload[snake_to_camel(key)] = value

        response = self.rest.put(f"greTunnels/{tunnel_id}", json=payload)
        if isinstance(response, Response) and not response.ok:
            # Handle error response
            raise Exception(f"API call failed with status {response.status_code}: {response.json()}")
        # Return the updated object
        return self.get_gre_tunnel(tunnel_id)

    def delete_gre_tunnel(self, tunnel_id: str) -> int:
        """
        Delete the specified static IP.

        Args:
            static_ip_id (str):
                The unique identifier for the static IP.

        Returns:
            :obj:`int`: The response code for the operation.

        Examples:
            >>> zia.traffic.delete_gre_tunnel('972494')

        """

        return self.rest.delete(f"greTunnels/{tunnel_id}").status_code

