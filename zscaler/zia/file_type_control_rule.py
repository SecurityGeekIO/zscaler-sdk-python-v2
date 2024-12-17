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
from zscaler.utils import format_url
from zscaler.api_client import APIClient
from zscaler.zia.models.filetyperules import FileTypeControlRules


class FileTypeControlRuleAPI(APIClient):

    reformat_params = [
        ("departments", "departments"),
        ("groups", "groups"),
        ("users", "users"),
        ("labels", "labels"),
        ("locations", "locations"),
        ("location_groups", "locationGroups"),
    ]

    _zia_base_endpoint = "/zia/api/v1"

    def __init__(self, request_executor):
        super().__init__()
        self._request_executor: RequestExecutor = request_executor

    def list_rules(
        self,
        query_params=None,
    ) -> tuple:
        """
        Lists file type control rules rules in your organization with pagination.
        A subset of file type control rules rules  can be returned that match a supported
        filter expression or query.

        Args:
            query_params {dict}: Map of query parameters for the request.
                [query_params.pagesize] {int}: Page size for pagination.
                [query_params.search] {str}: Search string for filtering results.
                [query_params.max_items] {int}: Maximum number of items to fetch before stopping.
                [query_params.max_pages] {int}: Maximum number of pages to request before stopping.

        Returns:
            tuple: A tuple containing (list of file type control rules rules instances, Response, error).

        Example:
            List all file type control rules rules with a specific page size:

            >>> rules_list, response, error = zia.file_type_control_rule.list_rules(
            ...    query_params={"pagesize": 50}
            ... )
            >>> for rule in rules_list:
            ...    print(rule.as_dict())
        """
        http_method = "get".upper()
        api_url = format_url(f"""
            {self._zia_base_endpoint}
            /fileTypeRules
        """)

        query_params = query_params or {}

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
            for item in response.get_all_pages_results():
                result.append(FileTypeControlRules(self.form_response_body(item))
            )
        except Exception as error:
            return (None, response, error)

        return (result, response, None)

    def get_rule(
        self,
        rule_id: int,
    ) -> tuple:
        """
        Returns information for the specified file type control rules filter rule.

        Args:
            rule_id (str): The unique identifier for the file type control rules filter rule.

        Returns:
            tuple: A tuple containing (file type control rules rule instance, Response, error).

        Example:
            Retrieve a file type control rules rule by its ID:

            >>> rule, response, error = zia.file_type_control_rule.get_rule(rule_id=123456)
            >>> if not error:
            ...    print(rule.as_dict())
        """
        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._zia_base_endpoint}
            /fileTypeRules/{rule_id}
            """
        )

        body = {}
        headers = {}

        request, error = self._request_executor.\
            create_request(http_method, api_url, body, headers)

        if error:
            return (None, None, error)

        # Execute the request
        response, error = self._request_executor.\
            execute(request, FileTypeControlRules)

        if error:
            return (None, response, error)

        try:
            result = FileTypeControlRules(
                self.form_response_body(response.get_body())
            )
        except Exception as error:
            return (None, response, error)
        return (result, response, None)

    def add_rule(
        self,
        **kwargs,
    ) -> tuple:
        """
        Adds a new file type control rules rule.

        Args:
            name (str): Name of the rule, max 31 chars.

        Keyword Args:
            description (str): Additional information about the rule.
            order (str): The order of the rule, defaults to adding rule to bottom of list.
            rank (str): The admin rank of the rule. Supported values 1-7
            state (str): The rule state. Accepted values are 'ENABLED' or 'DISABLED'.
            redirect_ip (str): The IP address to which the traffic will be redirected to when the DNAT rule is triggered.
            enable_full_logging (bool): If True, enables full logging.
            capture_pcap (bool): Indicates whether packet capture (PCAP) is enabled or not.
            predefined (bool): Indicates that the rule is predefined by using a true value
            default_rule (bool): Indicates whether the rule is the Default Cloud DNS Rule or not
            action (str): Action that must take place if the traffic matches the rule criteria. 
                Supported Values: ALLOW, BLOCK, REDIR_REQ, REDIR_RES, REDIR_ZPA, REDIR_REQ_DOH, REDIR_REQ_KEEP_SENDER
                    REDIR_REQ_TCP, REDIR_REQ_UDP, BLOCK_WITH_RESPONSE
            applications (list): DNS tunnels and network applications to which the rule applies
            dest_ip_groups (list): The IDs for the destination IP groups that this rule applies to.
            dest_ipv6_groups (list): The IDs for the destination IPV6 groups that this rule applies to.
            dest_countries (list): Destination countries for the rule.
            dest_addresses (list): Destination IPs for the rule. Accepts IP addresses or CIDR.
            src_ips (list): Source IPs for the rule. Accepts IP addresses or CIDR.
            source_countries (list): The countries of origin of traffic for which the rule is applicable.
            src_ip_groups (list): The IDs for the source IP groups that this rule applies to.
            src_ipv6_groups (list): The IDs for the source IPV6 groups that this rule applies to.
            dest_ip_categories (list): IP address categories for the rule.
            dest_countries (list): Destination countries for the rule.
            groups (list): The IDs for the groups that this rule applies to.
            users (list): The IDs for the users that this rule applies to.
            res_categories (list): Source IPs for the rule. Accepts IP addresses or CIDR.
            dns_rule_request_types (list): DNS request types to which the rule applies
            protocols (list): The protocols to which the rules applies.
            block_response_code (list): Specifies the DNS response code to be sent to the client when the action is configured to block and send response code
            devices (list): IDs for devices managed by Zscaler Client Connector.
            device_groups (list): IDs for device groups managed by Zscaler Client Connector.
            labels (list): The IDs for the labels that this rule applies to.
            locations (list): The IDs for the locations that this rule applies to.
            location_groups (list): The IDs for the location groups that this rule applies to.
            edns_ecs_object (list): IDs for EDNS ECS object which resolves DNS request
            time_windows (list): IDs for time windows the rule applies to.
            application_groups (list): IDs for DNS application groups to which the rule applies
            dns_gateway (list): ID for DNS gateway used to redirect traffic, specified when the rule action is to redirect DNS request to an external DNS service
            zpa_ip_group (list): The ZPA IP pool specified when the rule action is to resolve domain names of ZPA applications to an ephemeral IP address from a preconfigured IP pool

        Returns:
            tuple: Updated firewall dns filtering rule resource record.

        Example:
            Update an existing rule to change its name and action:

            >>> zia.file_type_control_rule.update_rule(
            ...    rule_id=123456,
            ...    name='UPDATED_RULE',
            ...    ba_rule_action='ALLOW',
            ...    description='Updated action for the rule'
            ... )
        """
        http_method = "post".upper()
        api_url = format_url(
            f"""
            {self._zia_base_endpoint}
            /fileTypeRules
        """
        )

        body = kwargs

        # Convert 'enabled' to 'state' (ENABLED/DISABLED) if it's present in the payload
        if "enabled" in body:
            body["state"] = "ENABLED" if body.pop("enabled") else "DISABLED"

        # Create the request
        request, error = self._request_executor\
            .create_request(
            method=http_method,
            endpoint=api_url,
            body=body,
        )

        if error:
            return (None, None, error)

        # Execute the request
        response, error = self._request_executor.\
            execute(request, FileTypeControlRules)
        if error:
            return (None, response, error)

        try:
            result = FileTypeControlRules(
                self.form_response_body(response.get_body())
            )
        except Exception as error:
            return (None, response, error)
        return (result, response, None)

    def update_rule(self, rule_id: int, **kwargs) -> tuple:
        """
        Updates an existing file type control rules rule.

        Args:
            rule_id (str): The unique ID for the rule that is being updated.
            **kwargs: Optional keyword args.

        Keyword Args:
            name (str): Name of the rule, max 31 chars.
            description (str): Additional information about the rule.
            order (str): The order of the rule, defaults to adding rule to bottom of list.
            rank (str): The admin rank of the rule. Supported values 1-7
            state (str): The rule state. Accepted values are 'ENABLED' or 'DISABLED'.
            redirect_ip (str): The IP address to which the traffic will be redirected to when the DNAT rule is triggered.
            enable_full_logging (bool): If True, enables full logging.
            capture_pcap (bool): Indicates whether packet capture (PCAP) is enabled or not.
            predefined (bool): Indicates that the rule is predefined by using a true value
            default_rule (bool): Indicates whether the rule is the Default Cloud DNS Rule or not
            action (str): Action that must take place if the traffic matches the rule criteria. 
                Supported Values: ALLOW, BLOCK, REDIR_REQ, REDIR_RES, REDIR_ZPA, REDIR_REQ_DOH, REDIR_REQ_KEEP_SENDER
                    REDIR_REQ_TCP, REDIR_REQ_UDP, BLOCK_WITH_RESPONSE
            applications (list): DNS tunnels and network applications to which the rule applies
            dest_ip_groups (list): The IDs for the destination IP groups that this rule applies to.
            dest_ipv6_groups (list): The IDs for the destination IPV6 groups that this rule applies to.
            dest_countries (list): Destination countries for the rule.
            dest_addresses (list): Destination IPs for the rule. Accepts IP addresses or CIDR.
            src_ips (list): Source IPs for the rule. Accepts IP addresses or CIDR.
            source_countries (list): The countries of origin of traffic for which the rule is applicable.
            src_ip_groups (list): The IDs for the source IP groups that this rule applies to.
            src_ipv6_groups (list): The IDs for the source IPV6 groups that this rule applies to.
            dest_ip_categories (list): IP address categories for the rule.
            dest_countries (list): Destination countries for the rule.
            groups (list): The IDs for the groups that this rule applies to.
            users (list): The IDs for the users that this rule applies to.
            res_categories (list): Source IPs for the rule. Accepts IP addresses or CIDR.
            dns_rule_request_types (list): DNS request types to which the rule applies
            protocols (list): The protocols to which the rules applies.
            block_response_code (list): Specifies the DNS response code to be sent to the client when the action is configured to block and send response code
            devices (list): IDs for devices managed by Zscaler Client Connector.
            device_groups (list): IDs for device groups managed by Zscaler Client Connector.
            labels (list): The IDs for the labels that this rule applies to.
            locations (list): The IDs for the locations that this rule applies to.
            location_groups (list): The IDs for the location groups that this rule applies to.
            edns_ecs_object (list): IDs for EDNS ECS object which resolves DNS request
            time_windows (list): IDs for time windows the rule applies to.
            application_groups (list): IDs for DNS application groups to which the rule applies
            dns_gateway (list): ID for DNS gateway used to redirect traffic, specified when the rule action is to redirect DNS request to an external DNS service
            zpa_ip_group (list): The ZPA IP pool specified when the rule action is to resolve domain names of ZPA applications to an ephemeral IP address from a preconfigured IP pool

        Returns:
            tuple: Updated firewall dns filtering rule resource record.

        Example:
            Update an existing rule to change its name and action:

            >>> zia.file_type_control_rule.update_rule(
            ...    rule_id=123456,
            ...    name='UPDATED_RULE',
            ...    ba_rule_action='ALLOW',
            ...    description='Updated action for the rule'
            ... )
        """
        http_method = "put".upper()
        api_url = format_url(
            f"""
            {self._zia_base_endpoint}
            /fileTypeRules/{rule_id}
        """
        )

        body = kwargs

        # Convert 'enabled' to 'state' (ENABLED/DISABLED) if it's present in the payload
        if "enabled" in body:
            body["state"] = "ENABLED" if body.pop("enabled") else "DISABLED"

        # Create the request
        request, error = self._request_executor\
            .create_request(
            method=http_method,
            endpoint=api_url,
            body=body,
        )

        if error:
            return (None, None, error)

        # Execute the request
        response, error = self._request_executor.\
            execute(request, FileTypeControlRules)
        if error:
            return (None, response, error)

        try:
            result = FileTypeControlRules(
                self.form_response_body(response.get_body())
            )
        except Exception as error:
            return (None, response, error)
        return (result, response, None)
    
    def delete_rule(self, rule_id: int) -> tuple:
        """
        Deletes the specified file type control rules filter rule.

        Args:
            rule_id (str): The unique identifier for the file type control rules rule.

        Returns:
            :obj:`int`: The status code for the operation.

        Examples:
            >>> zia.file_type_control_rule.delete_rule('278454')

        """
        http_method = "delete".upper()
        api_url = format_url(
            f"""
            {self._zia_base_endpoint}
            /fileTypeRules/{rule_id}
        """
        )

        params = {}

        request, error = self._request_executor.\
            create_request(http_method, api_url, params=params)
        if error:
            return (None, None, error)

        response, error = self._request_executor.\
            execute(request)
        if error:
            return (None, response, error)

        return (None, response, None)