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
from zscaler.zpa.models.lss import LSSConfig
from zscaler.utils import format_url, snake_to_camel, keys_exists
from urllib.parse import urlencode


class LSSConfigControllerAPI(APIClient):
    source_log_map = {
        "app_connector_metrics": "zpn_ast_comprehensive_stats",
        "app_connector_status": "zpn_ast_auth_log",
        "audit_logs": "zpn_audit_log",
        "browser_access": "zpn_http_trans_log",
        "private_svc_edge_status": "zpn_sys_auth_log",
        "user_activity": "zpn_trans_log",
        "user_status": "zpn_auth_log",
        "web_inspection": "zpn_waf_http_exchanges_log",
    }

    def __init__(self, request_executor, config):
        super().__init__()
        self._request_executor = request_executor
        customer_id = config["client"].get("customerId")
        self._base_endpoint = f"/zpa/mgmtconfig/v1/admin/customers/{customer_id}"

    def _create_policy(self, conditions: list) -> list:
        """
        Creates a dict template for feeding conditions into the ZPA Policies API when adding or updating a policy.

        Args:
            conditions (list): List of condition tuples.

        Returns:
            :obj:`list`: List containing the LSS Log Receiver Policy conditions template.

        """

        template = []

        for condition in conditions:
            # Template for SAML, SCIM, and SCIM_GROUP Policy Rule objects
            if condition[0] in ["saml", "scim", "scim_group"]:
                operand = {"operands": [{"objectType": condition[0].upper(), "entryValues": []}]}
                for entry in condition[1]:
                    entry_values = {
                        "lhs": entry[0],
                        "rhs": entry[1],
                    }
                    operand["operands"][0]["entryValues"].append(entry_values)
            # Template for client_type Policy Rule objects
            elif condition[0] == "client_type":
                operand = {
                    "operands": [
                        {
                            "objectType": condition[0].upper(),
                            "values": [self.get_client_types()[item] for item in condition[1]],
                        }
                    ]
                }
            # Template for all other object types
            else:
                operand = {
                    "operands": [
                        {
                            "objectType": condition[0].upper(),
                            "values": condition[1],
                        }
                    ]
                }
            template.append(operand)

        return template

    def list_configs(self, query_params=None, keep_empty_params=False) -> tuple:
        """
        Enumerates log receivers in your organization with pagination.
        A subset of log receivers can be returned that match a supported
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
            tuple: A tuple containing (list of AppConnectorGroup instances, Response, error)

        Example:
            >>> lss_configs = zpa.lss.list_configs(search="example", pagesize=100)
        """
        http_method = "get".upper()
        api_url = format_url(f"{self._base_endpoint}/lssConfig")

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
        response, error = self._request_executor.execute(request, LSSConfig)

        if error:
            return (None, response, error)

        # Parse the response into AppConnectorGroup instances
        try:
            result = []
            for item in response.get_body():
                result.append(LSSConfig(self.form_response_body(item)))
        except Exception as error:
            return (None, response, error)

        return (result, response, None)

    def get_config(self, lss_config_id: str, **kwargs) -> LSSConfig:
        """
        Gets information on the specified LSS Receiver config.

        Args:
            lss_config_id (str): The unique identifier of the LSS Receiver config.

        Returns:
            LSSConfig: The corresponding LSS Receiver config object.
        """
        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._base_endpoint}
            /lssConfig/{lss_config_id}
            """
        )

        request, error = self._request_executor.create_request(http_method, api_url, {}, kwargs)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return LSSConfig(response.get_body())

    def add_lss_config(
        self,
        lss_host: str,
        lss_port: str,
        name: str,
        source_log_type: str,
        app_connector_group_ids: list = None,
        enabled: bool = True,
        source_log_format: str = "csv",
        use_tls: bool = False,
        **kwargs,
    ) -> LSSConfig:
        """
        Adds a new LSS Receiver Config to ZPA.

        Args:
            app_connector_group_ids (list): A list of unique IDs for the App Connector Groups associated with this LSS Config. `Defaults to None.`
            enabled (bool): Enable the LSS Receiver. `Defaults to True`.
            lss_host (str): The IP address of the LSS Receiver.
            lss_port (str): The port number for the LSS Receiver.
            name (str): The name of the LSS Config.
            source_log_format (str): The format for the logs. Defaults to `csv`.
            source_log_type (str): The type of logs that will be sent to the receiver as part of this config.
            use_tls (bool): Enable to use TLS on the log traffic between LSS components. `Defaults to False.`

        Keyword Args:
            description (str): Additional information about the LSS Config.
            filter_status_codes (list): A list of Session Status Codes that will be excluded by LSS.
            log_stream_content (str): Custom log stream content formatting for the LSS Host.
            policy_rules (list): A list of policy rule tuples, such as (`object_type`, [`object_id`]).

        Returns:
            LSSConfig: The newly created LSS Config resource object.

        Examples:

            Add an LSS Receiver config that receives App Connector Metrics logs.

            >>> zpa.lss.add_lss_config(
                    app_connector_group_ids=["app_conn_group_id"],
                    lss_host="192.0.2.100",
                    lss_port="8080",
                    name="app_con_metrics_to_siem",
                    source_log_type="app_connector_metrics"
                )

            Add an LSS Receiver config that receives User Activity logs.

            >>> zpa.lss.add_lss_config(
                    app_connector_group_ids=["app_conn_group_id"],
                    lss_host="192.0.2.100",
                    lss_port="8080",
                    name="user_activity_to_siem",
                    policy_rules=[
                        ("idp", ["idp_id"]),
                        ("app", ["app_seg_id"]),
                        ("app_group", ["app_seg_group_id"]),
                        ("saml", [("saml_attr_id", "saml_attr_value")])
                    ],
                    source_log_type="user_activity"
                )
        """
        http_method = "post".upper()

        # Construct the API URL
        api_url = format_url(
            f"""
            {self._base_endpoint}
            /lssConfig
            """
        )

        # Map the source log type to ZPA internal log codes
        source_log_type = self.source_log_map[source_log_type]

        # Handle custom log stream content formatting or use default formatting from ZPA
        if kwargs.get("log_stream_content"):
            log_stream_content = kwargs.pop("log_stream_content")
        else:
            log_stream_content = self.get_log_formats()[source_log_type][source_log_format]

        # Prepare the payload
        payload = {
            "config": {
                "enabled": enabled,
                "lssHost": lss_host,
                "lssPort": lss_port,
                "name": name,
                "format": log_stream_content,
                "sourceLogType": source_log_type,
                "useTls": use_tls,
            },
            "connectorGroups": [{"id": group_id} for group_id in app_connector_group_ids] if app_connector_group_ids else [],
        }

        # Handle policy rules and convert tuples into dictionary format
        if kwargs.get("policy_rules"):
            payload["policyRuleResource"] = {
                "conditions": self._create_policy(kwargs.pop("policy_rules")),
                "name": kwargs.get("policy_name", "SIEM_POLICY"),
            }

        # Add optional filter status codes if provided
        if kwargs.get("filter_status_codes"):
            payload["config"]["filter"] = kwargs.pop("filter_status_codes")

        # Add additional optional parameters to the payload
        for key, value in kwargs.items():
            payload[snake_to_camel(key)] = value

        # Create the request using the request executor
        request, error = self._request_executor.create_request(http_method, api_url, payload, {})
        if error:
            return None

        # Execute the request
        response, error = self._request_executor.execute(request)
        if error:
            return None

        # Return the created LSS config object
        return LSSConfig(response.get_body())

    def update_lss_config(self, lss_config_id: str, **kwargs) -> LSSConfig:
        """
        Updates the specified LSS Receiver Config.

        Args:
            lss_config_id (str): The unique identifier for the LSS Receiver config.

        Keyword Args:
            description (str): Additional information about the LSS Config.
            enabled (bool): Enable the LSS host. Defaults to ``True``.
            filter_status_codes (list): A list of Session Status Codes that will be excluded by LSS.
            log_stream_content (str): Formatter for the log stream content that will be sent to the LSS Host.
            policy_rules (list): A list of policy rule tuples for conditional logic.
            source_log_format (str): The format for the logs. Must be one of csv, json, tsv. Defaults to csv.
            source_log_type (str): The type of logs that will be sent to the receiver as part of this config.
            use_tls (bool): Enable TLS on the log traffic between LSS components. Defaults to ``False``.

        Returns:
            LSSConfig: The updated LSS Receiver config object.

        Examples:
            Update an LSS Log Receiver config to change from user activity to user status.

            .. code-block:: python

                zpa.lss.update_lss_config(
                    lss_config_id="99999",
                    name="user_status_to_siem",
                    policy_rules=[
                        ("idp", ["idp_id"]),
                        ("client_type", ["machine_tunnel"]),
                        ("saml", [("attribute_id", "11111")]),
                    ],
                    source_log_type="user_status")
        """
        http_method = "put".upper()

        # Construct the API URL using the format_url pattern
        api_url = format_url(
            f"""
            {self._base_endpoint}
            /lssConfig/{lss_config_id}
            """
        )

        # Fetch the current configuration and update it with the provided kwargs
        existing_config = self.get_config(lss_config_id)
        payload = existing_config.request_format()

        # Handle custom log stream content formatting or map it to the ZPA internal format
        if kwargs.get("log_stream_content"):
            payload["config"]["format"] = kwargs.pop("log_stream_content")
        elif kwargs.get("source_log_type"):
            source_log_type = self.source_log_map[kwargs.pop("source_log_type")]
            payload["config"]["sourceLogType"] = source_log_type
            payload["config"]["format"] = self.get_log_formats()[source_log_type][kwargs.pop("source_log_format", "csv")]

        # Update the payload with known fields
        for key in ["name", "lss_host", "lss_port", "enabled", "use_tls"]:
            if key in kwargs:
                payload["config"][snake_to_camel(key)] = kwargs.pop(key)

        if "filter_status_codes" in kwargs:
            payload["config"]["filter"] = kwargs.pop("filter_status_codes")

        # Convert policy_rules tuples into the expected dict format and add to payload
        if kwargs.get("policy_rules"):
            if keys_exists(payload, "policyRuleResource", "name"):
                policy_name = payload["policyRuleResource"]["name"]
            else:
                policy_name = "placeholder"
            payload["policyRuleResource"] = {
                "conditions": self._create_policy(kwargs.pop("policy_rules")),
                "name": kwargs.pop("policy_name", policy_name),
            }

        # Add additional provided parameters to the payload
        for key, value in kwargs.items():
            payload[snake_to_camel(key)] = value

        # Create the request using the request executor
        request, error = self._request_executor.create_request(http_method, api_url, payload)
        if error:
            return None

        # Execute the request
        response, error = self._request_executor.execute(request)
        if error:
            return None

        # Return the updated configuration if successful
        if response.get_status_code() == 204:
            return self.get_config(lss_config_id)

        return None

    def delete_lss_config(self, lss_config_id: str, **kwargs) -> int:
        """
        Deletes the specified LSS Receiver Config.

        Args:
            lss_config_id (str): The unique identifier of the LSS Receiver config to be deleted.

        Returns:
            int: Status code of the delete operation.
        """
        http_method = "delete".upper()
        api_url = format_url(f"{self._base_endpoint}/lssConfig/{lss_config_id}")

        request, error = self._request_executor.create_request(http_method, api_url, {})
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return response.status_code

    def get_client_types(self, client_type=None) -> dict:
        """
        Returns all available LSS Client Types or a specific Client Type if specified.

        Args:
            client_type (str, optional): The human-readable name of the client type to filter for.

        Returns:
            dict: Dictionary containing all or a specific LSS Client Type with human-readable name as the key.

        Examples:
            >>> client_types = zpa.lss.get_client_types()
            >>> web_browser_type = zpa.lss.get_client_types('web_browser')
        """

        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._base_endpoint}
            /clientTypes"
        """,
            api_version="v2_lss",
        )

        request, error = self._request_executor.create_request(http_method, api_url)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        client_types = response.get_body()
        reverse_map = {v.lower().replace(" ", "_"): k for k, v in client_types.items()}

        if client_type and client_type in reverse_map:
            return {client_type: reverse_map[client_type]}

        return reverse_map

    def get_log_formats(self, log_type=None) -> dict:
        """
        Returns all available pre-configured LSS Log Formats or a specific log format if specified.

        Args:
            log_type (str, optional): The name of the log type to retrieve (e.g., 'zpn_ast_comprehensive_stats').

        Returns:
            dict: Dictionary containing pre-configured LSS Log Formats.

        Examples:
            >>> all_log_formats = zpa.lss.get_log_formats()
            >>> specific_format = zpa.lss.get_log_formats('zpn_ast_comprehensive_stats')
        """
        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._base_endpoint}
            /lssConfig/logType/formats"
        """,
            api_version="v2",
        )

        request, error = self._request_executor.create_request(http_method, api_url)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        formats = response.get_body()

        if log_type:
            specific_format = formats.get(log_type)
            return {log_type: specific_format} if specific_format else {}
        else:
            return formats

    def get_status_codes(self, log_type: str = "all") -> dict:
        """
        Returns a list of LSS Session Status Codes filtered by log type.

        Args:
            log_type (str): Filter the LSS Session Status Codes by Log Type.

        Returns:
            dict: Dictionary containing all LSS Session Status Codes.

        Examples:
            >>> all_status_codes = zpa.lss.get_status_codes()
            >>> user_activity_codes = zpa.lss.get_status_codes(log_type="user_activity")
        """
        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._base_endpoint}
            /statusCodes"
        """,
            api_version="v2",
        )

        request, error = self._request_executor.create_request(http_method, api_url)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        all_status_codes = response.get_body()

        if log_type == "all":
            return all_status_codes
        else:
            log_type_key = self.source_log_map.get(log_type)
            if not log_type_key:
                raise ValueError("Incorrect log_type provided.")

            filtered_status_codes = {
                code: details for code, details in all_status_codes.items() if log_type_key in details.get("log_types", [])
            }
            return filtered_status_codes
