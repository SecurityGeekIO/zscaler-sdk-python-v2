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
from zscaler.zpa.models.policyset_controller_v1 import PolicySetControllerV1
from zscaler.utils import format_url, snake_to_camel, convert_keys, add_id_groups
from urllib.parse import urlencode


class PolicySetControllerAPI(APIClient):
    """
    A client object for the Policy Set Controller resource.
    """

    def __init__(self, request_executor, config):
        super().__init__()
        self._request_executor = request_executor
        customer_id = config["client"].get("customerId")
        self._zpa_base_endpoint_v1 = f"/zpa/mgmtconfig/v1/admin/customers/{customer_id}"
        self._zpa_base_endpoint_v2 = f"/zpa/mgmtconfig/v1/admin/customers/{customer_id}"

    # Mapping policy types to their ZPA API equivalents
    POLICY_MAP = {
        "access": "ACCESS_POLICY",
        "capabilities": "CAPABILITIES_POLICY",
        "client_forwarding": "CLIENT_FORWARDING_POLICY",
        "clientless": "CLIENTLESS_SESSION_PROTECTION_POLICY",
        "credential": "CREDENTIAL_POLICY",
        "inspection": "INSPECTION_POLICY",
        "isolation": "ISOLATION_POLICY",
        "redirection": "REDIRECTION_POLICY",
        "siem": "SIEM_POLICY",
        "timeout": "TIMEOUT_POLICY",
    }

    def _create_conditions_v1(self, conditions: list) -> list:
        """
        Creates a dict template for feeding conditions into the ZPA Policies API when adding or updating a policy.

        Args:
            conditions (list): List of condition dicts or tuples.

        Returns:
            list: The conditions template.
        """
        template = []
        app_and_app_group_operands = []
        object_types_to_operands = {
            "CONSOLE": [],
            "MACHINE_GRP": [],
            "LOCATION": [],
            "BRANCH_CONNECTOR_GROUP": [],
            "EDGE_CONNECTOR_GROUP": [],
            "CLIENT_TYPE": [],
            "IDP": [],
            "PLATFORM": [],
            "POSTURE": [],
            "TRUSTED_NETWORK": [],
            "SAML": [],
            "SCIM": [],
            "SCIM_GROUP": [],
            "COUNTRY_CODE": [],
        }

        for condition in conditions:
            if isinstance(condition, tuple) and len(condition) == 3:
                # Handle each object type according to its pattern
                object_type = condition[0].upper()
                lhs = condition[1]
                rhs = condition[2]

                if object_type in ["APP", "APP_GROUP"]:
                    app_and_app_group_operands.append({"objectType": object_type, "lhs": "id", "rhs": rhs})
                elif object_type in object_types_to_operands:
                    if object_type == "CLIENT_TYPE":
                        object_types_to_operands[object_type].append({"objectType": object_type, "lhs": "id", "rhs": rhs})
                    elif object_type in object_types_to_operands:
                        object_types_to_operands[object_type].append({"objectType": object_type, "lhs": lhs, "rhs": rhs})
            elif isinstance(condition, dict):
                condition_template = {k: condition[k] for k in ["id", "negated", "operator"] if k in condition}
                operands = condition.get("operands", [])
                condition_template["operands"] = [{k: operand[k] for k in operand if k in operand} for operand in operands]
                template.append(condition_template)

        if app_and_app_group_operands:
            template.append({"operator": "OR", "operands": app_and_app_group_operands})
        for object_type, operands in object_types_to_operands.items():
            if operands:
                template.append({"operator": "OR", "operands": operands})

        return template

    def _create_conditions_v2(self, conditions: list) -> list:
        """
        Creates a dict template for feeding conditions into the ZPA Policies API when adding or updating a policy.

        Args:
            conditions (list): List of condition tuples where each tuple represents a specific policy condition.

        Returns:
            :obj:`list`: List containing the conditions formatted for the ZPA Policies API.
        """

        grouped_conditions = {"app_and_app_group": []}  # Specific group for APP and APP_GROUP
        template = []

        for condition in conditions:
            object_type, values = condition[0], condition[1]

            if object_type in ["app", "app_group"]:
                # Group APP and APP_GROUP together in the same operands block
                grouped_conditions["app_and_app_group"].append({"objectType": object_type.upper(), "values": values})
            elif object_type in [
                "console",
                "machine_grp",
                "location",
                "branch_connector_group",
                "edge_connector_group",
                "client_type",
            ]:
                # Each of these object types must be under individual operands blocks
                template.append({"operands": [{"objectType": object_type.upper(), "values": values}]})
            elif object_type in ["saml", "scim", "scim_group"]:
                # These types use "entryValues" with "lhs" and "rhs"
                template.append(
                    {
                        "operands": [
                            {"objectType": object_type.upper(), "entryValues": [{"lhs": v[0], "rhs": v[1]} for v in values]}
                        ]
                    }
                )
            elif object_type in ["posture", "trusted_network", "country_code", "platform"]:
                # These types use "entryValues" with "lhs" as unique ID and "rhs" as "true"/"false"
                template.append(
                    {"operands": [{"objectType": object_type.upper(), "entryValues": [{"lhs": values[0], "rhs": values[1]}]}]}
                )
            else:
                # Handle other possible object types if needed in the future
                template.append({"operands": [{"objectType": object_type.upper(), "values": values}]})

        # Add the grouped APP and APP_GROUP conditions if any were specified
        if grouped_conditions["app_and_app_group"]:
            template.append({"operands": grouped_conditions["app_and_app_group"]})

        return template

    def get_policy(self, policy_type: str, query_params=None) -> PolicySetControllerV1:
        """
        Returns the policy and rule sets for the given policy type.

        Args:
            policy_type (str): The type of policy to be returned. Accepted values are:

                |  ``access`` - returns the Access Policy
                |  ``capabilities`` - returns the Capabilities Policy
                |  ``client_forwarding`` - returns the Client Forwarding Policy
                |  ``clientless`` - returns the Clientless Session Protection Policy
                |  ``credential`` - returns the Credential Policy
                |  ``inspection`` - returns the Inspection Policy
                |  ``isolation`` - returns the Isolation Policy
                |  ``redirection`` - returns the Redirection Policy
                |  ``siem`` - returns the SIEM Policy
                |  ``timeout`` - returns the Timeout Policy

        Returns:
            PolicySetControllerV1: The resource record of the specified policy type.

        Raises:
            ValueError: If the policy_type is invalid.

        Example:
            >>> policy = zpa.policies.get_policy('access')
        """
        mapped_policy_type = self.POLICY_MAP.get(policy_type)
        if not mapped_policy_type:
            raise ValueError(f"Incorrect policy type provided: {policy_type}")

        http_method = "get".upper()
        api_url = format_url(f"""
            {self._zpa_base_endpoint_v1}
            /policySet/policyType/{mapped_policy_type}
        """)

        query_params = query_params or {}
        microtenant_id = query_params.get("microtenant_id", None)
        if microtenant_id:
            query_params["microtenantId"] = microtenant_id

        # Build the query string
        if query_params:
            encoded_query_params = urlencode(query_params)
            api_url += f"?{encoded_query_params}"

        # Prepare the request
        request, error = self._request_executor.create_request(http_method, api_url, params=query_params)
        if error:
            return (None, None, error)

        # Execute the request
        response, error = self._request_executor.execute(request)
        if error:
            return (None, response, error)

        # Handle the API response and return raw response data
        try:
            response_body = response.get_body()  # Get the raw response body
            if not response_body:
                return (None, response, None)

            return (response_body, response, None)
            
        except Exception as error:
            return (None, response, error)

    def get_rule(self, policy_type: str, rule_id: str, query_params=None) -> tuple:
        """
        Returns the specified policy rule.

        Args:
            policy_type (str): The type of policy to be returned. Accepted values are:

                |  ``access``
                |  ``capabilities``
                |  ``client_forwarding``
                |  ``clientless``
                |  ``credential``
                |  ``inspection``
                |  ``isolation``
                |  ``redirection``
                |  ``siem``
                |  ``timeout``

            rule_id (str): The unique identifier for the policy rule.

        Returns:
            PolicySetControllerV1: The resource record for the requested rule.

        Example:
            >>> rule = zpa.policies.get_rule('access', rule_id='12345')
        """
        http_method = "get".upper()
        policy_data, _, err = self.get_policy(policy_type)
        if err or not policy_data:
            return (None, None, f"Error retrieving policy for {policy_type}: {err}")

        # Get the policy ID
        policy_id = policy_data.get("id")
        if not policy_id:
            return (None, None, f"No policy ID found for policy_type: {policy_type}")

        # Construct the API URL using the retrieved policy ID
        api_url = format_url(f"""{
            self._zpa_base_endpoint_v1}
            /policySet/{policy_id}/rule/{rule_id}
        """)

        query_params = query_params or {}
        microtenant_id = query_params.get("microtenant_id", None)
        if microtenant_id:
            query_params["microtenantId"] = microtenant_id

        if query_params:
            encoded_query_params = urlencode(query_params)
            api_url += f"?{encoded_query_params}"

        # Create and execute the request
        request, error = self._request_executor\
            .create_request(http_method, api_url, params=query_params)
        if error:
            return (None, None, error)

        response, error = self._request_executor\
            .execute(request)
        if error:
            return (None, response, error)

        try:
            # Directly return the response body as a dictionary
            result = self.form_response_body(response.get_body())
        except Exception as error:
            return (None, response, error)

        return (result, response, None)

    def list_rules(self, policy_type: str, query_params=None) -> tuple:
        """
        Returns policy rules for a given policy type.

        Args:
            policy_type (str): The policy type. Accepted values are:

                |  ``access`` - returns Access Policy rules
                |  ``timeout`` - returns Timeout Policy rules
                |  ``client_forwarding`` - returns Client Forwarding Policy rules
                |  ``isolation`` - returns Isolation Policy rules
                |  ``inspection`` - returns Inspection Policy rules
                |  ``redirection`` - returns Redirection Policy rules
                |  ``credential`` - returns Credential Policy rules
                |  ``capabilities`` - returns Capabilities Policy rules
                |  ``siem`` - returns SIEM Policy rules

        Returns:
            list: A list of PolicySetControllerV1 objects.

        Example:
            >>> rules = zpa.policies.list_rules('access')
        """
        # Map the policy type to the ZPA API equivalent
        mapped_policy_type = self.POLICY_MAP.get(policy_type)
        if not mapped_policy_type:
            raise ValueError(f"Incorrect policy type provided: {policy_type}")

        http_method = "GET"
        api_url = format_url(f"""
            {self._zpa_base_endpoint_v1}
            /policySet/rules/policyType/{mapped_policy_type}
        """)

        query_params = query_params or {}
        microtenant_id = query_params.get("microtenant_id", None)
        if microtenant_id:
            query_params["microtenantId"] = microtenant_id

        # Build the query string
        if query_params:
            encoded_query_params = urlencode(query_params)
            api_url += f"?{encoded_query_params}"

        # Prepare request
        request, error = self._request_executor.create_request(http_method, api_url, params=query_params)
        if error:
            return (None, None, error)

        # Execute the request
        response, error = self._request_executor.execute(request)
        if error:
            return (None, response, error)

        try:
            # Directly return the results as a list of dictionaries
            result = [self.form_response_body(item) for item in response.get_results()]
        except Exception as error:
            return (None, response, error)

        return (result, response, None)

    def add_access_rule(
        self,
        name: str,
        action: str,
        app_connector_group_ids: list = [],
        app_server_group_ids: list = [],
        **kwargs,
    ) -> PolicySetControllerV1:
        """
        Add a new Access Policy rule.

        See the `ZPA Access Policy API reference <https://help.zscaler.com/zpa/access-policy-use-cases>`_
        for further detail on optional keyword parameter structures.

        Args:
            name (str):
                The name of the new rule.
            action (str):
                The action for the policy. Accepted values are:

                |  ``allow``
                |  ``deny``
            **kwargs:
                Optional keyword args.

        Keyword Args:
            conditions (list):
                A list of conditional rule tuples. Tuples must follow the convention: `Object Type`, `LHS value`,
                `RHS value`. If you are adding multiple values for the same object type then you will need
                a new entry for each value.
                E.g.

                .. code-block:: python

                    [('app', 'id', '99999'),
                    ('app', 'id', '88888'),
                    ('app_group', 'id', '77777),
                    ('client_type', 'zpn_client_type_exporter', 'zpn_client_type_zapp'),
                    ('trusted_network', 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxx', True)]
            custom_msg (str):
                A custom message.
            description (str):
                A description for the rule.
            app_connector_group_ids (:obj:`list` of :obj:`str`):
                A list of application connector IDs that will be attached to the access policy rule.
            app_server_group_ids (:obj:`list` of :obj:`str`):
                A list of application server group IDs that will be attached to the access policy rule.

        Returns:
            PolicySetControllerV1: The resource record of the newly created access policy rule.

        """
        policy_id = self.get_policy("access").id
        api_url = format_url(f"{self._zpa_base_endpoint_v1}/policySet/{policy_id}/rule")

        payload = {
            "name": name,
            "action": action.upper(),
            "appConnectorGroups": [{"id": group_id} for group_id in app_connector_group_ids],
            "appServerGroups": [{"id": group_id} for group_id in app_server_group_ids],
        }

        add_id_groups(self.reformat_params, kwargs, payload)

        conditions = kwargs.pop("conditions", [])
        if conditions:
            payload["conditions"] = self._create_conditions_v1(conditions)

        for key, value in kwargs.items():
            payload[snake_to_camel(key)] = value

        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request("post", api_url, payload, params)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return PolicySetControllerV1(response.get_body())

    def update_access_rule(
        self,
        rule_id: str,
        app_connector_group_ids: list = None,
        app_server_group_ids: list = None,
        **kwargs,
    ) -> PolicySetControllerV1:
        """
        Update an existing policy rule.

        Ensure you are using the correct arguments for the policy type that you want to update.

        Args:
            rule_id (str):
                The unique identifier for the rule to be updated.
            **kwargs:
                Optional keyword args.

        Keyword Args:
            action (str):
                The action for the policy. Accepted values are:

                |  ``allow``
                |  ``deny``
            app_connector_group_ids (:obj:`list` of :obj:`str`):
                A list of application connector IDs that will be attached to the access policy rule. Defaults to an empty list.
            app_server_group_ids (:obj:`list` of :obj:`str`):
                A list of server group IDs that will be attached to the access policy rule. Defaults to an empty list.

        Returns:
            PolicySetControllerV1: The updated policy rule record.

        Examples:
            Update the name and description of the Access Policy Rule:

            >>> zpa.policies.update_access_rule(
            ...    rule_id="999999",
            ...    name='Update_Access_Policy_Rule_v1',
            ...    description='Update_Access_Policy_Rule_v1',
            ... )
        """
        policy_id = self.get_policy("access").id
        api_url = format_url(f"{self._zpa_base_endpoint_v1}/policySet/{policy_id}/rule/{rule_id}")

        current_rule = self.get_rule("access", rule_id)
        payload = current_rule.request_format()

        payload["appConnectorGroups"] = [{"id": group_id} for group_id in app_connector_group_ids or []]
        payload["appServerGroups"] = [{"id": group_id} for group_id in app_server_group_ids or []]

        add_id_groups(self.reformat_params, kwargs, payload)

        for key, value in kwargs.items():
            if key == "conditions":
                payload["conditions"] = self._create_conditions_v1(value)
            else:
                payload[snake_to_camel(key)] = value

        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request("put", api_url, payload, params)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return PolicySetControllerV1(response.get_body())

    def add_timeout_rule(self, name: str, **kwargs) -> dict:
        """
        Add a new Timeout Policy rule.

        See the `ZPA Timeout Policy API reference <https://help.zscaler.com/zpa/timeout-policy-use-cases>`_
        for further detail on optional keyword parameter structures.

        Args:
            name (str):
                The name of the new rule.
            **kwargs:
                Optional parameters.

        Keyword Args:
            conditions (list):
                A list of conditional rule tuples. Tuples must follow the convention: `Object Type`, `LHS value`,
                `RHS value`. If you are adding multiple values for the same object type then you will need
                a new entry for each value.
                E.g.

                .. code-block:: python

                    [('app', 'id', '926196382959075416'),
                    ('app', 'id', '926196382959075417'),
                    ('app_group', 'id', '926196382959075332),
                    ('client_type', 'zpn_client_type_exporter', 'zpn_client_type_zapp'),
                    ('trusted_network', 'b15e4cad-fa6e-8182-9fc3-8125ee6a65e1', True)]
            custom_msg (str):
                A custom message.
            description (str):
                A description for the rule.
            re_auth_idle_timeout (int):
                The re-authentication idle timeout value in seconds.
            re_auth_timeout (int):
                The re-authentication timeout value in seconds.
        """
        http_method = "post".upper()
        policy_id = self.get_policy("timeout").id
        api_url = format_url(f"{self._zpa_base_endpoint_v1}/policySet/{policy_id}/rule")

        payload = {
            "name": name,
            "action": "RE_AUTH",
            "conditions": self._create_conditions_v1(kwargs.pop("conditions", [])),
            "reauthTimeout": kwargs.get("re_auth_timeout", 172800),
            "reauthIdleTimeout": kwargs.get("re_auth_idle_timeout", 600),
        }

        for key, value in kwargs.items():
            payload[snake_to_camel(key)] = value

        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, payload, params)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return response.get_body()

    def update_timeout_rule(self, rule_id: str, **kwargs) -> dict:
        """
        Update an existing policy rule.

        Ensure you are using the correct arguments for the policy type that you want to update.

        Args:
            rule_id (str):
                The unique identifier for the rule to be updated.
            **kwargs:
                Optional keyword args.

        Keyword Args:
            conditions (list):
                A list of conditional rule tuples. Tuples must follow the convention: `Object Type`, `LHS value`,
                `RHS value`. If you are adding multiple values for the same object type then you will need
                a new entry for each value.
                E.g.

                .. code-block:: python

                    [('app', 'id', '926196382959075416'),
                    ('app', 'id', '926196382959075417'),
                    ('app_group', 'id', '926196382959075332),
                    ('client_type', 'zpn_client_type_exporter', 'zpn_client_type_zapp'),
                    ('trusted_network', 'b15e4cad-fa6e-8182-9fc3-8125ee6a65e1', True)]
            custom_msg (str):
                A custom message.
            description (str):
                A description for the rule.
            re_auth_idle_timeout (int):
                The re-authentication idle timeout value in seconds.
            re_auth_timeout (int):
                The re-authentication timeout value in seconds.

        Returns:

        Examples:
            Updates the name only for a Timeout Policy rule:

            >>> zpa.policies.update_timeout_rule('99999', name='new_rule_name')

            Updates the description for a Timeout Policy rule:

            >>> zpa.policies.update_timeout_rule('888888', description='Updated Description')
        """
        http_method = "put".upper()
        policy_id = self.get_policy("timeout").id
        api_url = format_url(f"{self._zpa_base_endpoint_v1}/policySet/{policy_id}/rule/{rule_id}")

        current_rule = self.get_rule("timeout", rule_id)
        payload = convert_keys(current_rule)
        payload["action"] = "RE_AUTH"

        for key, value in kwargs.items():
            if key == "conditions":
                payload["conditions"] = self._create_conditions_v1(value)
            else:
                payload[snake_to_camel(key)] = value

        payload["reauthTimeout"] = kwargs.get("re_auth_timeout", 172800)
        payload["reauthIdleTimeout"] = kwargs.get("re_auth_idle_timeout", 600)

        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, payload, params)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return response.get_body()

    def add_client_forwarding_rule(self, name: str, action: str, **kwargs) -> dict:
        """
        Add a new Client Forwarding Policy rule.

        See the
        `ZPA Client Forwarding Policy API reference <https://help.zscaler.com/zpa/client-forwarding-policy-use-cases>`_
        for further detail on optional keyword parameter structures.

        Args:
            name (str):
                The name of the new rule.
            action (str):
                The action for the policy. Accepted values are:

                |  ``intercept``
                |  ``intercept_accessible``
                |  ``bypass``
            **kwargs:
                Optional keyword args.

        Keyword Args:
            conditions (list):
                A list of conditional rule tuples. Tuples must follow the convention: `Object Type`, `LHS value`,
                `RHS value`. If you are adding multiple values for the same object type then you will need
                a new entry for each value.
                E.g.

                .. code-block:: python

                    [('app', 'id', '926196382959075416'),
                    ('app', 'id', '926196382959075417'),
                    ('app_group', 'id', '926196382959075332),
                    ('client_type', 'zpn_client_type_exporter', 'zpn_client_type_zapp'),
                    ('trusted_network', 'b15e4cad-fa6e-8182-9fc3-8125ee6a65e1', True)]
            custom_msg (str):
                A custom message.
            description (str):
                A description for the rule.

        Returns:

        Examples:
            Add a new Client Forwarding Policy rule:

            >>> zpa.policies.add_client_forwarding_rule(
            ...    name='Add_Forwarding_Rule_v1',
            ...    description='Update_Forwarding_Rule_v1',
            ...    action='isolate',
            ...    conditions=[
            ...         ("app", ["216199618143361683"]),
            ...         ("app_group", ["216199618143360301"]),
            ...         ("scim_group", "idp_id", "scim_group_id"),
            ...         ("scim_group", "idp_id", "scim_group_id"),
            ...     ],
            ... )

        """
        http_method = "post".upper()
        policy_id = self.get_policy("client_forwarding").id
        api_url = format_url(f"{self._zpa_base_endpoint_v1}/policySet/{policy_id}/rule")

        payload = {
            "name": name,
            "action": action.upper(),
            "conditions": self._create_conditions_v1(kwargs.pop("conditions", [])),
        }

        for key, value in kwargs.items():
            payload[snake_to_camel(key)] = value

        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, payload, params)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return response.get_body()

    def update_client_forwarding_rule(self, rule_id: str, **kwargs) -> dict:
        """
        Update an existing Client Forwarding Policy rule.

        Ensure you are using the correct arguments for the policy type that you want to update.

        Args:
            rule_id (str):
                The unique identifier for the rule to be updated.
            **kwargs:
                Optional keyword args.

        Keyword Args:
            action (str):
                The action for the policy. Accepted values are:

                |  ``intercept``
                |  ``intercept_accessible``
                |  ``bypass``
            description (str):
                Additional information about the Client Forwarding Policy rule.
            enabled (bool):
                Whether or not the Client Forwarding Policy rule. is enabled.
            rule_order (str):
                The rule evaluation order number of the rule.
            conditions (list):
                A list of conditional rule tuples. Tuples must follow the convention: `Object Type`, `LHS value`,
                `RHS value`. If you are adding multiple values for the same object type then you will need
                a new entry for each value.
                E.g.

                .. code-block:: python

                    [('app', 'id', 'app_segment_id'),
                    ('app', 'id', 'app_segment_id'),
                    ('app_group', 'id', 'segment_group_id),
                    ("scim_group", "idp_id", "scim_group_id"),
                    ("scim_group", "idp_id", "scim_group_id"),
                    ('client_type', 'zpn_client_type_exporter')]

        Returns:

        Examples:
            Updates the name only for an Client Forwarding Policy rule:

            >>> zpa.policies.update_client_forwarding_rule(
            ...    rule_id='216199618143320419',
            ...    name='Update_Forwarding_Rule_v1',
            ...    description='Update_Forwarding_Rule_v1',
            ...    action='isolate',
            ...    conditions=[
            ...         ("app", ["216199618143361683"]),
            ...         ("app_group", ["216199618143360301"]),
            ...         ("scim_group", "idp_id", "scim_group_id"),
            ...         ("scim_group", "idp_id", "scim_group_id"),
            ...     ],
            ... )
        """
        http_method = "put".upper()
        policy_id = self.get_policy("client_forwarding").id
        api_url = format_url(f"{self._zpa_base_endpoint_v1}/policySet/{policy_id}/rule/{rule_id}")

        current_rule = self.get_rule("client_forwarding", rule_id)
        payload = convert_keys(current_rule)

        for key, value in kwargs.items():
            if key == "conditions":
                payload["conditions"] = self._create_conditions_v1(value)
            else:
                payload[snake_to_camel(key)] = value

        payload["action"] = kwargs.pop("action").upper()

        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, payload, params)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return response.get_body()

    def add_isolation_rule(self, name: str, action: str, zpn_isolation_profile_id: str, **kwargs) -> dict:
        """
        Add a new Isolation Policy rule.

        See the
        `ZPA Isolation Policy API reference <https://help.zscaler.com/zpa/configuring-isolation-policies-using-api>`_
        for further detail on optional keyword parameter structures.

        Args:
            name (str):
                The name of the new rule.
            action (str):
                The action for the policy. Accepted values are:

                |  ``isolate``
                |  ``bypass_isolate``
            **kwargs:
                Optional keyword args.

        Keyword Args:
            conditions (list):
                A list of conditional rule tuples. Tuples must follow the convention: `Object Type`, `LHS value`,
                `RHS value`. If you are adding multiple values for the same object type then you will need
                a new entry for each value.
                E.g.

                .. code-block:: python

                    [('app', 'id', '926196382959075416'),
                    ('app', 'id', '926196382959075417'),
                    ('app_group', 'id', '926196382959075332),
                    ('client_type', 'zpn_client_type_exporter')]
            zpn_isolation_profile_id (str):
                The isolation profile ID associated with the rule
            description (str):
                A description for the rule.

        Returns:

        """
        http_method = "post".upper()
        policy_id = self.get_policy("isolation").id
        api_url = format_url(f"{self._zpa_base_endpoint_v1}/policySet/{policy_id}/rule")

        payload = {
            "name": name,
            "action": action.upper(),
            "zpnIsolationProfileId": zpn_isolation_profile_id,
            "conditions": self._create_conditions_v1(kwargs.pop("conditions", [])),
        }

        client_type_present = any(
            cond.get("operands", [{}])[0].get("objectType", "") == "CLIENT_TYPE" for cond in payload["conditions"]
        )
        if not client_type_present:
            payload["conditions"].append(
                {"operator": "OR", "operands": [{"objectType": "CLIENT_TYPE", "lhs": "id", "rhs": "zpn_client_type_exporter"}]}
            )

        for key, value in kwargs.items():
            payload[snake_to_camel(key)] = value

        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, payload, params)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return response.get_body()

    def update_isolation_rule(self, rule_id: str, **kwargs) -> dict:
        """
        Update an existing client isolation policy rule.

        Ensure you are using the correct arguments for the policy type that you want to update.

        Args:
            rule_id (str):
                The unique identifier for the rule to be updated.
            **kwargs:
                Optional keyword args.

        Keyword Args:
            action (str):
                The action for the policy. Accepted values are:

                |  ``isolate``
                |  ``bypass_isolate``
            description (str):
                Additional information about the client forwarding policy rule.
            enabled (bool):
                Whether or not the client forwarding policy rule is enabled.
            rule_order (str):
                The rule evaluation order number of the rule.
            zpn_isolation_profile_id (str):
                The unique identifier of the inspection profile. This field is applicable only for inspection policies.
            conditions (list):
                A list of conditional rule tuples. Tuples must follow the convention: `Object Type`, `LHS value`,
                `RHS value`. If you are adding multiple values for the same object type then you will need
                a new entry for each value.
                E.g.

                .. code-block:: python

                    [('app', 'id', '926196382959075416'),
                    ('app', 'id', '926196382959075417'),
                    ('app_group', 'id', '926196382959075332),
                    ('client_type', 'zpn_client_type_exporter')]

        Returns:

        Examples:
            Updates the name only for an Isolation Policy rule:

            >>> zpa.policiesv2.update_isolation_rule(
            ...    rule_id='216199618143320419',
            ...    name='Update_Isolation_Rule_v2',
            ...    description='Update_Isolation_Rule_v2',
            ...    action='isolate',
            ...    conditions=[
            ...         ("app", ["216199618143361683"]),
            ...         ("app_group", ["216199618143360301"]),
            ...         ("scim_group", [("216199618143191058", "2079468"), ("216199618143191058", "2079446")]),
            ...     ],
            ... )
        """
        http_method = "put".upper()
        policy_id = self.get_policy("isolation").id
        api_url = format_url(f"{self._zpa_base_endpoint_v1}/policySet/{policy_id}/rule/{rule_id}")

        current_rule = self.get_rule("isolation", rule_id)
        payload = convert_keys(current_rule)

        for key, value in kwargs.items():
            if key == "conditions":
                payload["conditions"] = self._create_conditions_v1(value)
            else:
                payload[snake_to_camel(key)] = value

        client_type_present = any(
            cond.get("operands", [{}])[0].get("objectType", "") == "CLIENT_TYPE" for cond in payload["conditions"]
        )
        if not client_type_present:
            payload["conditions"].append(
                {"operator": "OR", "operands": [{"objectType": "CLIENT_TYPE", "lhs": "id", "rhs": "zpn_client_type_exporter"}]}
            )

        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, payload, params)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return response.get_body()

    def add_app_protection_rule(self, name: str, action: str, zpn_inspection_profile_id: str, **kwargs) -> dict:
        """
        Add a new App Protection Policy rule.
        """
        http_method = "post".upper()
        policy_id = self.get_policy("inspection").id
        api_url = format_url(f"{self._zpa_base_endpoint_v1}/policySet/{policy_id}/rule")

        payload = {
            "name": name,
            "action": action.upper(),
            "zpnInspectionProfileId": zpn_inspection_profile_id,
            "conditions": self._create_conditions_v1(kwargs.pop("conditions", [])),
        }

        for key, value in kwargs.items():
            payload[snake_to_camel(key)] = value

        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, payload, params)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return response.get_body()

    def update_app_protection_rule(self, rule_id: str, **kwargs) -> dict:
        """
        Update an existing app protection policy rule.

        Ensure you are using the correct arguments for the policy type that you want to update.

        Args:
            rule_id (str):
                The unique identifier for the rule to be updated.
            **kwargs:
                Optional keyword args.

        Keyword Args:
            action (str):
                The action for the policy. Accepted values are:

                |  ``isolate``
                |  ``bypass_isolate``
            description (str):
                Additional information about the app protection policy rule.
            enabled (bool):
                Whether or not the app protection policy rule is enabled.
            rule_order (str):
                The rule evaluation order number of the rule.
            zpn_inspection_profile_id (str):
                The unique identifier of the inspection profile. This field is applicable only for inspection policies.
            conditions (list):
                A list of conditional rule tuples. Tuples must follow the convention: `Object Type`, `LHS value`,
                `RHS value`. If you are adding multiple values for the same object type then you will need
                a new entry for each value.
                E.g.

                .. code-block:: python

                    [('app', 'id', '926196382959075416'),
                    ('app', 'id', '926196382959075417'),
                    ('app_group', 'id', '926196382959075332),
                    ('client_type', 'zpn_client_type_exporter')]

        Returns:

        Examples:
            Updates the name only for an Inspection Policy rule:

            >>> zpa.policiesv2.update_app_protection_rule(
            ...    rule_id='216199618143320419',
            ...    name='Update_Inspection_Rule_v2',
            ...    description='Update_Inspection_Rule_v2',
            ...    action='inspect',
            ...    zpn_inspection_profile_id='216199618143363055'
            ...    conditions=[
            ...         ("app", ["216199618143361683"]),
            ...         ("app_group", ["216199618143360301"]),
            ...         ("scim_group", [("216199618143191058", "2079468"), ("216199618143191058", "2079446")]),
            ...     ],
            ... )
        """
        http_method = "put".upper()
        policy_id = self.get_policy("inspection").id
        api_url = format_url(f"{self._zpa_base_endpoint_v1}/policySet/{policy_id}/rule/{rule_id}")

        current_rule = self.get_rule("inspection", rule_id)
        payload = convert_keys(current_rule)

        for key, value in kwargs.items():
            if key == "conditions":
                payload["conditions"] = self._create_conditions_v1(value)
            else:
                payload[snake_to_camel(key)] = value

        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, payload, params)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return response.get_body()

    def add_access_rule_v2(self, name: str, action: str, **kwargs) -> dict:
        """
        Add a new Access Policy rule.

        See the `ZPA Access Policy API reference <https://help.zscaler.com/zpa/access-policy-use-cases>`_
        for further detail on optional keyword parameter structures.

        Args:
            name (str):
                The name of the new rule.
            action (str):
                The action for the policy. Accepted values are:

                |  ``allow``
                |  ``deny``
            **kwargs:
                Optional keyword args.

        Keyword Args:
            custom_msg (str):
                A custom message.
            description (str):
                A description for the rule.
            app_connector_group_ids (:obj:`list` of :obj:`str`):
                A list of application connector IDs that will be attached to the access policy rule.
            app_server_group_ids (:obj:`list` of :obj:`str`):
                A list of application server group IDs that will be attached to the access policy rule.

            conditions (list):
                A list of conditional rule tuples. Tuples must follow the convention: `Object Type`, `LHS value`,
                `RHS value`. If you are adding multiple values for the same object type then you will need
                a new entry for each value.
                E.g.

                .. code-block:: python

                    [('app', 'id', '99999'),
                    ('app', 'id', '88888'),
                    ('app_group', 'id', '77777),
                    ('client_type', 'zpn_client_type_exporter', 'zpn_client_type_zapp'),
                    ('trusted_network', 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxx', True)]

        Returns:
            :obj:`Box`: The resource record of the newly created access policy rule.

        """
        http_method = "post".upper()
        policy_id = self.get_policy("access").id
        api_url = format_url(f"{self._zpa_base_endpoint_v2}/policySet/{policy_id}/rule")

        payload = {
            "name": name,
            "action": action.upper(),
            "conditions": self._create_conditions_v2(kwargs.pop("conditions", [])),
        }

        add_id_groups(self.reformat_params, kwargs, payload)

        for key, value in kwargs.items():
            payload[snake_to_camel(key)] = value

        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, payload, params)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return response.get_body()

    def update_access_rule_v2(self, rule_id: str, **kwargs) -> dict:
        """
        Update an existing policy rule.

        Ensure you are using the correct arguments for the policy type that you want to update.

        Args:
            rule_id (str):
                The unique identifier for the rule to be updated.
            app_connector_group_ids (:obj:`list` of :obj:`str`, optional):
                A list of application connector IDs that will be attached to the access policy rule. Defaults to an empty list.
            app_server_group_ids (:obj:`list` of :obj:`str`, optional):
                A list of server group IDs that will be attached to the access policy rule. Defaults to an empty list.

            **kwargs:
                Optional keyword args.

        Keyword Args:
            action (str):
                The action for the policy. Accepted values are:
                |  ``ALLOW``
                |  ``DENY``
            custom_msg (str):
                A custom message.
            description (str):
                A description for the rule.
            conditions (list):
                A list of conditional rule tuples. Tuples must follow the convention: `Object Type`, `LHS value`,
                `RHS value`. If you are adding multiple values for the same object type then you will need
                a new entry for each value.

        Returns:

        Examples:
            Updates the description for an Access Policy rule:

            >>> zpa.policiesv2.update_access_rule(
            ...    rule_id='216199618143320419',
            ...    description='Updated Description',
            ...    action='ALLOW',
            ...    conditions=[
            ...         ("client_type", ['zpn_client_type_exporter', 'zpn_client_type_zapp']),
            ...     ],
            ... )
        """
        http_method = "put".upper()
        policy_id = self.get_policy("access").id
        api_url = format_url(f"{self._zpa_base_endpoint_v2}/policySet/{policy_id}/rule/{rule_id}")

        current_rule = self.get_rule("access", rule_id)
        payload = convert_keys(current_rule)

        if "conditions" in payload and "conditions" not in kwargs:
            del payload["conditions"]

        for key, value in kwargs.items():
            if key == "conditions":
                payload["conditions"] = self._create_conditions_v2(value)
            elif key == "action":
                payload["action"] = value.upper()
            else:
                payload[snake_to_camel(key)] = value

        add_id_groups(self.reformat_params, kwargs, payload)

        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, payload, params)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return response.get_body()

    def add_timeout_rule_v2(self, name: str, **kwargs) -> dict:
        """
        Update an existing policy rule.

        Ensure you are using the correct arguments for the policy type that you want to update.

        Args:
            rule_id (str):
                The unique identifier for the rule to be updated.
            app_connector_group_ids (:obj:`list` of :obj:`str`, optional):
                A list of application connector IDs that will be attached to the access policy rule. Defaults to an empty list.
            app_server_group_ids (:obj:`list` of :obj:`str`, optional):
                A list of server group IDs that will be attached to the access policy rule. Defaults to an empty list.

            **kwargs:
                Optional keyword args.

        Keyword Args:
            action (str):
                The action for the policy. Accepted values are:
                |  ``ALLOW``
                |  ``DENY``
            custom_msg (str):
                A custom message.
            description (str):
                A description for the rule.
            conditions (list):
                A list of conditional rule tuples. Tuples must follow the convention: `Object Type`, `LHS value`,
                `RHS value`. If you are adding multiple values for the same object type then you will need
                a new entry for each value.

        Returns:

        Examples:
            Updates the description for an Access Policy rule:

            >>> zpa.policiesv2.update_access_rule(
            ...    rule_id='216199618143320419',
            ...    description='Updated Description',
            ...    action='ALLOW',
            ...    conditions=[
            ...         ("client_type", ['zpn_client_type_exporter', 'zpn_client_type_zapp']),
            ...     ],
            ... )
        """
        http_method = "post".upper()
        policy_id = self.get_policy("timeout").id
        api_url = format_url(f"{self._zpa_base_endpoint_v2}/policySet/{policy_id}/rule")

        payload = {
            "name": name,
            "action": "RE_AUTH",
            "conditions": self._create_conditions_v2(kwargs.pop("conditions", [])),
            "reauthTimeout": kwargs.get("re_auth_timeout", 172800),
            "reauthIdleTimeout": kwargs.get("re_auth_idle_timeout", 600),
        }

        for key, value in kwargs.items():
            payload[snake_to_camel(key)] = value

        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, payload, params)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return response.get_body()

    def update_timeout_rule_v2(self, rule_id: str, **kwargs) -> dict:
        """
        Update an existing policy rule.

        Ensure you are using the correct arguments for the policy type that you want to update.

        Args:
            rule_id (str):
                The unique identifier for the rule to be updated.
            **kwargs:
                Optional keyword args.

        Keyword Args:
            conditions (list):
                A list of conditional rule tuples. Tuples must follow the convention: `Object Type`, `LHS value`,
                `RHS value`. If you are adding multiple values for the same object type then you will need
                a new entry for each value.
                E.g.

                .. code-block:: python

                    [('app', 'id', '926196382959075416'),
                    ('app', 'id', '926196382959075417'),
                    ('app_group', 'id', '926196382959075332),
                    ('client_type', 'zpn_client_type_exporter', 'zpn_client_type_zapp'),
                    ('trusted_network', 'b15e4cad-fa6e-8182-9fc3-8125ee6a65e1', True)]
            custom_msg (str):
                A custom message.
            description (str):
                A description for the rule.
            re_auth_idle_timeout (int):
                The re-authentication idle timeout value in seconds.
            re_auth_timeout (int):
                The re-authentication timeout value in seconds.

        Returns:

        Examples:
            Updates the name only for a Timeout Policy rule:

            >>> zpa.policies.update_timeout_rule('99999', name='new_rule_name')

            Updates the description for a Timeout Policy rule:

            >>> zpa.policies.update_timeout_rule('888888', description='Updated Description')
        """
        http_method = "put".upper()
        policy_id = self.get_policy("timeout").id
        api_url = format_url(f"{self._zpa_base_endpoint_v2}/policySet/{policy_id}/rule/{rule_id}")

        current_rule = self.get_rule("timeout", rule_id)
        payload = convert_keys(current_rule)

        if "conditions" in payload and "conditions" not in kwargs:
            del payload["conditions"]

        for key, value in kwargs.items():
            if key == "conditions":
                payload["conditions"] = self._create_conditions_v2(value)
            elif key == "action":
                payload["action"] = value.upper()
            else:
                payload[snake_to_camel(key)] = value

        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, payload, params)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return response.get_body()

    def add_client_forwarding_rule_v2(self, name: str, action: str, **kwargs) -> dict:
        """
        Add a new Client Forwarding Policy rule.

        See the
        `ZPA Client Forwarding Policy API reference <https://help.zscaler.com/zpa/client-forwarding-policy-use-cases>`_
        for further detail on optional keyword parameter structures.

        Args:
            name (str):
                The name of the new rule.
            action (str):
                The action for the policy. Accepted values are:

                |  ``bypass``
                |  ``intercept``
                |  ``intercept_accessible``
            **kwargs:
                Optional keyword args.

        Keyword Args:
            conditions (list):
                A list of conditional rule tuples. Tuples must follow the convention: `Object Type`, `LHS value`,
                `RHS value`. If you are adding multiple values for the same object type then you will need
                a new entry for each value.
                E.g.

                .. code-block:: python

                    [('app', 'id', '926196382959075416'),
                    ('app', 'id', '926196382959075417'),
                    ('app_group', 'id', '926196382959075332),
                    ('client_type', 'zpn_client_type_exporter', 'zpn_client_type_zapp'),
                    ('trusted_network', 'b15e4cad-fa6e-8182-9fc3-8125ee6a65e1', True)]
            custom_msg (str):
                A custom message.
            description (str):
                A description for the rule.
        """
        http_method = "post".upper()
        policy_id = self.get_policy("client_forwarding").id
        api_url = format_url(f"{self._zpa_base_endpoint_v2}/policySet/{policy_id}/rule")

        payload = {
            "name": name,
            "action": action.upper(),
            "conditions": self._create_conditions_v2(kwargs.pop("conditions", [])),
        }

        for key, value in kwargs.items():
            payload[snake_to_camel(key)] = value

        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, payload, params)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return response.get_body()

    def update_client_forwarding_rule_v2(self, rule_id: str, **kwargs) -> dict:
        """
        Update an existing client forwarding policy rule.

        Ensure you are using the correct arguments for the policy type that you want to update.

        Args:

            rule_id (str):
                The unique identifier for the rule to be updated.
            **kwargs:
                Optional keyword args.

        Keyword Args:
            action (str):
                The action for the policy. Accepted values are:

                |  ``bypass``
                |  ``intercept``
                |  ``intercept_accessible``
            description (str):
                Additional information about the client forwarding policy rule.
            enabled (bool):
                Whether or not the client forwarding policy rule is enabled.
            rule_order (str):
                The rule evaluation order number of the rule.

            conditions (list):
                A list of conditional rule tuples. Tuples must follow the convention: `Object Type`, `LHS value`,
                `RHS value`. If you are adding multiple values for the same object type then you will need
                a new entry for each value.
                E.g.

                .. code-block:: python

                    ("client_type",
                        ['zpn_client_type_edge_connector',
                        'zpn_client_type_branch_connector',
                        'zpn_client_type_machine_tunnel',
                        'zpn_client_type_zapp', 'zpn_client_type_zapp_partner'
                    ]),

        Examples:
            Updates the name only for an Access Policy rule:

            >>> zpa.policiesv2.update_client_forwarding_rule(
            ...    rule_id='216199618143320419',
            ...    name='Update_Redirection_Rule_v2',
            ...    description='Update_Redirection_Rule_v2',
            ...    action='redirect_default',
            ...    conditions=[
            ...         ("client_type",
            ...         ['zpn_client_type_edge_connector',
            ...          'zpn_client_type_branch_connector',
            ...          'zpn_client_type_machine_tunnel',
            ...          'zpn_client_type_zapp',
            ...          'zpn_client_type_zapp_partner']),
            ...     ],
            ... )
        """
        http_method = "put".upper()
        policy_id = self.get_policy("client_forwarding").id
        api_url = format_url(f"{self._zpa_base_endpoint_v2}/policySet/{policy_id}/rule/{rule_id}")

        current_rule = self.get_rule("client_forwarding", rule_id)
        payload = convert_keys(current_rule)

        if "conditions" in payload and "conditions" not in kwargs:
            del payload["conditions"]

        for key, value in kwargs.items():
            if key == "conditions":
                payload["conditions"] = self._create_conditions_v2(value)
            elif key == "action":
                payload["action"] = value.upper()
            else:
                payload[snake_to_camel(key)] = value

        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, payload, params)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return response.get_body()

    def add_isolation_rule_v2(self, name: str, action: str, zpn_isolation_profile_id: str, **kwargs) -> dict:
        """
        Add a new Isolation Policy rule.

        See the
        `ZPA Isolation Policy API reference <https://help.zscaler.com/zpa/configuring-isolation-policies-using-api>`_
        for further detail on optional keyword parameter structures.

        Args:
            name (str):
                The name of the new rule.
            action (str):
                The action for the policy. Accepted values are:

                |  ``isolate``
                |  ``bypass_isolate``
            **kwargs:
                Optional keyword args.

        Keyword Args:
            conditions (list):
                A list of conditional rule tuples. Tuples must follow the convention: `Object Type`, `LHS value`,
                `RHS value`. If you are adding multiple values for the same object type then you will need
                a new entry for each value.
                E.g.

                .. code-block:: python

                    [('app', 'id', '926196382959075416'),
                    ('app', 'id', '926196382959075417'),
                    ('app_group', 'id', '926196382959075332),
                    ('client_type', 'zpn_client_type_exporter')]
            zpn_isolation_profile_id (str):
                The isolation profile ID associated with the rule
            description (str):
                A description for the rule.
        """
        http_method = "post".upper()
        policy_id = self.get_policy("isolation").id
        api_url = format_url(f"{self._zpa_base_endpoint_v2}/policySet/{policy_id}/rule")

        payload = {
            "name": name,
            "action": action.upper(),
            "zpnIsolationProfileId": zpn_isolation_profile_id,
            "conditions": self._create_conditions_v2(kwargs.pop("conditions", [])),
        }

        # Ensure client type condition exists
        payload["conditions"].append({"operands": [{"objectType": "CLIENT_TYPE", "values": ["zpn_client_type_exporter"]}]})

        for key, value in kwargs.items():
            payload[snake_to_camel(key)] = value

        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, payload, params)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return response.get_body()

    def update_isolation_rule_v2(self, rule_id: str, **kwargs) -> dict:
        """
        Update an existing client isolation policy rule.

        Ensure you are using the correct arguments for the policy type that you want to update.

        Args:
            rule_id (str):
                The unique identifier for the rule to be updated.
            **kwargs:
                Optional keyword args.

        Keyword Args:
            action (str):
                The action for the policy. Accepted values are:

                |  ``isolate``
                |  ``bypass_isolate``
            description (str):
                Additional information about the client forwarding policy rule.
            enabled (bool):
                Whether or not the client forwarding policy rule is enabled.
            rule_order (str):
                The rule evaluation order number of the rule.
            zpn_isolation_profile_id (str):
                The unique identifier of the inspection profile. This field is applicable only for inspection policies.
            conditions (list):
                A list of conditional rule tuples. Tuples must follow the convention: `Object Type`, `LHS value`,
                `RHS value`. If you are adding multiple values for the same object type then you will need
                a new entry for each value.
                E.g.

                .. code-block:: python

                    [('app', 'id', '926196382959075416'),
                    ('app', 'id', '926196382959075417'),
                    ('app_group', 'id', '926196382959075332),
                    ('client_type', 'zpn_client_type_exporter')]

        Examples:
            Updates the name only for an Isolation Policy rule:

            >>> zpa.policiesv2.update_isolation_rule_v1(
            ...    rule_id='216199618143320419',
            ...    name='Update_Isolation_Rule_v2',
            ...    description='Update_Isolation_Rule_v2',
            ...    action='isolate',
            ...    conditions=[
            ...         ("app", ["216199618143361683"]),
            ...         ("app_group", ["216199618143360301"]),
            ...         ("scim_group", [("216199618143191058", "2079468"), ("216199618143191058", "2079446")]),
            ...     ],
            ... )
        """
        http_method = "put".upper()
        policy_id = self.get_policy("isolation").id
        api_url = format_url(f"{self._zpa_base_endpoint_v2}/policySet/{policy_id}/rule/{rule_id}")

        current_rule = self.get_rule("isolation", rule_id)
        payload = convert_keys(current_rule)

        if "conditions" in payload and "conditions" not in kwargs:
            del payload["conditions"]

        for key, value in kwargs.items():
            if key == "conditions":
                payload["conditions"] = self._create_conditions_v2(value)
            else:
                payload[snake_to_camel(key)] = value

        # Ensure client type condition exists
        payload["conditions"].append({"operands": [{"objectType": "CLIENT_TYPE", "values": ["zpn_client_type_exporter"]}]})

        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, payload, params)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return response.get_body()

    def add_app_protection_rule_v2(self, name: str, action: str, zpn_inspection_profile_id: str, **kwargs) -> dict:
        """
        Update an existing app protection policy rule.

        Ensure you are using the correct arguments for the policy type that you want to update.

        Args:
            rule_id (str):
                The unique identifier for the rule to be updated.
            **kwargs:
                Optional keyword args.

        Keyword Args:
            action (str):
                The action for the policy. Accepted values are:

                |  ``isolate``
                |  ``bypass_isolate``
            description (str):
                Additional information about the app protection policy rule.
            enabled (bool):
                Whether or not the app protection policy rule is enabled.
            rule_order (str):
                The rule evaluation order number of the rule.
            zpn_inspection_profile_id (str):
                The unique identifier of the inspection profile. This field is applicable only for inspection policies.
            conditions (list):
                A list of conditional rule tuples. Tuples must follow the convention: `Object Type`, `LHS value`,
                `RHS value`. If you are adding multiple values for the same object type then you will need
                a new entry for each value.
                E.g.

                .. code-block:: python

                    [('app', 'id', '926196382959075416'),
                    ('app', 'id', '926196382959075417'),
                    ('app_group', 'id', '926196382959075332),
                    ('client_type', 'zpn_client_type_exporter')]

        Examples:
            Updates the name only for an Inspection Policy rule:

            >>> zpa.policiesv2.update_app_protection_rule(
            ...    rule_id='216199618143320419',
            ...    name='Update_Inspection_Rule_v2',
            ...    description='Update_Inspection_Rule_v2',
            ...    action='inspect',
            ...    zpn_inspection_profile_id='216199618143363055'
            ...    conditions=[
            ...         ("app", ["216199618143361683"]),
            ...         ("app_group", ["216199618143360301"]),
            ...         ("scim_group", [("216199618143191058", "2079468"), ("216199618143191058", "2079446")]),
            ...     ],
            ... )
        """
        http_method = "post".upper()
        policy_id = self.get_policy("inspection").id
        api_url = format_url(f"{self._zpa_base_endpoint_v2}/policySet/{policy_id}/rule")

        payload = {
            "name": name,
            "action": action.upper(),
            "zpnInspectionProfileId": zpn_inspection_profile_id,
            "conditions": self._create_conditions_v2(kwargs.pop("conditions", [])),
        }

        for key, value in kwargs.items():
            payload[snake_to_camel(key)] = value

        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, payload, params)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return response.get_body()

    def update_app_protection_rule_v2(self, rule_id: str, **kwargs) -> dict:
        """
        Add a new Privileged Remote Access Credential Policy rule.

        See the
        `ZPA Privileged Policies API reference <https://help.zscaler.com/zpa/configuring-privileged-policies-using-api>`_
        for further detail on optional keyword parameter structures.

        Args:
            name (str):
                The name of the new rule.
            credential_id (str):
                The ID of the privileged credential for the rule.
            **kwargs:
                Optional keyword args.

        Keyword Args:
            action (str):
                The action for the rule. Accepted value is: ``inject_credentials``
            description (str):
                Additional information about the credential rule.
            enabled (bool):
                Whether or not the credential rule is enabled.
            rule_order (str):
                The rule evaluation order number of the rule.
            conditions (list):
                A list of conditional rule tuples. Tuples must follow the convention: `Object Type`, `LHS value`, `RHS value`.
                If you are adding multiple values for the same object type then you will need a new entry for each value.

                * `conditions`: This is for providing the set of conditions for the policy
                    * `object_type`: This is for specifying the policy criteria.
                        The following values are supported: "app", "app_group", "saml", "scim", "scim_group"
                        * `saml`: The unique Identity Provider ID and SAML attribute ID
                        * `scim`: The unique Identity Provider ID and SCIM attribute ID
                        * `scim_group`: The unique Identity Provider ID and SCIM_GROUP ID

                .. code-block:: python

                    zpa.policiesv2.add_privileged_credential_rule(
                        name='new_pra_credential_rule',
                        description='new_pra_credential_rule',
                        credential_id='credential_id',
                        conditions=[
                            ("scim_group", [("idp_id", "scim_group_id"), ("idp_id", "scim_group_id")])
                            ("console", ["console_id"]),
                        ],
                    )
        """
        http_method = "put".upper()
        policy_id = self.get_policy("inspection").id
        api_url = format_url(f"{self._zpa_base_endpoint_v2}/policySet/{policy_id}/rule/{rule_id}")

        current_rule = self.get_rule("inspection", rule_id)
        payload = convert_keys(current_rule)

        if "conditions" in payload and "conditions" not in kwargs:
            del payload["conditions"]

        for key, value in kwargs.items():
            if key == "conditions":
                payload["conditions"] = self._create_conditions_v2(value)
            else:
                payload[snake_to_camel(key)] = value

        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, payload, params)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return response.get_body()

    def add_privileged_credential_rule_v2(self, name: str, credential_id: str, **kwargs) -> dict:
        """
        Add a new Privileged Remote Access Credential Policy rule.
        """
        http_method = "post".upper()
        policy_id = self.get_policy("credential").id
        api_url = format_url(f"{self._zpa_base_endpoint_v2}/policySet/{policy_id}/rule")

        payload = {
            "name": name,
            "action": "INJECT_CREDENTIALS",
            "credential": {"id": credential_id},
            "conditions": self._create_conditions_v2(kwargs.pop("conditions", [])),
        }

        for key, value in kwargs.items():
            payload[snake_to_camel(key)] = value

        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, payload, params)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return response.get_body()

    def update_privileged_credential_rule_v2(self, rule_id: str, **kwargs) -> dict:
        """
        Update an existing privileged credential policy rule.

        Args:
            rule_id (str):
                The unique identifier for the rule to be updated.
            **kwargs: Optional keyword args.

        Keyword Args:
            action (str):
                The action for the rule. Accepted value is: ``inject_credentials``
            description (str):
                Additional information about the credential rule.
            enabled (bool):
                Whether or not the credential rule is enabled.
            rule_order (str):
                The rule evaluation order number of the rule.
            credential_id (str):
                The ID of the privileged credential for the rule.
            conditions (list):
                A list of conditional rule tuples. Tuples must follow the convention: `Object Type`, `LHS value`,
                `RHS value`. If you are adding multiple values for the same object type then you will need
                a new entry for each value.

                Examples:

                .. code-block:: python

                    [('saml', 'id', '926196382959075416'),
                    ('scim', 'id', '926196382959075417'),
                    ('scim_group', 'id', '926196382959075332),
                    'credential_id', '926196382959075332, 'zpn_client_type_zapp'),

        Examples:
            Updates the name only for an Credential Policy rule:

            >>> zpa.policiesv2.update_privileged_credential_rule(
            ...   rule_id='888888',
            ...   name='credential_rule_new_name')
        """
        http_method = "put".upper()
        policy_id = self.get_policy("credential").id
        api_url = format_url(f"{self._zpa_base_endpoint_v2}/policySet/{policy_id}/rule/{rule_id}")

        current_rule = self.get_rule("credential", rule_id)
        payload = convert_keys(current_rule)

        if "conditions" in payload and "conditions" not in kwargs:
            del payload["conditions"]

        for key, value in kwargs.items():
            if key == "conditions":
                payload["conditions"] = self._create_conditions_v2(value)
            elif key == "credential_id":
                payload["credential"] = {"id": value}
            else:
                payload[snake_to_camel(key)] = value

        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        payload["action"] = "INJECT_CREDENTIALS"
        payload = {k: v for k, v in payload.items() if k != "conditions" or v}

        request, error = self._request_executor.create_request(http_method, api_url, payload, params)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return response.get_body()

    def delete_rule(self, policy_type: str, rule_id: str, **kwargs) -> int:
        """
        Deletes the specified policy rule.

        Args:
            policy_type (str):
                The type of policy the rule belongs to. Accepted values are:

                 |  ``access`` - returns the Access Policy
                 |  ``capabilities`` - returns the Capabilities Policy
                 |  ``client_forwarding`` - returns the Client Forwarding Policy
                 |  ``clientless`` - returns the Clientlesss Session Protection Policy
                 |  ``credential`` - returns the Credential Policy
                 |  ``inspection`` - returns the Inspection Policy
                 |  ``isolation`` - returns the Isolation Policy
                 |  ``redirection`` - returns the Redirection Policy
                 |  ``siem`` - returns the SIEM Policy
                 |  ``timeout`` - returns the Timeout Policy

            rule_id (str):
                The unique identifier for the policy rule.

        Examples:
            >>> zpa.policies.delete_rule(policy_type='access',
            ...    rule_id='88888')
        """
        http_method = "delete".upper()
        policy_id = self.get_policy(policy_type).id
        api_url = format_url(f"{self._zpa_base_endpoint_v2}/policySet/{policy_id}/rule/{rule_id}")

        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, {}, params)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return response.get_status_code()

    def reorder_rule(self, policy_type: str, rule_id: str, rule_order: str, **kwargs) -> tuple:
        """
        Change the order of an existing policy rule.
        Args:
            policy_type (str): The policy type. Accepted values are:

                |  ``access``
                |  ``timeout``
                |  ``client_forwarding``
                |  ``isolation``
                |  ``inspection``
                |  ``redirection``
                |  ``credential``
                |  ``capabilities``
                |  ``siem``
            rule_id (str): The unique ID of the rule that will be reordered.
            rule_order (str): The new order for the rule.
            **kwargs: Optional keyword arguments.
                microtenant_id (str): The ID of the microtenant, if applicable.
        Returns:
            tuple: (Updated rule, response, error)

        Examples:
            Updates the order for an existing access policy rule:

            >>> zpa.policies.reorder_rule(
            ...     policy_type='access',
            ...     rule_id='88888',
            ...     rule_order='2'
            ... )

            Updates the order for an existing timeout policy rule with a specific microtenant:

            >>> zpa.policies.reorder_rule(
            ...     policy_type='timeout',
            ...     rule_id='77777',
            ...     rule_order='1',
            ...     microtenant_id='1234567890'
            ... )
        """
        http_method = "put".upper()
        policy_id = self.get_policy(policy_type).id
        api_url = format_url(f"""
            {self._zpa_base_endpoint_v1}
            /policySet/{policy_id}/rule/{rule_id}/reorder/{rule_order}
        """)

        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor\
            .create_request(http_method, api_url, {}, params)
        if error:
            return (None, None, error)

        response, error = self._request_executor\
            .execute(request)
        if error:
            return (None, response, error)

        updated_rule, error = self.get_rule(policy_type, rule_id)
        return (updated_rule, response, error)

    def bulk_reorder_rules(self, policy_type: str, rules_orders: list[str], **kwargs) -> tuple:
        """
        Bulk change the order of policy rules.

        Args:
            policy_type (str): The policy type. Accepted values are:

                |  ``access``
                |  ``timeout``
                |  ``client_forwarding``
                |  ``isolation``
                |  ``inspection``
                |  ``redirection``
                |  ``credential``
                |  ``capabilities``
                |  ``siem``
            rules_orders (list[str]): A list of rule IDs in the desired order.
            **kwargs: Optional keyword arguments.

        Returns:
            tuple: (Response, error)

        Examples:
            Reordering access policy rules:

            >>> zpa.policies.bulk_reorder_rules(
            ...     policy_type='access',
            ...     rules_orders=[
            ...         '216199618143374210',
            ...         '216199618143374209',
            ...         '216199618143374208',
            ...         '216199618143374207',
            ...         '216199618143374206',
            ...         '216199618143374205',
            ...         '216199618143374204',
            ...         '216199618143374203',
            ...         '216199618143374202',
            ...         '216199618143374201',
            ...     ]
            ... )

            Reordering timeout policy rules for a specific microtenant:

            >>> zpa.policies.bulk_reorder_rules(
            ...     policy_type='timeout',
            ...     rules_orders=[
            ...         '216199618143374220',
            ...         '216199618143374219',
            ...         '216199618143374218',
            ...         '216199618143374217',
            ...         '216199618143374216',
            ...     ],
            ...     microtenant_id='1234567890'
            ... )
        """
        http_method = "put".upper()

        # Get the first policy from the list returned by get_policy
        policy_data, _, err = self.get_policy(policy_type)
        if err or not policy_data:
            return (None, None, f"Error retrieving policy for {policy_type}: {err}")

        policy_set_id = policy_data.get("id")
        if not policy_set_id:
            return (None, None, f"No policy ID found for policy_type: {policy_type}")

        # Construct the API URL using the retrieved policy_set_id
        api_url = format_url(f"""
            {self._zpa_base_endpoint_v1}
            /policySet/{policy_set_id}/reorder
        """)

        # Extract microtenant_id if present in kwargs
        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        # Call create_request without the need for custom headers
        request, error = self._request_executor\
            .create_request(http_method, api_url, body=rules_orders, params=params)
        if error:
            return (None, None, error)

        # Execute the request
        response, error = self._request_executor\
            .execute(request)
        if error:
            return (None, response, error)
        return (None, response, None)