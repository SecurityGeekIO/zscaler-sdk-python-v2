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
from zscaler.zia.models.devices import Devices
from zscaler.zia.models.device_groups import DeviceGroups
from zscaler.utils import format_url
from urllib.parse import urlencode


class DeviceManagementAPI(APIClient):
    """
    A Client object for the Device Management resource.
    """

    def __init__(self):
        super().__init__()
        self._base_url = ""

    def list_device_groups(
            self, query_params=None,
            keep_empty_params=False
    ) -> tuple:
        """
        Returns the list of ZIA Device Groups.

        Args:
            query_params {dict}: Map of query parameters for the request.
                [query_params.page] {int}: Specifies the page offset.
                [query_params.pagesize] {int}: Specifies the page size. The default size is 100, but the maximum size is 1000.
                [query_params.max_items] {int}: Maximum number of items to fetch before stopping.
                [query_params.max_pages] {int}: Maximum number of pages to request before stopping.
            keep_empty_params {bool}: Whether to include empty parameters in the query string.

        Returns:
            tuple: A tuple containing (list of Device Group instances, Response, error)

        Examples:
            Print all device groups

            >>> for device group in zia.device_groups.list_device_groups():
            ...    pprint(device)

            Print Device Groups that match the name or description 'Windows'

            >>> pprint(zia.device_groups.list_device_groups('Windows'))

        """
        http_method = "get".upper()
        api_url = format_url(f"{self._base_url}/zia/api/v1/deviceGroups")

        query_params = query_params or {}

        if query_params:
            encoded_query_params = urlencode(query_params)
            api_url += f"?{encoded_query_params}"

        body = {}
        headers = {}
        form = {}

        request, error = self._request_executor.create_request(
            http_method, api_url, body, headers, form, keep_empty_params=keep_empty_params
        )

        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request, DeviceGroups)

        if error:
            return (None, response, error)

        try:
            result = []
            for item in response.get_body():
                result.append(DeviceGroups(
                    self.form_response_body(item)
                ))
        except Exception as error:
            return (None, response, error)

        return (result, response, None)

    def list_devices(
            self, query_params=None,
            keep_empty_params=False
    ) -> tuple:
        """
        Returns the list of Devices.

        Args:
            query_params {dict}: Map of query parameters for the request.
                [query_params.name] {str}: The device group name. This is a `starts with` match.
                [query_params.userIds] {list}: Used to list devices for specific users.
                [query_params.includeAll] {bool}: Used to include or exclude Cloud Browser Isolation devices.                       
                [query_params.page] {int}: Specifies the page offset.
                [query_params.pagesize] {int}: Specifies the page size. The default size is 100, but the maximum size is 1000.
                [query_params.max_items] {int}: Maximum number of items to fetch before stopping.
                [query_params.max_pages] {int}: Maximum number of pages to request before stopping.
            keep_empty_params {bool}: Whether to include empty parameters in the query string.

        Returns:
            tuple: A tuple containing (list of Devices instances, Response, error)


        Examples:
            Print all devices

            >>> for dlp device in zia.device_groups.list_devices():
            ...    pprint(device)

            Print Devices that match the name or description 'WINDOWS_OS'

            >>> pprint(zia.device_groups.list_devices('WINDOWS_OS'))

        """
        http_method = "get".upper()
        api_url = format_url(f"{self._base_url}/zia/api/v1/deviceGroups/devices")

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
        response, error = self._request_executor.execute(request, Devices)

        if error:
            return (None, response, error)

        # Parse the response into AdminUser instances
        try:
            result = []
            for item in response.get_body():
                result.append(Devices(
                    self.form_response_body(item)
                ))
        except Exception as error:
            return (None, response, error)

        return (result, response, None)

    def list_device_lite(self) -> tuple:
        """
        Returns the list of devices that includes device ID, name, and owner name.

        Returns:
            tuple: List of Device/ids.

        Examples:
            Get Device Lite results

            >>> results = zia.device.list_device_lite()
            ... for item in results:
            ...    print(item)

        """
        http_method = "get".upper()
        api_url = format_url(f"{self._base_url}/zia/api/v1/deviceGroups/devices/lite")

        # Prepare the request (GET request, no body needed)
        request, error = self._request_executor.create_request(
            http_method, api_url, body=None, headers={}, form=None, keep_empty_params=False
        )

        if error:
            return (None, None, error)

        # Execute the request
        response, error = self._request_executor.execute(request, DeviceGroups)

        if error:
            return (None, response, error)

        # Parse the response into Application instances
        try:
            result = []
            for item in response.get_body():
                result.append(DeviceGroups(self.form_response_body(item)))
        except Exception as error:
            return (None, response, error)

        return (result, response, None)
