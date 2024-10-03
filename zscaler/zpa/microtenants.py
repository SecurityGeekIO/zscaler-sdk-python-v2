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
from zscaler.zpa.models.microtenants import Microtenant
from zscaler.utils import format_url, snake_to_camel
from zscaler.api_response import get_paginated_data


class MicrotenantsAPI(APIClient):
    """
    A client object for the Microtenants resource.
    """

    def __init__(self):
        super().__init__()
        self._base_url = ""

    def list_microtenants(self, **kwargs) -> list:
        """
        Returns a list of all configured microtenants.

        Keyword Args:
            max_items (int): The maximum number of items to return.
            max_pages (int): The maximum number of pages to return.
            pagesize (int): Number of items per page (default is 20, maximum is 500).
            search (str): The search string used to match against features and fields.
            keep_empty_params (bool): Whether to include empty parameters in the query string.

        Returns:
            list: A list of `Microtenant` instances.

        Examples:
            >>> microtenants = zpa.microtenants.list_microtenants()
        """
        api_url = format_url(f"{self._base_url}/microtenants")

        list_data, error = get_paginated_data(request_executor=self._request_executor, path=api_url, **kwargs)

        if error:
            return None

        # Convert the raw microtenant data into Microtenant objects
        return [Microtenant(tenant) for tenant in list_data]

    def get_microtenant(self, microtenant_id: str) -> Microtenant:
        """
        Returns information on the specified microtenant.

        Args:
            microtenant_id (str): The unique identifier for the microtenant.

        Returns:
            Microtenant: The resource record for the microtenant.

        Examples:
            >>> microtenant = zpa.microtenants.get_microtenant('216199618143364393')
        """
        http_method = "get".upper()
        api_url = format_url(f"{self._base_url}/microtenants/{microtenant_id}")

        request, error = self._request_executor.create_request(http_method, api_url)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return Microtenant(response.get_body())

    def get_microtenant_summary(self) -> Microtenant:
        """
        Returns the name and ID of the configured Microtenant.

        Returns:
            Microtenant: The resource record for the microtenant.

        Examples:
            >>> summary = zpa.microtenants.get_microtenant_summary()
        """
        http_method = "get".upper()
        api_url = format_url(f"{self._base_url}/microtenants/summary")

        request, error = self._request_executor.create_request(http_method, api_url)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return Microtenant(response.get_body())

    def get_microtenant_by_name(self, name: str, **kwargs) -> Microtenant:
        """
        Returns information on the microtenant with the specified name.

        Args:
            name (str): The name of the microtenant.

        Returns:
            Microtenant: The resource record for the microtenant if found, otherwise None.

        Examples:
            >>> microtenant = zpa.microtenants.get_microtenant_by_name('example_name')
        """
        microtenants = self.list_microtenants(**kwargs)
        for microtenant in microtenants:
            if microtenant.name == name:
                return microtenant
        return None

    def add_microtenant(self, name: str, criteria_attribute: str, criteria_attribute_values: list, **kwargs) -> Microtenant:
        """
        Add a new microtenant.

        Args:
            name (str): The name of the microtenant.
            criteria_attribute (str): The criteria attribute for the microtenant.
            criteria_attribute_values (list): The values for the criteria attribute.

        Keyword Args:
            description (str): A description for the microtenant.
            enabled (bool): Whether the microtenant is enabled. Defaults to True.
            privileged_approvals_enabled (bool): Whether privileged approvals are enabled. Defaults to True.

        Returns:
            Microtenant: The resource record for the newly created microtenant.

        Examples:
            >>> microtenant = zpa.microtenants.add_microtenant(
                    name="Microtenant_A",
                    criteria_attribute="AuthDomain",
                    criteria_attribute_values=["acme.com"]
                )
        """
        http_method = "post".upper()
        api_url = format_url(f"{self._base_url}/microtenants")

        payload = {
            "name": name,
            "criteriaAttribute": criteria_attribute,
            "criteriaAttributeValues": criteria_attribute_values,
        }

        # Add optional parameters to payload
        for key, value in kwargs.items():
            payload[snake_to_camel(key)] = value

        request, error = self._request_executor.create_request(http_method, api_url, payload)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return Microtenant(response.get_body())

    def update_microtenant(self, microtenant_id: str, **kwargs) -> Microtenant:
        """
        Updates the specified microtenant.

        Args:
            microtenant_id (str): The unique identifier for the microtenant being updated.

        Keyword Args:
            name (str): The name of the microtenant.
            description (str): A description for the microtenant.
            enabled (bool): Whether the microtenant is enabled. Defaults to True.
            privileged_approvals_enabled (bool): Whether privileged approvals are enabled. Defaults to True.
            criteria_attribute (str): The criteria attribute for the microtenant.
            criteria_attribute_values (list): The values for the criteria attribute.

        Returns:
            Microtenant: The updated resource record for the microtenant.

        Examples:
            >>> updated_microtenant = zpa.microtenants.update_microtenant(
                    microtenant_id="216199618143368569",
                    name="Microtenant_A",
                    enabled=False
                )
        """
        http_method = "put".upper()
        api_url = format_url(f"{self._base_url}/microtenants/{microtenant_id}")

        # Get the current microtenant data and update it with the new kwargs
        microtenant_data = self.get_microtenant(microtenant_id).request_format()
        microtenant_data.update({snake_to_camel(k): v for k, v in kwargs.items()})

        request, error = self._request_executor.create_request(http_method, api_url, microtenant_data)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return Microtenant(response.get_body())

    def delete_microtenant(self, microtenant_id: str) -> int:
        """
        Deletes the specified microtenant.

        Args:
            microtenant_id (str): The unique identifier for the microtenant to be deleted.

        Returns:
            int: Status code of the delete operation.

        Examples:
            >>> zpa.microtenants.delete_microtenant('99999')
        """
        http_method = "delete".upper()
        api_url = format_url(f"{self._base_url}/microtenants/{microtenant_id}")

        request, error = self._request_executor.create_request(http_method, api_url)
        if error:
            return None

        response, error = self._request_executor.execute(request)
        if error:
            return None

        return response.status_code


# from box import Box, BoxList
# from requests import Response
# from zscaler.utils import snake_to_camel
# from zscaler.api_client import APIClient

# class MicrotenantsAPI(APIClient):

#     def list_microtenants(self, **kwargs) -> BoxList:
#         """
#         Returns a list of all configured microtenants.

#         Returns:
#             :obj:`BoxList`: A list of all configured microtenants.

#         Examples:
#             >>> for microtenant in zpa.microtenants.list_microtenants():
#             ...    pprint(microtenant)

#         """
#         if "pageSize" in kwargs:
#             kwargs.pop("pageSize")
#         list, _ = self.rest.get_paginated_data(path="/microtenants", **kwargs)
#         return list

#     def get_microtenant(self, microtenant_id: str) -> Box:
#         """
#         Returns information on the specified microtenant.

#         Args:
#             microtenant_id (str):
#                 The unique identifier for the microtenant.

#         Returns:
#             :obj:`Box`: The resource record for the microtenant.

#         Examples:
#             >>> pprint(zpa.microtenants.get_microtenant('216199618143364393'))

#         """
#         response = self.rest.get("/microtenants/%s" % (microtenant_id))
#         if isinstance(response, Response):
#             status_code = response.status_code
#             if status_code != 200:
#                 return None
#         return response

#     def get_microtenant_summary(self) -> Box:
#         """
#         Returns the name and ID of the configured Microtenant

#         Args:

#         Returns:
#             :obj:`Box`: The resource record for the microtenant.

#         Examples:
#             >>> pprint(zpa.microtenants.get_microtenant_summary())

#         """
#         return self.rest.get("microtenants/summary")

#     def get_microtenant_by_name(self, name: str, **kwargs) -> Box:
#         """
#         Returns information on the microtenant with the specified name.

#         Args:
#             name (str): The name of the microtenant.

#         Returns:
#             :obj:`Box` or None: The resource record for the microtenant if found, otherwise None.

#         Examples:
#             >>> microtenant = zpa.microtenants.get_microtenant_by_name('example_name')
#             >>> if microtenant:
#             ...     pprint(microtenant)
#             ... else:
#             ...     print("Microtenant not found")
#         """
#         microtenants = self.list_microtenants(**kwargs)
#         for microtenant in microtenants:
#             if microtenant.get("name") == name:
#                 return microtenant
#         return None

#     def add_microtenant(self, name: str, criteria_attribute: str, criteria_attribute_values: list, **kwargs) -> Box:
#         """
#         Add a new microtenant.

#         Args:
#             name (str): The name of the microtenant.
#             **kwargs: Optional keyword args.

#         Keyword Args:
#             description (str): A description for the microtenant.
#             enabled (bool): Whether the Microtenant is enabled or not. Defaults to True.
#             privileged_approvals_enabled (bool): Whether the Microtenant is enabled or not. Defaults to True.
#             criteria_attribute (str): The criteria attribute for the Microtenant. The supported value is AuthDomain.
#             criteria_attribute_values (list): The value for the criteria attribute.
#                 This is the valid authentication domains configured for a customer (e.g., ExampleAuthDomain.com).

#         Returns:
#             :obj:`Box`: The resource record for the newly created microtenant, including the user block.

#         Examples:
#             Create a server with the minimum required parameters:

#             >>> zpa.microtenants.add_microtenant(
#             ...   name='Microtenant_A',
#             ...   description='New Microtenant',
#             ...   enabled=True,
#             ...   privileged_approvals_enabled=True,
#             ...   criteria_attribute_values=['acme.com'],
#             ...   criteria_attribute='AuthDomain',
#             ... )

#         """
#         payload = {"name": name, "criteriaAttribute": criteria_attribute, "criteriaAttributeValues": criteria_attribute_values}

#         # Add optional parameters to payload
#         for key, value in kwargs.items():
#             payload[snake_to_camel(key)] = value
#         response = self.rest.post("microtenants", json=payload)
#         if isinstance(response, Response):
#             status_code = response.status_code
#             raise Exception(f"API call failed with status {status_code}: {response.json()}")
#         return response

#     def update_microtenant(self, microtenant_id: str, **kwargs) -> Box:
#         """
#         Updates the specified microtenant.

#         Args:
#             microtenant_id (str):
#                 The unique identifier for the microtenant being updated.
#             **kwargs:
#                 Optional keyword args.

#         Keyword Args:
#             name (str): The name of the microtenant.
#             description (str): A description for the microtenant.
#             enabled (bool): Whether the Microtenant is enabled or not. Defaults to True.
#             privileged_approvals_enabled (bool): Whether the Microtenant is enabled or not. Defaults to True.
#             criteria_attribute (str): The criteria attribute for the Microtenant. The supported value is AuthDomain.
#             criteria_attribute_values (list): The value for the criteria attribute.
#                 This is the valid authentication domains configured for a customer (e.g., ExampleAuthDomain.com).

#         Returns:
#             :obj:`Box`: The resource record for the updated microtenant.

#         Examples:
#             Update the name of a microtenant:

#             >>> zpa.servers.update_server(
#             ...   '99999',
#             ...   name='Update_Microtenant_A')

#             Disable the privileged_approvals_enabled:

#             >>> zpa.microtenants.update_microtenant(
#             ...   microtenant_id='216199618143368569',
#             ...   name='Microtenant_A',
#             ...   description='Microtenant_A',
#             ...   enabled=True,
#             ...   privileged_approvals_enabled=False,
#             ...   criteria_attribute_values=['acme.com'],
#             ...   criteria_attribute='AuthDomain',
#             ... )

#         """
#         # Set payload to value of existing record
#         payload = {snake_to_camel(k): v for k, v in self.get_microtenant(microtenant_id).items()}

#         # Add optional parameters to payload
#         for key, value in kwargs.items():
#             payload[snake_to_camel(key)] = value

#         resp = self.rest.put(f"microtenants/{microtenant_id}", json=payload).status_code
#         if not isinstance(resp, Response):
#             return self.get_microtenant(microtenant_id)

#     def delete_microtenant(self, microtenant_id: str) -> int:
#         """
#         Delete the specified microtenant.

#         Args:
#             microtenant_id (str): The unique identifier for the Microtenant to be deleted.

#         Returns:
#             :obj:`int`: The response code for the operation.

#         Examples:
#             >>> zpa.microtenant.delete_microtenant('99999')

#         """
#         return self.rest.delete(f"microtenants/{microtenant_id}").status_code
