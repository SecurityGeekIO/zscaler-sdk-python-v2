# -*- coding: utf-8 -*-

# Copyright (c) 2023, Zscaler Inc.
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.


from zscaler.api_client import APIClient
from zscaler.zpa.models.lss import LSSConfig
from zscaler.utils import format_url, convert_keys, snake_to_camel, keys_exists
from zscaler.api_response import get_paginated_data
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

    #     self.v2_admin_url = "https://config.private.zscaler.com/mgmtconfig/v2/admin/lssConfig"

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
            {self._base_url}
            /clientTypes"
        """,
        api_version="v2_lss"
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
    
    # def get_client_types(self, client_type=None) -> Box:
    #     """
    #     Returns all available LSS Client Types or a specific Client Type if specified.

    #     Client Types are used when creating LSS Receiver configs.
    #     ZPA uses an internal code for Client Types, e.g.
    #     `zpn_client_type_ip_anchoring` is the Client Type for a ZIA Service Edge.
    #     The zscaler-sdk-python inverts the key/value so
    #     that you can perform a lookup using a human-readable name in your code (e.g. `cloud_connector`).

    #     Args:
    #         client_type_name (str, optional): The human-readable name of the client type to filter for.

    #     Returns:
    #         :obj:`Box`: Dictionary containing all or a specific LSS Client Type with human-readable name as the key.

    #     Examples:
    #         Print all LSS Client Types:
    #         >>> print(zpa.lss.get_client_types())

    #         Print only the 'web_browser' Client Type:
    #         >>> print(zpa.lss.get_client_types('web_browser'))
    #     """
    #     response = self.rest.send("GET", "clientTypes", api_version="v2_lss")
    #     if response.status_code == 200:
    #         client_types = response.json()
    #         reverse_map = {v.lower().replace(" ", "_"): k for k, v in client_types.items()}
    #         box = Box(reverse_map)

    #         if client_type and client_type in box:
    #             return Box({client_type: box[client_type]})
    #         return box
    #     else:
    #         response.raise_for_status()

    # def get_log_formats(self, log_type=None) -> Box:
    #     """
    #     Returns all available pre-configured LSS Log Formats or a specific log format if specified.

    #     LSS Log Formats are provided as either CSV, JSON, or TSV. The values can be used when
    #     creating or updating LSS Log Receiver configs.

    #     Args:
    #         log_type_name (str, optional): The name of the log type to retrieve (e.g., 'zpn_ast_comprehensive_stats').

    #     Returns:
    #         :obj:`Box`: Dictionary containing pre-configured LSS Log Formats.

    #     Examples:
    #         >>> print(zpa.lss.get_log_formats())
    #         >>> print(zpa.lss.get_log_formats('zpn_ast_comprehensive_stats'))
    #     """
    #     response = self.rest.send("GET", "lssConfig/logType/formats", api_version="v2")
    #     if response.status_code == 200:
    #         formats = response.json()
    #         if log_type:
    #             # Filter and return only the requested log type
    #             specific_format = formats.get(log_type, None)
    #             if specific_format:
    #                 return Box({log_type: specific_format})
    #             else:
    #                 return Box()  # or raise an Exception if preferred
    #         else:
    #             # Return all formats
    #             return Box(formats)
    #     else:
    #         response.raise_for_status()

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
            {self._base_url}
            /lssConfig/logType/formats"
        """,
        api_version="v2"
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

    # def get_status_codes(self, log_type: str = "all") -> Box:
    #     """
    #     Returns a list of LSS Session Status Codes filtered by log type.

    #     Args:
    #         log_type (str):
    #             Filter the LSS Session Status Codes by Log Type, accepted values are:

    #             - ``all``
    #             - ``app_connector_status``
    #             - ``private_svc_edge_status``
    #             - ``user_activity``
    #             - ``user_status``

    #             `Defaults to all.`

    #     Returns:
    #         :obj:`Box`: Dictionary containing all LSS Session Status Codes.

    #     Examples:
    #         Print all LSS Session Status Codes.

    #         >>> for item in zpa.lss.get_status_codes():
    #         ...    print(item)

    #         Print LSS Session Status Codes for `User Activity` log types.

    #         >>> for item in zpa.lss.get_status_codes(log_type="user_activity"):
    #         ...    print(item)

    #     """
    #     full_url = f"{self.v2_admin_url}/statusCodes"
    #     response = requests.get(full_url, headers=self.rest.headers)
    #     response.raise_for_status()
    #     all_status_codes = response.json()

    #     if log_type == "all":
    #         return Box(all_status_codes)
    #     else:
    #         filtered_status_codes = {}
    #         log_type_key = self.source_log_map.get(log_type)
    #         if log_type_key:
    #             for code, details in all_status_codes.items():
    #                 if log_type_key in details.get("log_types", []):
    #                     filtered_status_codes[code] = details
    #             return Box(filtered_status_codes)
    #         else:
    #             raise ValueError("Incorrect log_type provided.")

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
            {self._base_url}
            /statusCodes"
        """,
        api_version="v2"
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
                code: details for code, details in all_status_codes.items()
                if log_type_key in details.get("log_types", [])
            }
            return filtered_status_codes

    # def list_configs(self, **kwargs) -> BoxList:
    #     """
    #     Returns all configured LSS receivers.

    #     Keyword Args:
    #         **max_items (int):
    #             The maximum number of items to request before stopping iteration.
    #         **max_pages (int):
    #             The maximum number of pages to request before stopping iteration.
    #         **pagesize (int):
    #             Specifies the page size. The default size is 20, but the maximum size is 500.
    #         **search (str, optional):
    #             The search string used to match against features and fields.

    #     Returns:
    #         :obj:`BoxList`: List of all configured LSS receivers.

    #     Examples:
    #         Print all configured LSS Receivers.

    #         >>> for lss_config in zpa.lss.list_configs():
    #         ...    print(config)
    #     """
    #     list, _ = self.rest.get_paginated_data(path="/lssConfig", **kwargs, api_version="v2")
    #     return list

    # def get_config(self, lss_config_id: str) -> Box:
    #     """
    #     Returns information on the specified LSS Receiver config.

    #     Args:
    #         lss_config_id (str):
    #             The unique identifier for the LSS Receiver config.

    #     Returns:
    #         :obj:`Box`: The resource record for the LSS Receiver config in a Box object for easy attribute access.

    #     Examples:
    #         Print information on the specified LSS Receiver config.

    #         >>> print(zpa.lss.get_config('99999'))
    #     """
    #     # Perform the GET request
    #     return self.rest.get(f"lssConfig/{lss_config_id}", api_version="v2")

    # def add_lss_config(
    #     self,
    #     lss_host: str,
    #     lss_port: str,
    #     name: str,
    #     source_log_type: str,
    #     app_connector_group_ids: list = None,
    #     enabled: bool = True,
    #     source_log_format: str = "csv",
    #     use_tls: bool = False,
    #     **kwargs,
    # ) -> Box:
    #     """
    #     Adds a new LSS Receiver Config to ZPA.

    #     Args:
    #         app_connector_group_ids (list): A list of unique IDs for the App Connector Groups associated with this
    #             LSS Config. `Defaults to None.`
    #         enabled (bool): Enable the LSS Receiver. `Defaults to True`.
    #         lss_host (str): The IP address of the LSS Receiver.
    #         lss_port (str): The port number for the LSS Receiver.
    #         name (str): The name of the LSS Config.
    #         source_log_format (str):
    #             The format for the logs. Must be one of the following options:

    #             - ``csv`` - send logs in CSV format
    #             - ``json`` - send logs in JSON format
    #             - ``tsv`` - send logs in TSV format

    #             `Defaults to csv.`
    #         source_log_type (str):
    #             The type of logs that will be sent to the receiver as part of this config. Must be one of the following
    #             options:

    #             - ``app_connector_metrics``
    #             - ``app_connector_status``
    #             - ``audit_logs``
    #             - ``browser_access``
    #             - ``private_svc_edge_status``
    #             - ``user_activity``
    #             - ``user_status``
    #         use_tls (bool):
    #             Enable to use TLS on the log traffic between LSS components. `Defaults to False.`

    #     Keyword Args:
    #         description (str):
    #             Additional information about the LSS Config.
    #         filter_status_codes (list):
    #             A list of Session Status Codes that will be excluded by LSS.
    #         log_stream_content (str):
    #             Formatter for the log stream content that will be sent to the LSS Host. Only pass this parameter if you
    #             intend on using custom log stream content.
    #         policy_rules (list):
    #             A list of policy rule tuples. Tuples must follow the convention:

    #              (`object_type`, [`object_id`]).

    #             E.g.

    #             .. code-block:: python

    #                 ('app_segment_ids', ['11111', '22222']),
    #                 ('segment_group_ids', ['88888']),
    #                 ('idp_ids', ['99999']),
    #                 ('client_type', ['zia_service_edge'])
    #                 ('saml', [('33333', 'value')])

    #     Returns:
    #         :obj:`Box`: The newly created LSS Config resource record.

    #     Examples:

    #         Add an LSS Receiver config that receives App Connector Metrics logs.

    #         .. code-block:: python

    #             zpa.lss.add_config(
    #                 app_connector_group_ids=["app_conn_group_id"],
    #                 lss_host="192.0.2.100,
    #                 lss_port="8080",
    #                 name="app_con_metrics_to_siem",
    #                 source_log_type="app_connector_metrics")

    #         Add an LSS Receiver config that receives User Activity logs.

    #         .. code-block:: python

    #             zpa.lss.add_config(
    #                 app_connector_group_ids=["app_conn_group_id"],
    #                 lss_host="192.0.2.100,
    #                 lss_port="8080",
    #                 name="user_activity_to_siem",
    #                 policy_rules=[
    #                     ("idp", ["idp_id"]),
    #                     ("app", ["app_seg_id"]),
    #                     ("app_group", ["app_seg_group_id"]),
    #                     ("saml", [("saml_attr_id", "saml_attr_value")]),
    #                 ],
    #                 source_log_type="user_activity")

    #         Add an LSS Receiver config that receives User Status logs.

    #         .. code-block:: python

    #             zpa.lss.add_config(
    #                 app_connector_group_ids=["app_conn_group_id"],
    #                 lss_host="192.0.2.100,
    #                 lss_port="8080",
    #                 name="user_activity_to_siem",
    #                 policy_rules=[
    #                     ("idp", ["idp_id"]),
    #                     ("client_type", ["web_browser", "client_connector"]),
    #                     ("saml", [("attribute_id", "test3")]),
    #                 ],
    #                 source_log_type="user_status")

    #     """
    #     source_log_type = self.source_log_map[source_log_type]

    #     # If the user has supplied custom log stream content formatting then we'll use that. Otherwise map the log
    #     # type to internal ZPA log codes and get the preformatted log stream content formatting directly from ZPA.
    #     if kwargs.get("log_stream_content"):
    #         log_stream_content = kwargs.pop("log_stream_content")
    #     else:
    #         log_stream_content = self.get_log_formats()[source_log_type][source_log_format]

    #     payload = {
    #         "config": {
    #             "enabled": enabled,
    #             "lssHost": lss_host,
    #             "lssPort": lss_port,
    #             "name": name,
    #             "format": log_stream_content,
    #             "sourceLogType": source_log_type,
    #             "useTls": use_tls,
    #         },
    #         "connectorGroups": [{"id": group_id} for group_id in app_connector_group_ids],
    #     }

    #     # Convert tuple list to dict and add to payload
    #     if kwargs.get("policy_rules"):
    #         payload["policyRuleResource"] = {
    #             "conditions": self._create_policy(kwargs.pop("policy_rules")),
    #             "name": kwargs.get("policy_name", "SIEM_POLICY"),
    #         }

    #     # Add Session Status Codes to filter if provided
    #     if kwargs.get("filter_status_codes"):
    #         payload["config"]["filter"] = kwargs.pop("filter_status_codes")

    #     # Add optional parameters to payload
    #     for key, value in kwargs.items():
    #         payload[snake_to_camel(key)] = value

    #     response = self.rest.post("/lssConfig", api_version="v2", json=payload)
    #     if isinstance(response, Response):
    #         # this is only true when the creation failed (status code is not 2xx)
    #         status_code = response.status_code
    #         # Handle error response
    #         raise Exception(f"API call failed with status {status_code}: {response.json()}")
    #     return response

    # def update_lss_config(self, lss_config_id: str, **kwargs):
    #     """
    #     Update the LSS Receiver Config.

    #     Args:
    #         lss_config_id (str): The unique id for the LSS Receiver config.
    #         **kwargs: Optional keyword args.

    #     Keyword Args:
    #         description (str):
    #             Additional information about the LSS Config.
    #         enabled (bool):
    #             Enable the LSS host. Defaults to ``True``.
    #         filter_status_codes (list):
    #             A list of Session Status Codes that will be excluded by LSS. If you would like to filter all error codes
    #             then pass the string "all".
    #         log_stream_content (str):
    #             Formatter for the log stream content that will be sent to the LSS Host.
    #         policy_rules (list):
    #             A list of policy rule tuples. Tuples must follow the convention:

    #              (`object_type`, [`object_id`]).

    #             E.g.

    #             .. code-block:: python

    #                 ('app_segment_ids', ['11111', '22222']),
    #                 ('segment_group_ids', ['88888']),
    #                 ('idp_ids', ['99999']),
    #                 ('client_type', ['zpn_client_type_exporter'])
    #                 ('saml_attributes', [('33333', 'value')])
    #         source_log_format (str):
    #             The format for the logs. Must be one of the following options:

    #             - ``csv`` - send logs in CSV format
    #             - ``json`` - send logs in JSON format
    #             - ``tsv`` - send logs in TSV format
    #         source_log_type (str):
    #             The type of logs that will be sent to the receiver as part of this config. Must be one of the following
    #             options:

    #             - ``app_connector_metrics``
    #             - ``app_connector_status``
    #             - ``audit_logs``
    #             - ``browser_access``
    #             - ``private_svc_edge_status``
    #             - ``user_activity``
    #             - ``user_status``
    #         use_tls (bool):
    #             Enable to use TLS on the log traffic between LSS components. Defaults to ``False``.

    #     Examples:

    #         Update an LSS Log Receiver config to change from user activity to user status.

    #         Note that the ``policy_rules`` will need to be modified to be compatible with the chosen
    #         ``source_log_type``.

    #         .. code-block:: python

    #             zpa.lss.update_lss_config(
    #                 name="user_status_to_siem",
    #                 policy_rules=[
    #                     ("idp", ["idp_id"]),
    #                     ("client_type", ["machine_tunnel"]),
    #                     ("saml", [("attribute_id", "11111")]),
    #                 ],
    #                 source_log_type="user_status")
    #     """
    #     # Set payload to value of existing record
    #     payload = convert_keys(self.get_config(lss_config_id))

    #     # If the user has supplied custom log stream content formatting then we'll use that. Otherwise, map the log
    #     # type to internal ZPA log codes and get the preformatted log stream content formatting directly from ZPA.
    #     if kwargs.get("log_stream_content"):
    #         payload["config"]["format"] = kwargs.pop("log_stream_content")
    #     elif kwargs.get("source_log_type"):
    #         source_log_type = self.source_log_map[kwargs.pop("source_log_type")]
    #         payload["config"]["sourceLogType"] = source_log_type
    #         payload["config"]["format"] = self.get_log_formats()[source_log_type][kwargs.pop("source_log_format", "csv")]

    #     # Iterate kwargs and update payload for keys that we've renamed.
    #     for k in list(kwargs):
    #         if k in ["name", "lss_host", "lss_port", "enabled", "use_tls"]:
    #             payload["config"][snake_to_camel(k)] = kwargs.pop(k)
    #         elif k == "filter_status_codes":
    #             payload["config"]["filter"] = kwargs.pop(k)

    #     # Convert tuple list to dict and add to payload
    #     if kwargs.get("policy_rules"):
    #         if keys_exists(payload, "policyRuleResource", "name"):
    #             policy_name = payload["policyRuleResource"]["name"]
    #         else:
    #             policy_name = "placeholder"
    #         payload["policyRuleResource"] = {
    #             "conditions": self._create_policy(kwargs.pop("policy_rules")),
    #             "name": kwargs.pop("policy_name", policy_name),
    #         }

    #     # Add additional provided parameters to payload
    #     for key, value in kwargs.items():
    #         payload[snake_to_camel(key)] = value

    #     # Send the update request to the API
    #     resp = self.rest.put(f"/lssConfig/{lss_config_id}", api_version="v2", json=payload)
    #     if resp.status_code == 204:
    #         # Fetch and return the updated configuration as no content is returned with a 204 response
    #         return self.get_config(lss_config_id)
    #     else:
    #         raise Exception("Failed to update LSS Config, status code: {}".format(resp.status_code))

    # def delete_lss_config(self, lss_config_id: str) -> int:
    #     """
    #     Delete the specified LSS Receiver Config.

    #     Args:
    #         lss_config_id (str): The unique identifier for the LSS Receiver Config to be deleted.

    #     Returns:
    #         :obj:`int`:
    #             The response code for the operation.

    #     Examples:
    #         Delete an LSS Receiver config.

    #         >>> zpa.lss.delete_lss_config('99999')

    #     """
    #     return self.rest.delete(f"/lssConfig/{lss_config_id}", api_version="v2").status_code

    def list_configs(self, **kwargs) -> list:
        """
        Returns all configured LSS receivers with pagination support.

        Keyword Args:
            - search (str): The search string used to match against features and fields.
            - max_items (int): Maximum number of items to return.
            - max_pages (int): Maximum number of pages to return.
            - pagesize (int): Number of items per page (default is 20, maximum is 500).
            - keep_empty_params (bool): Whether to include empty parameters in the query string.

        Returns:
            list: A list of `LSSConfig` instances.
        
        Example:
            >>> lss_configs = zpa.lss.list_configs(search="example", pagesize=100)
        """
        api_url = format_url(f"{self._base_url}/lssConfig")

        # Fetch paginated data using the request executor
        list_data, error = get_paginated_data(
            request_executor=self._request_executor,
            path=api_url,
            **kwargs
        )

        if error:
            return []

        # Convert the raw data into LSSConfig objects
        return [LSSConfig(config) for config in list_data]

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
            {self._base_url}
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
            {self._base_url}
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
            {self._base_url}
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
        api_url = format_url(f"{self._base_url}/lssConfig/{lss_config_id}")

        request, error = self._request_executor.create_request(http_method, api_url, {})
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return response.status_code