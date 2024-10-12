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
from zscaler.zia.models.authentication_settings import AuthenticationSettings
from zscaler.utils import format_url

class AuthenticationSettingsAPI(APIClient):
    """
    A Client object for the Authentication Settings resource.
    """

    _zia_base_endpoint = "/zia/api/v1"
    
    def __init__(self, request_executor):
        super().__init__()
        self._request_executor = request_executor

    def get_exempted_urls(self) -> tuple:
        """
        Returns a list of exempted URLs.

        Returns:
            tuple: A tuple containing (AuthenticationSettings instance, Response, error)

        Examples:
            >>> exempted_urls, response, error = zia.authentication_settings.get_exempted_urls()
        """
        http_method = "get".upper()
        api_url = format_url(f"""
            {self._zia_base_endpoint}
            /authSettings/exemptedUrls
        """)

        # Prepare request body and headers
        body = {}
        headers = {}

        request, error = self._request_executor.create_request(
            http_method, api_url, body, headers
        )

        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request)

        if error:
            return (None, response, error)

        try:
            result = []
            for item in response.get_body():
                result.append(AuthenticationSettings(
                    self.form_response_body(item)
                ))
        except Exception as error:
            return (None, response, error)

        return (result, response, None)

    def add_urls_to_exempt_list(self, url_list: list) -> tuple:
        """
        Adds the provided URLs to the exempt list.

        Args:
            url_list (:obj:`list` of :obj:`str`): The list of URLs to be added.

        Returns:
            tuple: A tuple containing (updated AuthenticationSettings instance, Response, error)

        Examples:
            >>> exempted_urls, response, error = zia.authentication_settings.add_urls_to_exempt_list(["example.com"])
        """
        http_method = "post".upper()
        api_url = format_url(f"""
            {self._zia_base_endpoint}
            /authSettings/exemptedUrls?action=ADD_TO_LIST
            """)

        payload = {"urls": url_list}

        # Prepare request body and headers
        body = {}
        headers = {}

        request, error = self._request_executor.create_request(
            http_method, api_url, payload, body, headers
        )

        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request, AuthenticationSettings)

        if error:
            return (None, response, error)

        return self.get_exempted_urls()

    def delete_urls_from_exempt_list(self, url_list: list) -> tuple:
        """
        Deletes the provided URLs from the exemption list.

        Args:
            url_list (:obj:`list` of :obj:`str`): The list of URLs to be removed.

        Returns:
            tuple: A tuple containing (updated AuthenticationSettings instance, Response, error)

        Examples:
            >>> exempted_urls, response, error = zia.authentication_settings.delete_urls_from_exempt_list(["example.com"])
        """
        http_method = "post".upper()
        api_url = format_url(f"""
            {self._zia_base_endpoint}
            /authSettings/exemptedUrls?action=REMOVE_FROM_LIST
        """)

        payload = {"urls": url_list}

        request, error = self._request_executor.create_request(
            http_method, api_url, payload, {}, {}
        )

        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request, AuthenticationSettings)

        if error:
            return (None, response, error)

        return self.get_exempted_urls()
