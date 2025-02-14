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

from box import BoxList

from zscaler.api_client import APIClient
from zscaler.request_executor import RequestExecutor
from zscaler.zdx.models.ongoing_alerts import OngoingAlerts
from zscaler.utils import format_url
from zscaler.utils import zdx_params


class AlertsAPI(APIClient):
    
    def __init__(self, request_executor):
        super().__init__()
        self._request_executor: RequestExecutor = request_executor
        self._zdx_base_endpoint = "/zdx/v1"

    # @zdx_params
    def list_ongoing(self, query_params=None) -> tuple:
        """
        Returns a list of all ongoing alert rules across an organization in ZDX.

        Keyword Args:
            since (int): The number of hours to look back for devices.
            department_id (str): The unique ID for the department.
            geo_id (str): The unique ID for the geolocation.
            user_ids (list): List of user IDs.
            device_ids (list): List of device IDs.

        Returns:
            :obj:`tuple`: The list of software in ZDX.

        Examples:
            List all ongoing alerts in ZDX for the past 2 hours:

            >>> for alert in zdx.alerts.list_ongoing():
            ...     print(alert)

            List all ongoing alerts in ZDX for the past 24 hours:

            >>> for alert in zdx.alerts.list_ongoing(since=24):
            ...     print(alert)
        """
        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._zdx_base_endpoint}
            /alerts/ongoing
        """
        )

        query_params = query_params or {}

        # Prepare request body and headers
        body = {}
        headers = {}

        request, error = self._request_executor.\
            create_request(http_method, api_url, body, headers, params=query_params)

        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request)
        if error:
            return (None, response, error)

        try:
            result = []
            for item in response.get_results():
                result.append(OngoingAlerts(
                    self.form_response_body(item))
                )
        except Exception as error:
            return (None, response, error)
        return (result, response, None)

    # @zdx_params
    # def list_historical(self, **kwargs) -> BoxList:
    #     """
    #     Returns a list of all ongoing alert rules across an organization in ZDX.

    #     Keyword Args:
    #         since (int): The number of hours to look back for devices.
    #         department_id (str): The unique ID for the department.
    #         geo_id (str): The unique ID for the geolocation.
    #         user_ids (list): List of user IDs.
    #         device_ids (list): List of device IDs.

    #     Returns:
    #         :obj:`BoxList`: The list of software in ZDX.

    #     Examples:
    #         List all ongoing alerts in ZDX for the past 2 hours:

    #         >>> for alert in zdx.alerts.list_historical():
    #         ...     print(alert)

    #         List all ongoing alerts in ZDX for the past 24 hours:

    #         >>> for alert in zdx.alerts.list_historical(since=24):
    #         ...     print(alert)
    #     """
    #     filters = CommonFilters(**kwargs).to_dict()
    #     return ZDXIterator(self.rest, "alerts/historical", filters)

    # @zdx_params
    # def get_alert(self, alert_id: str, **kwargs):
    #     """
    #     Returns a single alert in ZDX.

    #     Args:
    #         alert_id (str): The unique ID for the alert.

    #     Keyword Args:
    #         since (int): The number of hours to look back for devices.

    #     Returns:
    #         :obj:`Tuple`: The ZDX device resource record.

    #     Examples:
    #         Get information for the device with an ID of 123456789.
    #         >>> device = zdx.alerts.get_alert('123456789')

    #         Get information for the device with an ID of 123456789 for the last 24 hours.
    #         >>> device = zdx.alerts.get_alert('123456789', since=24)

    #     """
    #     return self.rest.get(f"alerts/{alert_id}", params=kwargs)

    # @zdx_params
    # def list_affected_devices(self, alert_id, **kwargs) -> BoxList:
    #     """
    #     Returns a list of all all affected devices associated with
    #     an alert rule in conjunction with provided filters.

    #     Keyword Args:
    #         since (int): The number of hours to look back for devices.
    #         department_id (str): The unique ID for the department.
    #         geo_id (str): The unique ID for the geolocation.
    #         location_groups (list): List of location group IDs.

    #     Returns:
    #         :obj:`BoxList`: The list of software in ZDX.

    #     Examples:
    #         List all ongoing alerts in ZDX for the past 2 hours:

    #         >>> for alert in zdx.alerts.list_affected_devices():
    #         ...     print(alert)

    #         List all ongoing alerts in ZDX for the past 24 hours:

    #         >>> for alert in zdx.alerts.list_affected_devices(since=24):
    #         ...     print(alert)
    #     """
    #     filters = CommonFilters(**kwargs).to_dict()
    #     return ZDXIterator(self.rest, f"alerts/{alert_id}/affected_devices", filters)
