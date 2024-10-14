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
from zscaler.zpa.models.emergency_access import EmergencyAccessUser
from urllib.parse import urlencode
from zscaler.utils import format_url, snake_to_camel


class EmergencyAccessAPI(APIClient):
    """
    A Client object for the Emergency Access Users resource.
    """

    def __init__(self, request_executor, config):
        super().__init__()
        self._request_executor = request_executor
        customer_id = config["client"].get("customerId")
        self._base_endpoint = f"/zpa/mgmtconfig/v1/admin/customers/{customer_id}"

    def list_users(self, query_params=None, keep_empty_params=False) -> tuple:
        """
        Enumerates emergency access in your organization with pagination.
        A subset of emergency access can be returned that match a supported
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
        """
        http_method = "get".upper()
        api_url = format_url(f"{self._base_endpoint}/emergencyAccess/users")

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
        response, error = self._request_executor.execute(request, EmergencyAccessUser)

        if error:
            return (None, response, error)

        # Parse the response into AppConnectorGroup instances
        try:
            result = []
            for item in response.get_body():
                result.append(EmergencyAccessUser(self.form_response_body(item)))
        except Exception as error:
            return (None, response, error)

        return (result, response, None)

    def get_user(self, user_id: str, **kwargs) -> tuple:
        """
        Returns information on the specified emergency access user.

        Args:
            user_id (str): The unique identifier for the emergency access user.

        Returns:
            tuple: A tuple containing the `EmergencyAccessUser` instance, response object, and error if any.
        """
        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._base_endpoint}
            /emergencyAccess/user/{user_id}
        """
        )

        request, error = self._request_executor.create_request(http_method, api_url, {}, kwargs)
        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request, EmergencyAccessUser)
        if error:
            return (None, response, error)

        return (EmergencyAccessUser(response.get_body()), response, None)

    def add_user(
        self, email_id: str, first_name: str, last_name: str, user_id: str, activate_now: bool = True, **kwargs
    ) -> tuple:
        """
        Add an emergency access user.

        Args:
            email_id (str): The email address of the emergency access user.
            first_name (str): The first name of the emergency access user.
            last_name (str): The last name of the emergency access user.
            user_id (str): The unique identifier of the emergency access user.
            activate_now (bool, optional): Indicates if the emergency access user is activated upon creation. Defaults to True.

        Returns:
            tuple: A tuple containing the `EmergencyAccessUser` instance, response object, and error if any.
        """
        http_method = "post".upper()
        api_url = format_url(
            f"""
            {self._base_endpoint}
            /emergencyAccess/user
        """
        )

        payload = {
            "emailId": email_id,
            "firstName": first_name,
            "lastName": last_name,
            "userId": user_id,
        }

        # Include any additional attributes passed via kwargs
        payload.update({snake_to_camel(key): value for key, value in kwargs.items()})

        # Append 'activateNow=true' to the URL query parameters if activate_now is True
        query_params = {"activateNow": "true"} if activate_now else {}

        request, error = self._request_executor.create_request(http_method, api_url, payload, query_params)
        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request, EmergencyAccessUser)
        if error:
            return (None, response, error)

        return (EmergencyAccessUser(response.get_body()), response, None)

    def update_user(self, user_id: str, **kwargs) -> tuple:
        """
        Updates the specified emergency access user.

        Args:
            user_id (str): The unique identifier of the emergency access user.

        Keyword Args:
            email_id (str): The email address of the emergency access user.
            first_name (str): The first name of the emergency access user.
            last_name (str): The last name of the emergency access user.

        Returns:
            tuple: A tuple containing the `EmergencyAccessUser` instance, response object, and error if any.
        """
        http_method = "put".upper()
        api_url = format_url(
            f"""
            {self._base_endpoint}
            /emergencyAccess/user/{user_id}
        """
        )

        # Get current user data and update it
        current_user, response, error = self.get_user(user_id)
        if error:
            return (None, response, error)

        payload = current_user.request_format()
        payload.update({snake_to_camel(key): value for key, value in kwargs.items()})

        request, error = self._request_executor.create_request(http_method, api_url, payload)
        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request, EmergencyAccessUser)
        if error:
            return (None, response, error)

        return (EmergencyAccessUser(response.get_body()), response, None)

    def activate_user(self, user_id: str, send_email: bool = False) -> tuple:
        """
        Activates the emergency access user.

        Args:
            user_id (str): The unique identifier of the emergency access user.

        Returns:
            tuple: A tuple containing the `EmergencyAccessUser` instance, response object, and error if any.
        """
        http_method = "put".upper()
        api_url = format_url(
            f"""
            {self._base_endpoint}
            /emergencyAccess/user/{user_id}/activate
        """
        )

        query_params = {"sendEmail": "true"} if send_email else {}

        request, error = self._request_executor.create_request(http_method, api_url, {}, query_params)
        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request)
        if error:
            return (None, response, error)

        return self.get_user(user_id)

    def deactivate_user(self, user_id: str) -> tuple:
        """
        Deactivates the emergency access user.

        Args:
            user_id (str): The unique identifier of the emergency access user.

        Returns:
            tuple: A tuple containing the `EmergencyAccessUser` instance, response object, and error if any.
        """
        http_method = "put".upper()
        api_url = format_url(
            f"""
            {self._base_endpoint}
            /emergencyAccess/user/{user_id}/deactivate
        """
        )

        request, error = self._request_executor.create_request(http_method, api_url)
        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request)
        if error:
            return (None, response, error)

        return self.get_user(user_id)


# from box import Box, BoxList
# from requests import Response

# from zscaler.utils import snake_to_camel
# from zscaler.api_client import APIClient


# class EmergencyAccessAPI(APIClient):


#     def list_users(self, **kwargs) -> BoxList:
#         """
#         Returns a list of all configured Emergency Access Users.

#         Returns:
#             :obj:`BoxList`: A list of all configured Emergency Access Users.

#         Examples:
#             >>> for users in zpa.emergency_access.list_users():
#             ...    pprint(users)

#         """
#         list, _ = self.rest.get_paginated_data(path="/emergencyAccess/users", **kwargs, api_version="v1")
#         return list

#     def get_user(self, user_id: str) -> Box:
#         """
#         Returns information on the specified emergency access user.

#         Args:
#             portal_id (str):
#                 The unique identifier for the emergency access user.

#         Returns:
#             :obj:`Box`: The resource record for the emergency access user.

#         Examples:
#             >>> pprint(zpa.emergency_access.get_user('99999'))

#         """
#         return self.rest.get(f"emergencyAccess/user/{user_id}")

#     def add_user(
#         self,
#         email_id: str,
#         first_name: str,
#         last_name: str,
#         user_id: str,
#         activate_now: bool = True,
#         **kwargs,
#     ) -> Box:
#         """
#         Add an emergency access user.

#         Args:
#             email_id (str): The email address of the emergency access user, as provided by the admin.
#             first_name (str): The first name of the emergency access user.
#             last_name (str): The last name of the emergency access user, as provided by the admin.
#             user_id (str): The unique identifier of the emergency access user.
#             activate_now (bool, optional): Indicates if the emergency access user is activated upon creation. Defaults to True.

#             **kwargs: Optional keyword args for additional attributes.

#         Returns:
#             :obj:`Box`: The resource record for the newly created user or an error message.

#         Examples:
#             >>> zpa.emergency_access.add_user(
#             ...   email_id='user1Access@acme.com',
#             ...   first_name='User1',
#             ...   last_name='Access',
#             ...   user_id='user1',
#             ...   activate_now=True,
#             )
#         """
#         payload = {
#             "emailId": email_id,
#             "userId": user_id,
#             "firstName": first_name,
#             "lastName": last_name,
#         }

#         # Include any additional attributes passed via kwargs
#         for key, value in kwargs.items():
#             payload[snake_to_camel(key)] = value

#         # Append 'activateNow=true' to the URL query parameters if activate_now is True
#         query_params = {"activateNow": "true"} if activate_now else {}

#         response = self.rest.post("emergencyAccess/user", params=query_params, json=payload)
#         if isinstance(response, Response):
#             # this is only true when the creation failed (status code is not 2xx)
#             status_code = response.status_code
#             # Handle error response
#             raise Exception(f"API call failed with status {status_code}: {response.json()}")
#         return response

#     def update_user(self, user_id: str, **kwargs) -> Box:
#         """
#         Updates the specified emergency access user.

#         Args:
#             user_id (str): The unique identifier of the emergency access user.

#         Keyword Args:
#             email_id (str): The email address of the emergency access user, as provided by the admin.
#             first_name (str): The first name of the emergency access user.
#             last_name (str): The last name of the emergency access user, as provided by the admin.
#             user_id (str): The unique identifier of the emergency access user.

#         Returns:
#             Box: A Box object containing the details of the emergency access user.

#         Examples:
#             >>> zpa.emergency_access.update_user(
#             ...     user_id='99999',
#             ...     first_name='User1',
#             ...     last_name='Access')
#         """
#         # Set payload to value of existing record
#         payload = {snake_to_camel(k): v for k, v in self.get_user(user_id).items()}

#         # Add optional parameters to payload
#         for key, value in kwargs.items():
#             payload[snake_to_camel(key)] = value

#         resp = self.rest.put(f"emergencyAccess/user/{user_id}", json=payload)
#         if not isinstance(resp, Response):
#             return self.get_user(user_id)

#     def activate_user(self, user_id: str, send_email: bool = False) -> Box:
#         """
#         Activates the emergency access user.

#         Args:
#             user_id (str): The unique identifier of the emergency access user to be activated.

#         Returns:

#         Examples:
#             >>> zpa.emergency_access.activate_user('99999', send_email=True)

#         """
#         query_params = {"sendEmail": "true"} if send_email else {}

#         response = self.rest.put(f"emergencyAccess/user/{user_id}/activate", params=query_params)
#         if response.status_code == 200:
#             return self.get_user(user_id)
#         else:
#             raise Exception(f"API call failed with status {response.status_code}: {response.text}")

#     def deactivate_user(self, user_id: str) -> Box:
#         """
#         Deactivates the emergency access user.

#         Args:
#             user_id (str): The unique identifier of the emergency access user to be deactivated.

#         Returns:

#         Examples:
#             >>> zpa.emergency_access.deactivate_user('99999')

#         """
#         resp = self.rest.put(f"emergencyAccess/user/{user_id}/deactivate").status_code
#         if not isinstance(resp, Response):
#             return self.get_user(user_id)
