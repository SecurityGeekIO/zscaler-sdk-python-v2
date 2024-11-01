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
from zscaler.request_executor import RequestExecutor
from zscaler.zpa.models.provisioning_keys import ProvisioningKey
from zscaler.utils import format_url


def simplify_key_type(key_type):
    """
    Simplifies the key type for the user. Accepted values are 'connector' and 'service_edge'.

    Args:
        key_type (str): The key type provided by the user.

    Returns:
        str: The simplified key type.
    """
    if key_type == "connector":
        return "CONNECTOR_GRP"
    elif key_type == "service_edge":
        return "SERVICE_EDGE_GRP"
    else:
        raise ValueError("Unexpected key type.")


class ProvisioningKeyAPI(APIClient):
    """
    A client object for the Provisioning Keys resource.
    """

    def __init__(self, request_executor, config):
        super().__init__()
        self._request_executor: RequestExecutor = request_executor
        customer_id = config["client"].get("customerId")
        self._zpa_base_endpoint = f"/zpa/mgmtconfig/v1/admin/customers/{customer_id}"

    def list_provisioning_keys(self, key_type: str, query_params=None) -> tuple:
        """
        Returns a list of all configured provisioning keys that match the specified ``key_type``.

        Args:
            key_type (str): The type of provisioning key. Accepted values are:
                ``connector`` and ``service_edge``.
            query_params (dict, optional): Map of query parameters for the request.
                [query_params.pagesize] {int}: Page size for pagination.
                [query_params.search] {str}: Search string for filtering results.
                [query_params.microtenant_id] {str}: ID of the microtenant, if applicable.
                [query_params.max_items] {int}: Maximum number of items to fetch before stopping.
                [query_params.max_pages] {int}: Maximum number of pages to request before stopping.

        Returns:
            tuple: A tuple containing (list of ProvisioningKey instances, Response, error)

        Examples:
            List all App Connector Groups provisioning keys:

            >>> for key in zpa.provisioning.list_provisioning_keys(key_type="connector"):
            ...    print(key)

            List all Service Edge Groups provisioning keys:

            >>> for key in zpa.provisioning.list_provisioning_keys(key_type="service_edge"):
            ...    print(key)
        """
        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._zpa_base_endpoint}
            /associationType/{simplify_key_type(key_type)}/provisioningKey
        """
        )

        query_params = query_params or {}
        microtenant_id = query_params.get("microtenant_id", None)
        if microtenant_id:
            query_params["microtenantId"] = microtenant_id

        # Prepare request
        request, error = self._request_executor.create_request(http_method, api_url, params=query_params)
        if error:
            return (None, None, error)

        # Execute the request
        response, error = self._request_executor.execute(request)
        if error:
            return (None, response, error)

        try:
            result = []
            for item in response.get_all_pages_results():
                result.append(ProvisioningKey(self.form_response_body(item)))
        except Exception as error:
            return (None, response, error)
        return (result, response, None)

    def get_provisioning_key(self, key_id: str, key_type: str, query_params=None) -> tuple:
        """
        Returns information on the specified provisioning key.

        Args:
            key_id (str): The unique id of the provisioning key.
            key_type (str): The type of provisioning key, accepted values are:

                ``connector`` and ``service_edge``.
            **kwargs: Optional keyword arguments.

        Keyword Args:
            microtenant_id (str): The unique identifier for the microtenant.

        Returns:
            :obj:`Box`: The requested provisioning key resource record.

        Examples:
            Get the specified App Connector key.

            >>> provisioning_key = zpa.provisioning.get_provisioning_key("999999",
            ...    key_type="connector")

            Get the specified Service Edge key.

            >>> provisioning_key = zpa.provisioning.get_provisioning_key("888888",
            ...    key_type="service_edge")

            Get the specified App Connector key for a microtenant.

            >>> provisioning_key = zpa.provisioning.get_provisioning_key("999999",
            ...    key_type="connector", microtenant_id="12345")

        """
        http_method = "get".upper()
        api_url = format_url(
            f"""{
            self._zpa_base_endpoint}
            /associationType/{simplify_key_type(key_type)}/provisioningKey/{key_id}
        """
        )

        query_params = query_params or {}
        microtenant_id = query_params.get("microtenant_id", None)
        if microtenant_id:
            query_params["microtenantId"] = microtenant_id

        request, error = self._request_executor.create_request(http_method, api_url, params=query_params)
        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request, ProvisioningKey)
        if error:
            return (None, response, error)

        try:
            result = ProvisioningKey(self.form_response_body(response.get_body()))
        except Exception as error:
            return (None, response, error)
        return (result, response, None)

    def add_provisioning_key(self, provisioning, **kwargs) -> tuple:
        """
        Adds a new provisioning key to ZPA.

        Args:
            key_type (str): The type of provisioning key, accepted values are:

                ``connector`` and ``service_edge``.
            name (str): The name of the provisioning key.
            max_usage (int): The maximum amount of times this key can be used.
            enrollment_cert_id (str):
                The unique id of the enrollment certificate that will be used for this provisioning key.
            component_id (str):
                The unique id of the component that this provisioning key will be linked to. For App Connectors, this
                will be the App Connector Group Id. For Service Edges, this will be the Service Edge Group Id.
            **kwargs: Optional keyword args.

        Returns:
            :obj:`Box`: The newly created Provisioning Key resource record.
        """
        # Extract key_type from the provisioning dictionary
        key_type = provisioning.pop("key_type", None)
        if key_type is None:
            raise ValueError("key_type must be provided.")

        http_method = "post".upper()
        api_url = format_url(
            f"""
            {self._zpa_base_endpoint}
            /associationType/{simplify_key_type(key_type)}/provisioningKey
        """
        )

        # Ensure provisioning is a dictionary
        if isinstance(provisioning, dict):
            body = provisioning
        else:
            body = provisioning.as_dict()

        # Extract microtenant_id from the body
        microtenant_id = body.get("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        # Extract and set attributes from the body
        name = body.pop("name", None)
        max_usage = body.pop("max_usage", None)
        enrollment_cert_id = body.get("enrollment_cert_id")
        component_id = body.get("component_id")

        # Add extracted values to the body
        body.update(
            {"name": name, "maxUsage": max_usage, "enrollmentCertId": enrollment_cert_id, "zcomponentId": component_id}
        )

        # Add any additional attributes from kwargs
        body.update(kwargs)

        # Create the request
        request, error = self._request_executor.create_request(http_method, api_url, body=body, params=params)
        if error:
            return (None, None, error)

        # Execute the request
        response, error = self._request_executor.execute(request, ProvisioningKey)
        if error:
            return (None, response, error)

        try:
            result = ProvisioningKey(self.form_response_body(response.get_body()))
        except Exception as error:
            return (None, response, error)
        return (result, response, None)

    def update_provisioning_key(self, key_id: str, provisioning, **kwargs) -> tuple:
        """
        Updates the specified provisioning key.

        Args:
            key_id (str): The unique id of the Provisioning Key being updated.
            key_type (str): The type of provisioning key, accepted values are:

                ``connector`` and ``service_edge``.
            **kwargs: Optional keyword args.

        Returns:
            :obj:`Box`: The updated Provisioning Key resource record.
        """
        # Extract key_type from the provisioning dictionary
        key_type = provisioning.pop("key_type", None)
        if key_type is None:
            raise ValueError("key_type must be provided.")

        http_method = "put".upper()
        api_url = format_url(
            f"""
            {self._zpa_base_endpoint}
            /associationType/{simplify_key_type(key_type)}/provisioningKey/{key_id}
        """
        )

        # Ensure provisioning is in dictionary format
        if isinstance(provisioning, dict):
            body = provisioning
        else:
            body = provisioning.as_dict()

        # Extract microtenant_id from the body
        microtenant_id = body.get("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        # Extract and set attributes from the body
        name = body.pop("name", None)
        max_usage = body.pop("max_usage", None)
        enrollment_cert_id = body.get("enrollment_cert_id")
        component_id = body.get("component_id")

        # Add extracted values to the body
        body.update(
            {"name": name, "maxUsage": max_usage, "enrollmentCertId": enrollment_cert_id, "zcomponentId": component_id}
        )

        # Add any additional attributes from kwargs
        body.update(kwargs)

        # Create the request
        request, error = self._request_executor.create_request(http_method, api_url, body=body, params=params)
        if error:
            return (None, None, error)

        # Execute the request
        response, error = self._request_executor.execute(request, ProvisioningKey)
        if error:
            return (None, response, error)

        # Handle case where no content is returned (204 No Content)
        if response is None:
            # Return a meaningful result to indicate success
            return (ProvisioningKey({"id": key_id}), None, None)

        try:
            result = ProvisioningKey(self.form_response_body(response.get_body()))
        except Exception as error:
            return (None, response, error)
        return (result, response, None)

    def delete_provisioning_key(self, key_id: str, key_type: str, microtenant_id: str = None) -> tuple:
        """
        Deletes the specified provisioning key from ZPA.

        Args:
            key_id (str): The unique id of the provisioning key that will be deleted.
            key_type (str): The type of provisioning key, accepted values are:

                ``connector`` and ``service_edge``.
            **kwargs: Optional keyword args.

        Keyword Args:
            microtenant_id (str): The microtenant ID to be used for this request.

        Returns:
            :obj:`int`: The status code for the operation.

        Examples:
            Delete an App Connector provisioning key:

            >>> zpa.provisioning.delete_provisioning_key(key_id="999999",
            ...    key_type="connector")

            Delete a Service Edge provisioning key:

            >>> zpa.provisioning.delete_provisioning_key(key_id="888888",
            ...    key_type="service_edge")

        """
        http_method = "delete".upper()
        api_url = format_url(
            f"""
            {self._zpa_base_endpoint}
            /associationType/{simplify_key_type(key_type)}/provisioningKey/{key_id}
        """
        )

        # Handle microtenant_id in URL params if provided
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        # Create the request
        request, error = self._request_executor.create_request(http_method, api_url, params=params)
        if error:
            return (None, None, error)

        # Execute the request
        response, error = self._request_executor.execute(request)
        if error:
            return (None, response, error)

        return (None, response, None)
