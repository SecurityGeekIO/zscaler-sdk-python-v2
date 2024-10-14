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
from zscaler.zpa.models.trusted_network import TrustedNetwork
from zscaler.utils import format_url
from urllib.parse import urlencode


class TrustedNetworksAPI(APIClient):
    """
    A client object for the Trusted Networks resource.
    """

    def __init__(self, request_executor, config):
        super().__init__()
        self._request_executor = request_executor
        customer_id = config["client"].get("customerId")
        self._base_endpoint = f"/zpa/mgmtconfig/v1/admin/customers/{customer_id}"
        self._base_endpoint_v2 = f"/zpa/mgmtconfig/v1/admin/customers/{customer_id}"

    def list_trusted_networks(self, query_params=None, keep_empty_params=False) -> tuple:
        """
        Returns a list of all configured trusted networks.

        Keyword Args:
            max_items (int): The maximum number of items to request before stopping iteration.
            max_pages (int): The maximum number of pages to request before stopping iteration.
            pagesize (int): Specifies the page size. The default size is 20, but the maximum size is 500.
            search (str, optional): The search string used to match against features and fields.
            keep_empty_params (bool): Whether to include empty parameters in the query string.

        Returns:
            list: A list of `TrustedNetwork` instances.

        Example:
            >>> trusted_networks = zpa.trusted_networks.list_trusted_networks(search="example")
        """
        http_method = "get".upper()
        api_url = format_url(f"{self._base_endpoint_v2}/network")

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
        response, error = self._request_executor.execute(request, TrustedNetwork)

        if error:
            return (None, response, error)

        # Parse the response into AppConnectorGroup instances
        try:
            result = []
            for item in response.get_body():
                result.append(TrustedNetwork(self.form_response_body(item)))
        except Exception as error:
            return (None, response, error)

        return (result, response, None)

    def get_network(self, network_id: str) -> TrustedNetwork:
        """
        Returns information on the specified trusted network.

        Args:
            network_id (str): The unique identifier for the trusted network.

        Returns:
            TrustedNetwork: The corresponding trusted network object.
        """
        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._base_endpoint}/network/{network_id}
        """
        )

        # Create the request using RequestExecutor
        request, error = self._request_executor.create_request(http_method, api_url)

        if error:
            raise Exception(f"Error creating request: {error}")

        # Execute the request and get the response
        response, error = self._request_executor.execute(request)

        if error:
            raise Exception(f"API request failed: {error}")

        return TrustedNetwork(response.get_body())

    def get_network_by_name(self, name: str, **kwargs) -> TrustedNetwork:
        """
        Returns information on the trusted network with the specified name.

        Args:
            name (str): The name of the trusted network.

        Returns:
            TrustedNetwork or None: The resource record for the trusted network if found, otherwise None.
        """
        networks = self.list_trusted_networks(**kwargs)
        for network in networks:
            if network.name == name:
                return network
        return None

    def get_network_by_udid(self, network_udid: str, **kwargs) -> TrustedNetwork:
        """
        Returns a trusted network based on its 'network_udid'.

        Args:
            network_udid (str): The unique identifier for the network_udid of the trusted network.

        Returns:
            TrustedNetwork: The resource record for the trusted network, or None if not found.
        """
        networks = self.list_trusted_networks(**kwargs)
        for network in networks:
            if network.network_id == network_udid:
                return network
        return None
