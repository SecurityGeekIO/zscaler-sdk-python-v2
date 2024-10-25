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
from zscaler.zpa.models.inspection import InspectionProfile
from zscaler.zpa.models.inspection import AppProtectionCustomControl
from zscaler.zpa.models.inspection import PredefinedInspectionControl
from zscaler.utils import format_url, convert_keys, snake_to_camel
from requests.utils import quote
from urllib.parse import urlencode


class InspectionControllerAPI(APIClient):
    """
    A client object for the ZPA Inspection Profiles resource.
    """

    def __init__(self, request_executor, config):
        super().__init__()
        self._request_executor = request_executor
        customer_id = config["client"].get("customerId")
        self._base_endpoint = f"/zpa/mgmtconfig/v1/admin/customers/{customer_id}"

    def list_profiles(self, query_params=None, keep_empty_params=False) -> tuple:
        """
        Enumerates App Protection Profile in your organization with pagination.
        A subset of App Protection Profile can be returned that match a supported
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
            tuple: A tuple containing (list of InspectionProfile instances, Response, error)
        """
        http_method = "get".upper()
        api_url = format_url(f"{self._base_endpoint}/inspectionProfile")

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
        response, error = self._request_executor.execute(request, InspectionProfile)

        if error:
            return (None, response, error)

        # Parse the response into IDP instances
        try:
            result = []
            for item in response.get_body():
                result.append(InspectionProfile(self.form_response_body(item)))
        except Exception as error:
            return (None, response, error)

        return (result, response, None)

    def get_profile(self, profile_id: str, **kwargs) -> InspectionProfile:
        """
        Gets information on the specified inspection profile.

        Args:
            profile_id (str): The unique identifier for the inspection profile.

        Returns:
            InspectionProfile: The corresponding inspection profile object.
        """
        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._base_endpoint}
            /inspectionProfile/{profile_id}
            """
        )

        request, error = self._request_executor.create_request(http_method, api_url, {}, kwargs)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return InspectionProfile(response.get_body())

    def add_profile(self, name: str, paranoia_level: int, predef_controls_version: str, **kwargs) -> InspectionProfile:
        """
        Adds a new inspection profile.

        Args:
            name (str): The name of the inspection profile.
            paranoia_level (int): The paranoia level of the profile.
            predef_controls_version (str): The version of predefined controls.

        Returns:
            InspectionProfile: The created inspection profile object.
        """
        http_method = "post".upper()
        api_url = format_url(f"{self._base_endpoint}/inspectionProfile")

        # Preprocessors group logic
        preprocessors_group = self.get_predef_control_group_by_name("Preprocessors")
        preprocessors_controls = [
            {"id": control["id"], "action": control["default_action"]}
            for control in preprocessors_group["predefined_inspection_controls"]
        ]

        payload = {
            "name": name,
            "paranoiaLevel": paranoia_level,
            "predefinedControlsVersion": predef_controls_version,
            "predefinedControls": preprocessors_controls,
        }

        # Add predefined controls if provided
        if kwargs.get("predef_controls"):
            predef_controls = kwargs.pop("predef_controls")
            payload["predefinedControls"].extend([{"id": control[0], "action": control[1]} for control in predef_controls])

        # Add custom controls if provided
        if kwargs.get("custom_controls"):
            custom_controls = kwargs.pop("custom_controls")
            payload["customControls"] = [{"id": control[0], "action": control[1]} for control in custom_controls]

        # Add additional parameters
        payload.update(kwargs)

        # Send the POST request
        request, error = self._request_executor.create_request(http_method, api_url, payload)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return InspectionProfile(response.get_body())

    def update_profile(self, profile_id: str, **kwargs) -> InspectionProfile:
        """
        Updates the specified inspection profile.

        Args:
            profile_id (str): The unique ID of the profile to be updated.

        Returns:
            InspectionProfile: The updated inspection profile object.
        """
        http_method = "put".upper()
        api_url = format_url(f"{self._base_endpoint}/inspectionProfile/{profile_id}")

        # Fetch the existing profile and update with new kwargs
        profile_data = self.get_profile(profile_id).request_format()

        # Ensure the preprocessors control group is included
        preprocessors_group = self.get_predef_control_group_by_name("Preprocessors")
        preprocessors_controls = [
            {"id": control["id"], "action": control["default_action"]}
            for control in preprocessors_group["predefined_inspection_controls"]
        ]

        if not any(control["id"] in profile_data["predefinedControls"] for control in preprocessors_controls):
            profile_data["predefinedControls"].extend(preprocessors_controls)

        # Add predefined controls if provided
        if kwargs.get("predef_controls"):
            predef_controls = kwargs.pop("predef_controls")
            profile_data["predefinedControls"].extend(
                [{"id": control[0], "action": control[1]} for control in predef_controls]
            )

        # Add custom controls if provided
        if kwargs.get("custom_controls"):
            custom_controls = kwargs.pop("custom_controls")
            profile_data["customControls"] = [{"id": control[0], "action": control[1]} for control in custom_controls]

        # Update with other provided parameters
        profile_data.update(kwargs)

        # Send the PUT request
        request, error = self._request_executor.create_request(http_method, api_url, profile_data)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return InspectionProfile(response.get_body())

    def delete_profile(self, profile_id: str) -> int:
        """
        Deletes the specified inspection profile.

        Args:
            profile_id (str): The unique identifier for the inspection profile to be deleted.

        Returns:
            int: Status code of the delete operation.
        """
        http_method = "delete".upper()
        api_url = format_url(f"{self._base_endpoint}/inspectionProfile/{profile_id}")

        request, error = self._request_executor.create_request(http_method, api_url)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return response.status_code

    def profile_control_attach(self, profile_id: str, action: str, **kwargs) -> InspectionProfile:
        """
        Attaches or detaches all predefined ZPA Inspection Controls to a ZPA Inspection Profile.

        Args:
            profile_id (str): The unique ID for the ZPA Inspection Profile that will be modified.
            action (str): The association action that will be taken, accepted values are:
                * ``attach``: Attaches all predefined controls to the Inspection Profile with the specified version.
                * ``detach``: Detaches all predefined controls from the Inspection Profile.
            **kwargs: Additional keyword arguments.

        Keyword Args:
            profile_version (str): The version of the Predefined Controls to attach. Only required when using the
                attach action. Defaults to ``OWASP_CRS/3.3.0``.

        Returns:
            InspectionProfile: The updated ZPA Inspection Profile resource record.
        """
        http_method = "put".upper()
        if action == "attach":
            api_url = format_url(f"{self._base_endpoint}/inspectionProfile/{profile_id}/associateAllPredefinedControls")
            payload = {"version": kwargs.pop("profile_version", "OWASP_CRS/3.3.0")}
        elif action == "detach":
            api_url = format_url(f"{self._base_endpoint}/inspectionProfile/{profile_id}/deAssociateAllPredefinedControls")
            payload = {}
        else:
            raise ValueError("Unknown action provided. Valid actions are 'attach' or 'detach'.")

        request, error = self._request_executor.create_request(http_method, api_url, payload)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error or response.status_code != 204:
            return response.status_code

        return self.get_profile(profile_id)

    def update_profile_and_controls(self, profile_id: str, inspection_profile: dict, **kwargs) -> InspectionProfile:
        """
        Updates the inspection profile and controls for the specified ID.

        Args:
            profile_id (str): The unique ID of the inspection profile.
            inspection_profile (dict): The new inspection profile object.
            **kwargs: Additional keyword arguments.

        Returns:
            InspectionProfile: The updated ZPA Inspection Profile resource record.
        """
        http_method = "put".upper()
        api_url = format_url(f"{self._base_endpoint}/inspectionProfile/{profile_id}/patch")

        payload = {
            "inspection_profile_id": profile_id,
            "inspection_profile": inspection_profile,
        }

        # Convert payload keys to match API format
        payload = convert_keys(payload)

        request, error = self._request_executor.create_request(http_method, api_url, payload)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error or response.status_code != 204:
            return None

        return self.get_profile(profile_id)

    def list_custom_controls(self, query_params=None, keep_empty_params=False) -> tuple:
        """
        Enumerates App Protection Custom Control in your organization with pagination.
        A subset of App Protection Custom Control can be returned that match a supported
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
            tuple: A tuple containing (list of AppProtectionCustomControl instances, Response, error)
        """
        http_method = "get".upper()
        api_url = format_url(f"{self._base_endpoint}/inspectionControls/custom")

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
        response, error = self._request_executor.execute(request, AppProtectionCustomControl)

        if error:
            return (None, response, error)

        # Parse the response into IDP instances
        try:
            result = []
            for item in response.get_body():
                result.append(AppProtectionCustomControl(self.form_response_body(item)))
        except Exception as error:
            return (None, response, error)

        return (result, response, None)

    def get_predef_control(self, control_id: str) -> AppProtectionCustomControl:
        """
        Returns the specified predefined ZPA Inspection Control.

        Args:
            control_id (str): The unique ID of the predefined control.

        Returns:
            AppProtectionCustomControl: The corresponding predefined control object.
        """
        http_method = "get".upper()
        api_url = format_url(f"{self._base_endpoint}/inspectionControls/predefined/{control_id}")

        request, error = self._request_executor.create_request(http_method, api_url, {})
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return AppProtectionCustomControl(response.get_body())

    def get_custom_control(self, control_id: str) -> AppProtectionCustomControl:
        """
        Returns the specified custom ZPA Inspection Control.

        Args:
            control_id (str): The unique ID of the custom control.

        Returns:
            AppProtectionCustomControl: The corresponding custom control object.
        """
        http_method = "get".upper()
        api_url = format_url(f"{self._base_endpoint}/inspectionControls/custom/{control_id}")

        request, error = self._request_executor.create_request(http_method, api_url, {})
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return AppProtectionCustomControl(response.get_body())

    def add_custom_control(
        self,
        name: str,
        default_action: str,
        severity: str,
        type: str,
        rules: list,
        **kwargs,
    ) -> AppProtectionCustomControl:
        """
        Adds a new ZPA Inspection Custom Control.

        Args:
            name (str): The name of the custom control.
            default_action (str): The default action for this control.
            severity (str): The severity level for the control.
            type (str): The type of HTTP message this control applies to.
            rules (list): A list of Inspection Control rule objects.

        Returns:
            AppProtectionCustomControl: The newly created custom control object.
        """
        http_method = "post".upper()
        api_url = format_url(f"{self._base_endpoint}/inspectionControls/custom")

        payload = {
            "name": name,
            "defaultAction": default_action,
            "severity": severity,
            "type": type,
            "rules": [self._create_rule(rule) for rule in rules],
        }

        # Add optional parameters to payload
        if "default_action_value" in kwargs:
            payload["defaultActionValue"] = kwargs.pop("default_action_value")

        for key, value in kwargs.items():
            payload[snake_to_camel(key)] = value

        request, error = self._request_executor.create_request(http_method, api_url, payload)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return AppProtectionCustomControl(response.get_body())

    def update_custom_control(self, control_id: str, **kwargs) -> AppProtectionCustomControl:
        """
        Updates the specified custom ZPA Inspection Control.

        Args:
            control_id (str): The unique ID of the custom control.

        Returns:
            AppProtectionCustomControl: The updated custom control object.
        """
        http_method = "put".upper()
        api_url = format_url(f"{self._base_endpoint}/inspectionControls/custom/{control_id}")

        # Get existing control and update it with new values
        payload = self.get_custom_control(control_id).request_format()

        if "rules" in kwargs:
            payload["rules"] = [self._create_rule(rule) for rule in kwargs.pop("rules")]

        for key, value in kwargs.items():
            payload[snake_to_camel(key)] = value

        request, error = self._request_executor.create_request(http_method, api_url, payload)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return AppProtectionCustomControl(response.get_body())

    def delete_custom_control(self, control_id: str) -> int:
        """
        Deletes the specified custom ZPA Inspection Control.

        Args:
            control_id (str): The unique ID for the custom control.

        Returns:
            int: The status code for the operation.
        """
        http_method = "delete".upper()
        api_url = format_url(f"{self._base_endpoint}/inspectionControls/custom/{control_id}")

        request, error = self._request_executor.create_request(http_method, api_url, {})
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return response.status_code

    def list_predef_controls(self, version: str = "OWASP_CRS/3.3.0", query_params=None, keep_empty_params=False) -> tuple:
        """
        Returns a list of predefined ZPA Inspection Controls.

        Args:
            version (str): The version of the predefined controls to return. Default is "OWASP_CRS/3.3.0".
            query_params {dict}: Map of additional query parameters for the request.
                [query_params.search] {str}: Search string for filtering results by features or fields.
                [query_params.search_field] {str}: Field to search by. Default is "name".
            keep_empty_params (bool): Whether to include empty parameters in the query string.

        Returns:
            tuple: A tuple containing (list of PredefinedInspectionControl objects, Response, error).

        Examples:
            >>> for control in zpa.inspection.list_predef_controls():
            ...     print(control)

            >>> for control in zpa.inspection.list_predef_controls(search="Failed to parse request body"):
            ...     print(control)
        """
        # Initialize URL and HTTP method
        http_method = "get".upper()
        encoded_version = quote(version, safe="")

        api_url = format_url(f"{self._base_endpoint}/inspectionControls/predefined?version={encoded_version}")

        # Handle query parameters
        query_params = query_params or {}
        search = query_params.pop("search", None)
        search_field = query_params.pop("search_field", "name")

        if search:
            encoded_search = quote(f"{search_field}+EQ+{search}", safe="")
            api_url += f"&search={encoded_search}"

        # Append any additional query parameters, if provided
        if query_params:
            additional_params = "&".join(f"{key}={quote(str(value))}" for key, value in query_params.items())
            api_url += f"&{additional_params}"

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
        response, error = self._request_executor.execute(request, PredefinedInspectionControl)

        if error:
            return (None, response, error)

        # Parse the response into PredefinedInspectionControl instances
        try:
            result = []
            for item in response.get_body():
                result.append(PredefinedInspectionControl(self.form_response_body(item)))
        except Exception as error:
            return (None, response, error)

        return (result, response, None)

    def get_predef_control_by_name(self, name: str, version: str = "OWASP_CRS/3.3.0") -> PredefinedInspectionControl:
        """
        Returns the specified predefined ZPA Inspection Control by its name.

        Args:
            name (str): The name of the predefined ZPA Inspection Control to be returned.
            version (str): The version of the predefined control to return. Default is "OWASP_CRS/3.3.0".

        Returns:
            PredefinedInspectionControl: The corresponding predefined ZPA Inspection Control object.

        Examples:
            >>> print(inspection.get_predef_control_by_name("Failed to parse request body"))
        """
        control_groups = self.list_predef_controls(search=name, version=version)
        for control_group in control_groups:
            for control in control_group.predefined_inspection_controls:
                if control.name == name:
                    return control

        raise ValueError(f"No predefined control named '{name}' found.")

    def get_predef_control_group_by_name(
        self, group_name: str, version: str = "OWASP_CRS/3.3.0"
    ) -> PredefinedInspectionControl:
        """
        Returns the specified predefined ZPA Inspection Control Group by its name.

        Args:
            group_name (str): The name of the predefined ZPA Inspection Control Group to be returned.
            version (str): The version of the predefined control to return. Default is "OWASP_CRS/3.3.0".

        Returns:
            PredefinedInspectionControl: The corresponding predefined ZPA Inspection Control Group object.

        Examples:
            >>> print(zpa.inspection.get_predef_control_group_by_name("Protocol Issues"))
        """
        control_groups = self.list_predef_controls(search=group_name, search_field="controlGroup", version=version)
        for control_group in control_groups:
            if control_group.control_group == group_name:
                return control_group

            for control in control_group.predefined_inspection_controls:
                if control.control_group == group_name:
                    return control_group

        raise ValueError(f"No predefined control group named '{group_name}' found.")

    def list_control_action_types(self) -> tuple:
        """
        Returns a list of ZPA Inspection Control Action Types.

        Returns:
            tuple: A tuple containing (list of action types, Response, error).

        Examples:
            >>> for action_type in zpa.inspection.list_control_action_types():
            ...     print(action_type)

        """
        # Initialize URL and HTTP method
        http_method = "get".upper()
        api_url = format_url(f"{self._base_endpoint}/inspectionControls/actionTypes")

        # Prepare request body and headers
        body = {}
        headers = {}
        form = {}

        # Create the request
        request, error = self._request_executor.create_request(http_method, api_url, body, headers, form)

        if error:
            return (None, None, error)

        # Execute the request
        response, error = self._request_executor.execute(request, str)  # Expecting a list of strings

        if error:
            return (None, response, error)

        # Parse the response
        try:
            result = response.get_body()  # In this case, response is a list of strings like ["PASS", "BLOCK", "REDIRECT"]
        except Exception as error:
            return (None, response, error)

        return (result, response, None)

    def list_control_severity_types(self) -> tuple:
        """
        Returns a list of Inspection Control Severity Types.

        Returns:
            tuple: A dictionary containing all valid Inspection Control Severity Types.

        Examples:
            >>> for severity in zpa.inspection.list_control_severity_types():
            ...     print(severity)

        """
        http_method = "get".upper()
        api_url = format_url(f"{self._base_endpoint}/inspectionControls/severityTypes")

        body = {}
        headers = {}
        form = {}

        # Create the request
        request, error = self._request_executor.create_request(http_method, api_url, body, headers, form)

        if error:
            return (None, None, error)

        # Execute the request
        response, error = self._request_executor.execute(request, str)  # Expecting a list of strings

        if error:
            return (None, response, error)

        # Parse the response
        try:
            result = response.get_body()  # In this case, response is a list of strings like ["PASS", "BLOCK", "REDIRECT"]
        except Exception as error:
            return (None, response, error)

        return (result, response, None)

    def list_control_types(self) -> tuple:
        """
        Returns a list of ZPA Inspection Control Types.

        Returns:
            tuple: A dictionary containing ZPA Inspection Control Types.

        Examples:
            >>> for control_type in zpa.inspection.list_control_types():
            ...     print(control_type)

        """
        http_method = "get".upper()
        api_url = format_url(f"{self._base_endpoint}/inspectionControls/controlTypes")

        # Prepare request body and headers
        body = {}
        headers = {}
        form = {}

        # Create the request
        request, error = self._request_executor.create_request(http_method, api_url, body, headers, form)

        if error:
            return (None, None, error)

        # Execute the request
        response, error = self._request_executor.execute(request, str)  # Expecting a list of strings

        if error:
            return (None, response, error)

        # Parse the response
        try:
            result = response.get_body()  # In this case, response is a list of strings like ["PASS", "BLOCK", "REDIRECT"]
        except Exception as error:
            return (None, response, error)

        return (result, response, None)

    def list_custom_http_methods(self) -> tuple:
        """
        Returns a list of custom ZPA Inspection Control HTTP Methods.

        Returns:
            tuple: A dictionary containing custom ZPA Inspection Control HTTP Methods.

        Examples:
            >>> for method in zpa.inspection.list_custom_http_methods():
            ...     print(method)

        """
        http_method = "get".upper()
        api_url = format_url(f"{self._base_endpoint}/inspectionControls/custom/httpMethods")

        body = {}
        headers = {}
        form = {}

        # Create the request
        request, error = self._request_executor.create_request(http_method, api_url, body, headers, form)

        if error:
            return (None, None, error)

        # Execute the request
        response, error = self._request_executor.execute(request, str)  # Expecting a list of strings

        if error:
            return (None, response, error)

        # Parse the response
        try:
            result = response.get_body()  # In this case, response is a list of strings like ["PASS", "BLOCK", "REDIRECT"]
        except Exception as error:
            return (None, response, error)

        return (result, response, None)

    def list_predef_control_versions(self) -> tuple:
        """
        Returns a list of predefined ZPA Inspection Control versions.

        Returns:
            tuple: A dictionary containing all predefined ZPA Inspection Control versions.

        Examples:
            >>> for version in zpa.inspection.list_predef_control_versions():
            ...     print(version)

        """
        http_method = "get".upper()
        api_url = format_url(f"{self._base_endpoint}/inspectionControls/predefined/versions")

        body = {}
        headers = {}
        form = {}

        # Create the request
        request, error = self._request_executor.create_request(http_method, api_url, body, headers, form)

        if error:
            return (None, None, error)

        # Execute the request
        response, error = self._request_executor.execute(request, str)  # Expecting a list of strings

        if error:
            return (None, response, error)

        # Parse the response
        try:
            result = response.get_body()  # In this case, response is a list of strings like ["PASS", "BLOCK", "REDIRECT"]
        except Exception as error:
            return (None, response, error)

        return (result, response, None)
