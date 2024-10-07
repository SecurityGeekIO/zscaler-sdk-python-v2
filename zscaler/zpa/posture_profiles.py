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

    def __init__(self):
        super().__init__()  # Inherit initialization from APIClient
        self._base_url = ""

    def list_posture_profiles(
            self, query_params=None,
            keep_empty_params=False
    ) -> tuple:
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
        api_url = format_url(f"{self._base_url}/posture")

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
                result.append(PostureProfile(
                    self.form_response_body(item)
                ))
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
            {self._base_url}/posture/{profile_id}
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
        profiles, response, error = self.list_profiles(query_params=query_params, keep_empty_params=keep_empty_params)
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
        profiles, response, error = self.list_profiles(query_params=query_params, keep_empty_params=keep_empty_params)
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
        profiles, response, error = self.list_profiles(query_params=query_params, keep_empty_params=keep_empty_params)
        if error:
            return (None, response, error)

        for profile in profiles:
            if profile.get("postureUdid") == search_udid:
                return profile.get("name"), response, None

        return None, response, None


# from box import Box, BoxList
# from requests import Response

# from zscaler.utils import remove_cloud_suffix

# from zscaler.api_client import APIClient


# class PostureProfilesAPI(APIClient):

#     def list_profiles(self, **kwargs) -> BoxList:
#         """
#         Returns a list of all configured posture profiles.

#         Keyword Args:
#             max_items (int):
#                 The maximum number of items to request before stopping iteration.
#             max_pages (int):
#                 The maximum number of pages to request before stopping iteration.
#             pagesize (int):
#                 Specifies the page size. The default size is 20, but the maximum size is 500.
#             search (str, optional):
#                 The search string used to match against features and fields.

#         Returns:
#             BoxList: A list of all configured posture profiles.

#         Examples:
#             >>> for posture_profile in zpa.posture_profiles.list_profiles():
#             ...    pprint(posture_profile)
#         """
#         list, _ = self.rest.get_paginated_data(path="/posture", **kwargs, api_version="v2")
#         return list

#     def get_profile_by_name(self, name):
#         """
#         Searches for and returns a posture profile based on its name.

#         This method performs a case-sensitive search through all posture profiles,
#         returning the first profile that matches the specified name exactly.

#         Args:
#             name (str): The name of the posture profile to search for.

#         Returns:
#             Box: The posture profile that matches the given name, or None if no match is found.

#         Examples:
#             >>> profile = zpa.posture_profiles.get_profile_by_name("Example Profile Name")
#             >>> if profile:
#             ...     print("Profile ID:", profile.id)
#             ... else:
#             ...     print("Profile not found.")
#         """
#         profiles = self.list_profiles()
#         for profile in profiles:
#             if profile.get("name") == name:
#                 return profile
#         return None

#     def get_profile(self, profile_id: str) -> Box:
#         """
#         Returns information on the specified posture profiles.

#         Args:
#             profile_id (str):
#                 The unique identifier for the posture profiles.

#         Returns:
#             :obj:`Box`: The resource record for the posture profiles.

#         Examples:
#             >>> pprint(zpa.posture_profiles.get_profile('99999'))

#         """
#         response = self.rest.get("/posture/%s" % (profile_id))
#         if isinstance(response, Response):
#             status_code = response.status_code
#             if status_code != 200:
#                 return None
#         return response

#     def get_udid_by_profile_name(self, search_name: str, **kwargs) -> str:
#         """
#         Searches for a posture profile by name and returns its posture_udid.

#         This function searches through all configured posture profiles, comparing the
#         provided search_name against each profile's name, both exactly and with any cloud suffix removed.
#         It returns the 'posture_udid' of the first matching profile found.

#         Args:
#             search_name (str): The name of the posture profile to search for.

#         Keyword Args:
#             **kwargs: Additional keyword arguments to pass to the list_profiles method, such as
#                     'max_items', 'max_pages', 'pagesize', and 'search'.

#         Returns:
#             str: The posture_udid of the found posture profile, or None if not found.

#         Examples:
#             >>> udid = zpa.posture_profiles.get_udid_by_profile_name("Example Profile")
#             >>> if udid:
#             ...     print(f"Found Profile UDID: {udid}")
#             ... else:
#             ...     print("Profile not found.")
#         """
#         profiles = self.list_profiles(**kwargs)
#         for profile in profiles:
#             clean_profile_name = remove_cloud_suffix(profile.get("name"))
#             if clean_profile_name == search_name or profile.get("name") == search_name:
#                 return profile.get("posture_udid")
#         return None

#     def get_name_by_posture_udid(self, search_udid: str, **kwargs) -> str:
#         """
#         Searches for a posture profile by posture_udid and returns its name.

#         Args:
#             search_udid (str): The posture_udid of the posture profile to search for.

#         Keyword Args:
#             **kwargs: Additional keyword arguments to pass to the list_profiles method.

#         Returns:
#             str: The name of the found posture profile, or None if not found.
#         """
#         profiles = self.list_profiles(**kwargs)
#         for profile in profiles:
#             if profile.get("posture_udid") == search_udid:
#                 return profile.get("name")
#         return None
