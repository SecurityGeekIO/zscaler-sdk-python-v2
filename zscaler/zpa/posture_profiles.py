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
from zscaler.zpa.models.posture_profiles import PostureProfile
from zscaler.utils import format_url, remove_cloud_suffix
from urllib.parse import urlencode


class PostureProfilesAPI(APIClient):
    """
    A Client object for the Posture Profiles resource.
    """

    def __init__(self, request_executor, config):
        super().__init__()
        self._request_executor = request_executor
        customer_id = config["client"].get("customerId")
        self._base_endpoint = f"/zpa/mgmtconfig/v1/admin/customers/{customer_id}"
        self._base_endpoint_v2 = f"/zpa/mgmtconfig/v2/admin/customers/{customer_id}"

    def list_posture_profiles(self, query_params=None, keep_empty_params=False) -> tuple:
        """
        Returns a list of all configured posture profiles.

        Keyword Args:
            max_items (int): The maximum number of items to request before stopping iteration.
            max_pages (int): The maximum number of pages to request before stopping iteration.
            pagesize (int): Specifies the page size. The default size is 20, but the maximum size is 500.
            search (str, optional): The search string used to match against features and fields.
            keep_empty_params (bool): Whether to include empty parameters in the query string.

        Returns:
            list: A list of `PostureProfile` instances.

        Example:
            >>> posture_profiles = zpa.posture_profiles.list_posture_profiles(search="example")
        """
        http_method = "get".upper()
        api_url = format_url(f"{self._base_endpoint_v2}/posture")

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
        response, error = self._request_executor.execute(request, PostureProfile)

        if error:
            return (None, response, error)

        # Parse the response into AppConnectorGroup instances
        try:
            result = []
            for item in response.get_body():
                result.append(PostureProfile(self.form_response_body(item)))
        except Exception as error:
            return (None, response, error)

        return (result, response, None)

    def get_profile(self, profile_id: str, query_params={}, keep_empty_params=False):
        """
        Gets a specific posture profile by its unique ID.

        Args:
            profile_id (str): The unique identifier of the posture profile.
            query_params (dict): Optional query parameters.
            keep_empty_params (bool): Whether to include empty query parameters in the request.

        Returns:
            tuple: A tuple containing (list of Posture Profile instances, Response, error)

        Example:
            >>> profile, response, error = zpa.posture_profiles.get_profile('12345')
            >>> if error is None:
            ...     pprint(profile)
        """
        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._base_endpoint}/posture/{profile_id}
        """
        )

        if query_params:
            encoded_query_params = urlencode(query_params)
            api_url += f"?{encoded_query_params}"

        body, headers, form = {}, {}, {}

        request, error = self._request_executor.create_request(
            http_method, api_url, body, headers, form, keep_empty_params=keep_empty_params
        )

        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request)

        if error:
            return (None, response, error)

        return response.get_body(), response, None

    def get_profile_by_name(self, name: str, query_params={}, keep_empty_params=False):
        """
        Returns a posture profile by its name.

        Args:
            name (str): The name of the posture profile.
            query_params (dict): Optional query parameters.
            keep_empty_params (bool): Whether to include empty query parameters.

        Returns:
            dict: The posture profile matching the specified name, or None if not found.

        Example:
            >>> profile, response, error = zpa.posture_profiles.get_profile_by_name('CrowdStrike_ZPA')
            >>> if error is None:
            ...     pprint(profile)
        """
        profiles, response, error = self.list_posture_profiles(query_params=query_params, keep_empty_params=keep_empty_params)
        if error:
            return (None, response, error)

        for profile in profiles:
            if profile.get("name") == name:
                return profile, response, None

        return None, response, None

    def get_udid_by_profile_name(self, search_name: str, query_params={}, keep_empty_params=False):
        """
        Searches for a posture profile by name and returns its posture_udid.

        Args:
            search_name (str): The name of the posture profile to search for.
            query_params (dict): Optional query parameters.
            keep_empty_params (bool): Whether to include empty query parameters.

        Returns:
            str: The posture_udid of the matching profile, or None if not found.

        Example:
            >>> udid, response, error = zpa.posture_profiles.get_udid_by_profile_name('CrowdStrike_ZPA')
            >>> if error is None:
            ...     print(f"Found Profile UDID: {udid}")
        """
        profiles, response, error = self.list_posture_profiles(query_params=query_params, keep_empty_params=keep_empty_params)
        if error:
            return (None, response, error)

        for profile in profiles:
            clean_profile_name = remove_cloud_suffix(profile.get("name"))
            if clean_profile_name == search_name or profile.get("name") == search_name:
                return profile.get("postureUdid"), response, None

        return None, response, None

    def get_name_by_posture_udid(self, search_udid: str, query_params={}, keep_empty_params=False):
        """
        Searches for a posture profile by posture_udid and returns its name.

        Args:
            search_udid (str): The posture_udid of the posture profile to search for.
            query_params (dict): Optional query parameters.
            keep_empty_params (bool): Whether to include empty query parameters.

        Returns:
            str: The name of the posture profile, or None if not found.

        Example:
            >>> name, response, error = zpa.posture_profiles.get_name_by_posture_udid('e2538bb9-af91-49bc-98ea')
            >>> if error is None:
            ...     print(f"Profile Name: {name}")
        """
        profiles, response, error = self.list_posture_profiles(query_params=query_params, keep_empty_params=keep_empty_params)
        if error:
            return (None, response, error)

        for profile in profiles:
            if profile.get("postureUdid") == search_udid:
                return profile.get("name"), response, None

        return None, response, None
