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
from zscaler.utils import format_url, zcc_param_map
from zscaler.zcc.models.devices import Device
from datetime import datetime


class DevicesAPI(APIClient):

    def __init__(self, request_executor):
        super().__init__()
        self._request_executor: RequestExecutor = request_executor
        self._zcc_base_endpoint = "/zcc/papi/public/v1"

    def download_devices(
        self,
        filename: str = None,
        os_types: list = None,
        registration_types: list = None,
    ):
        """
        Downloads the list of devices in the Client Connector Portal as a CSV file.

        By default, this method will create a file named `zcc-devices-YYmmDD-HH_MM_SS.csv`. This can be overridden by
        specifying the ``filename`` argument.

        Notes:
            This API endpoint is heavily rate-limited by Zscaler and as of NOV 2022 only 3 calls per-day are allowed.

        Args:
            filename (str):
                The name of the file that you want to save to disk.
            os_types (list):
                A list of OS Types to filter the device list. Omitting this argument will result in all OS types being
                matched.
                Valid options are:

                - ios
                - android
                - windows
                - macos
                - linux
            registration_types (list):
                A list of device registration states to filter the device list.
                Valid options are:

                - all (provides all states except for 'removed')
                - registered
                - removal_pending
                - unregistered
                - removed
                - quarantined

        Returns:
            :obj:`str`: The local filename for the CSV file that was downloaded.

        Examples:
            Create a CSV with all OS types and all registration types:

            >>> zcc.devices.download_devices(registration_types=["all", "removed"])

            Create a CSV for Windows and macOS devices that are in the `registered` state:

            >>> zcc.devices.download_devices(os_types=["windows", "macos"],
            ...     registration_types=["registered"])

            Create a CSV with filename `unregistered.csv` for devices in the unregistered state:

            >>> zcc.devices.download_devices(filename="unregistered.csv",
            ...     registration_types=["unregistered"])

        """

        if not filename:
            filename = f"zcc-devices-{datetime.now().strftime('%Y%m%d-%H_%M_%S')}.csv"

        params = {}

        # Simplify the os_type argument, raise an error if the user supplies the wrong one.
        if os_types:
            for item in os_types:
                os_type = zcc_param_map["os"].get(item, None)
                if os_type:
                    if "osTypes" not in params:
                        params["osTypes"] = str(os_type)
                    else:
                        params["osTypes"] += "," + str(os_type)
                else:
                    raise ValueError("Invalid os_type specified. Check the pyZscaler documentation for valid os_type options.")

        # Simplify the registration_type argument, raise an error if the user supplies the wrong one.
        if registration_types:
            for item in registration_types:
                reg_type = zcc_param_map["reg_type"].get(item, None)
                if reg_type:
                    if "registrationTypes" not in params:
                        params["registrationTypes"] = str(reg_type)
                    else:
                        params["registrationTypes"] += "," + str(reg_type)
                else:
                    raise ValueError(
                        "Invalid registration_type specified. Check the pyZscaler documentation for valid "
                        "registration_type options."
                    )

        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._zcc_base_endpoint}
            /downloadDevices
        """
        )

        request, error = self._request_executor.create_request(http_method, api_url, params=params)
        if error:
            raise Exception("Error creating request for downloading devices.")

        with open(filename, "wb") as f:
            response, error = self._request_executor.execute(request)
            if error:
                raise Exception("Error executing request for downloading devices.")
            f.write(response.content)

        return filename

    def list_devices(self, query_params=None) -> tuple:
        """
        Returns the list of devices enrolled in the Client Connector Portal.

        Keyword Args:
            os_type (str):
                Filter by device operating system. Valid options are:

                - ios
                - android
                - windows
                - macos
                - linux
            page (int):
                Return a specific page number.
            page_size (int):
                Specify the number of devices per page, defaults to ``30``.
            user_name (str):
                Filter by the enrolled user for the device.

        Returns:
            :obj:`list`: A list containing devices using ZCC enrolled in the Client Connector Portal.

        Examples:
            Prints all devices in the Client Connector Portal to the console:

            >>> for device in zcc.devices.list_devices():
            ...    print(device)

        """
        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._zcc_base_endpoint}
            /getDevices
        """
        )

        query_params = query_params or {}

        # Prepare request body and headers
        body = {}
        headers = {}

        request, error = self._request_executor.create_request(http_method, api_url, body, headers, params=query_params)

        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request)
        if error:
            return (None, response, error)

        try:
            result = []
            for item in response.get_all_pages_results():
                result.append(Device(self.form_response_body(item)))
        except Exception as error:
            return (None, response, error)
        return (result, response, None)

    def remove_devices(self, remove) -> tuple:
        """
        Removes the specified devices from the Zscaler Client Connector Portal.

        Notes:
            You must be using API credentials with the `Write` role.
            You must specify at least one criterion from `Keyword Args` to remove devices.

        Args:
            force (bool):
                Setting force to ``True`` removes the enrolled device from the portal. You can only remove devices that
                are in the `registered` or `device removal pending` state.
            **kwargs:
                Optional keyword args.

        Keyword Args:
            client_connector_version (list):
                A list of client connector versions that will be removed. You must supply the exact version number, i.e.
                if the Client Connector version is `3.2.0.18` you must specify `3.2.0.18` and not `3.2`.
            os_type (str):
                The OS Type for the devices to be removed. Valid options are:

                - ios
                - android
                - windows
                - macos
                - linux
            udids (list):
                A list of Unique Device IDs.
            user_name (str):
                The username of the user whose devices will be removed.

        Returns:
            :obj:`Box`: Server response containing the total number of devices removed.

        Examples:
            Soft-remove devices using ZCC version 3.7.1.44 from the Client Connector Portal:

            >>> zcc.devices.remove_devices(client_connector_version=["3.7.1.44"])

            Soft-remove Android devices from the Client Connector Portal:

            >>> zcc.devices.remove_devices(os_type="android")

            Hard-remove devices from the Client Connector Portal by UDID:

            >>> zcc.devices.remove_devices(force=True, udids=["99999", "88888", "77777"])

            Hard-remove Android devices for johnno@widgets.co from the Client Connector Portal:

            >>> zcc.devices.remove_devices(force=True, os_type="android",
            ...     user_name="johnno@widgets.co")

        """
        http_method = "post".upper()
        api_url = format_url(
            f"""
            {self._zcc_base_endpoint}
            /removeDevices
        """
        )

        # payload = convert_keys(dict(kwargs))

        if isinstance(remove, dict):
            body = remove
        else:
            body = remove.as_dict()

        request, error = self._request_executor.create_request(
            method=http_method,
            endpoint=api_url,
            body=body,
        )

        if error:
            return None, None, error

        response, error = self._request_executor.execute(request)
        if error:
            return None, response, error

        return None, response, None
