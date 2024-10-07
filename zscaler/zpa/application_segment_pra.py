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
from zscaler.zpa.models.application_segment_pra import ApplicationSegmentPRA
from urllib.parse import urlencode
from zscaler.utils import format_url, snake_to_camel, recursive_snake_to_camel, add_id_groups

class AppSegmentsPRAAPI(APIClient):
    """
    A client object for Application Segments PRA (Privileged Remote Access).
    """

    def __init__(self):
        super().__init__()
        self._base_url = ""
        
    def list_segments_pra(
            self, query_params=None,
            keep_empty_params=False
    ) -> tuple:
        """
        Enumerates application segment pra in your organization with pagination.
        A subset of application segment pra can be returned that match a supported
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
            tuple: A tuple containing (list of AppSegmentsPRA instances, Response, error)
        """
        # Initialize URL and HTTP method
        http_method = "get".upper()
        api_url = format_url(f"{self._base_url}/application")

        # Handle query parameters (including microtenant_id if provided)
        query_params = query_params or {}
        microtenant_id = query_params.pop("microtenant_id", None)
        if microtenant_id:
            query_params["microtenantId"] = microtenant_id

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
        response, error = self._request_executor.execute(request, ApplicationSegmentPRA)

        if error:
            return (None, response, error)

        # Parse the response into AppConnectorGroup instances
        try:
            result = []
            for item in response.get_body():
                result.append(ApplicationSegmentPRA(
                    self.form_response_body(item)
                ))
        except Exception as error:
            return (None, response, error)

        return (result, response, None)


    def get_segment_pra(self, segment_id: str, **kwargs) -> tuple:
        """
        Get details of an application segment by its ID.

        Args:
            segment_id (str): The unique ID for the application segment.

        Returns:
            tuple: A tuple containing (ApplicationSegment, Response, error)
        """
        http_method = "get".upper()
        api_url = format_url(f"{self._base_url}/application/{segment_id}")

        # Optional parameters such as microtenant_id
        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, params=params)
        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request)
        if error:
            return (None, response, error)

        result = ApplicationSegmentPRA(response.get_body())
        return (result, response, None)

    def add_segment_pra(
        self, name: str, 
        domain_names: list, 
        segment_group_id: str, 
        server_group_ids: list, 
        tcp_port_ranges: list = None,
        udp_port_ranges: list = None,
        common_apps_dto: dict = None,
        **kwargs) -> tuple:
        """
        Add a new application segment.

        Args:
            segment_group_id (str):
                The unique identifer for the segment group this application segment belongs to.
            udp_ports (:obj:`list` of :obj:`str`):
                List of udp port range pairs, e.g. ['35000', '35000'] for port 35000.
            tcp_ports (:obj:`list` of :obj:`str`):
                List of tcp port range pairs, e.g. ['22', '22'] for port 22-22, ['80', '100'] for 80-100.
            domain_names (:obj:`list` of :obj:`str`):
                List of domain names or IP addresses for the application segment.
            name (str):
                The name of the application segment.
            server_group_ids (:obj:`list` of :obj:`str`):
                The list of server group IDs that belong to this application segment.
            **kwargs:
                Optional keyword args.

        Keyword Args:
            bypass_type (str):
                The type of bypass for the Application Segment. Accepted values are `ALWAYS`, `NEVER` and `ON_NET`.
            config_space (str):
                The config space for this Application Segment. Accepted values are `DEFAULT` and `SIEM`.
            default_idle_timeout (int):
                The Default Idle Timeout for the Application Segment.
            default_max_age (int):
                The Default Max Age for the Application Segment.
            description (str):
                Additional information about this Application Segment.
            double_encrypt (bool):
                Double Encrypt the Application Segment micro-tunnel.
            enabled (bool):
                Enable the Application Segment.
            health_check_type (str):
                Set the Health Check Type. Accepted values are `DEFAULT` and `NONE`.
            health_reporting (str):
                Set the Health Reporting. Accepted values are `NONE`, `ON_ACCESS` and `CONTINUOUS`.
            ip_anchored (bool):
                Enable IP Anchoring for this Application Segment.
            is_cname_enabled (bool):
                Enable CNAMEs for this Application Segment.
            passive_health_enabled (bool):
                Enable Passive Health Checks for this Application Segment.
            icmp_access_type (str): Sets ICMP access type for ZPA clients.

        Returns:
            tuple: A tuple containing (ApplicationSegment, Response, error)
        
        Examples:
            Add a new application segment for example.com, ports 8080-8085.

            >>> zpa.app_segments_pra.add_segment('new_app_segment',
            ...    domain_names=['example.com'],
            ...    segment_group_id='99999',
            ...    tcp_ports=['8080', '8085'],
            ...    server_group_ids=['99999', '88888'])
        """
        http_method = "post".upper()
        api_url = format_url(f"{self._base_url}/application")

        payload = {
            "name": name,
            "domainNames": domain_names,
            "segmentGroupId": segment_group_id,
            "serverGroups": [{"id": group_id} for group_id in server_group_ids],
            "tcpPortRanges": tcp_port_ranges,
            "udpPortRanges": udp_port_ranges,
            "commonAppsDto": common_apps_dto if common_apps_dto else None,
        }

        if common_apps_dto:
            camel_common_apps_dto = recursive_snake_to_camel(common_apps_dto)
            payload["commonAppsDto"] = camel_common_apps_dto

        # Optional parameters for the payload
        add_id_groups(self.reformat_params, kwargs, payload)

        for key, value in kwargs.items():
            if value is not None:
                payload[snake_to_camel(key)] = value

        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, json=payload, params=params)
        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request)
        if error:
            return (None, response, error)

        result = ApplicationSegmentPRA(response.get_body())
        return (result, response, None)

    def update_segment_pra(self, segment_id: str, common_apps_dto=None, **kwargs) -> tuple:
        """
        Update an existing application segment.

        Args:
            segment_id (str): The unique ID of the application segment.

        Returns:
            tuple: A tuple containing (ApplicationSegment, Response, error)
        """
        http_method = "put".upper()
        api_url = format_url(f"{self._base_url}/application/{segment_id}")

        # Fetch existing data
        existing_segment, _, error = self.get_segment_pra(segment_id, **kwargs)
        if error:
            return (None, None, error)

        payload = {snake_to_camel(k): v for k, v in existing_segment.request_format().items()}

        if kwargs.get("tcp_port_ranges"):
            payload["tcpPortRange"] = [{"from": ports[0], "to": ports[1]} for ports in kwargs.pop("tcp_port_ranges")]

        if kwargs.get("udp_port_ranges"):
            payload["udpPortRange"] = [{"from": ports[0], "to": ports[1]} for ports in kwargs.pop("udp_port_ranges")]

        if common_apps_dto:
            camel_common_apps_dto = recursive_snake_to_camel(common_apps_dto)
            payload["commonAppsDto"] = camel_common_apps_dto

        # Apply updates
        add_id_groups(self.reformat_params, kwargs, payload)

        for key, value in kwargs.items():
            payload[snake_to_camel(key)] = value

        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, json=payload, params=params)
        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request)
        if error:
            return (None, response, error)

        result = ApplicationSegmentPRA(response.get_body())
        return (result, response, None)

    def delete_segment_pra(self, segment_id: str, force_delete: bool = False, **kwargs) -> tuple:
        """
        Delete an application segment.

        Args:
            segment_id (str): The unique ID of the application segment.
            force_delete (bool, optional): Whether to force delete the mapping between the segment and the group.

        Returns:
            tuple: A tuple containing (None, Response, error)
        """
        http_method = "delete".upper()
        api_url = format_url(f"{self._base_url}/application/{segment_id}")

        params = {}
        if force_delete:
            params["forceDelete"] = "true"
        if "microtenant_id" in kwargs:
            params["microtenantId"] = kwargs.pop("microtenant_id")

        request, error = self._request_executor.create_request(http_method, api_url, params=params)
        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request)
        if error:
            return (None, response, error)

        return (None, response, None)
