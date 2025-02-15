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
from zscaler.zdx.models.alerts import Alerts
from zscaler.zdx.models.alert_details import AlertDetails
from zscaler.utils import format_url, zdx_params

class AlertsAPI(APIClient):
    
    def __init__(self, request_executor):
        super().__init__()
        self._request_executor: RequestExecutor = request_executor
        self._zdx_base_endpoint = "/zdx/v1"

    @zdx_params
    def list_ongoing(self, query_params=None) -> tuple:
        """
        Returns a list of all ongoing alert rules across an organization in ZDX.
        All ongoing alert rules are returned if the search filter is not specified.
        The endpoint defaults to the previous 2 hours.
        Ongoing alerts are alerts that don't have an Ended On date.
        Note: Cannot exceed the 14-day time range limit for alert rules.

        Args:
            query_params {dict}: Map of query parameters for the request.
            
                ``[query_params.from]`` {int}: The start time (in seconds) for the query. 
                    The value is entered in Unix Epoch. 
                    If not entered, returns the data for the last 2 hours.
                    
                ``[query_params.to]`` {int}: The end time (in seconds) for the query.
                    The value is entered in Unix Epoch.
                    If not entered, returns the data for the last 2 hours.
                    
                ``[query_params.dept]`` {str}: The department ID. You can add multiple department IDs.

                ``[query_params.loc]`` {str}: The Zscaler location ID. You can add multiple location IDs.

                ``[query_params.geo]`` {str}: The active geolocation ID. You can add multiple active geolocation IDs.

                ``[query_params.offset]`` {str}: The next_offset value from the last request.
                    You must enter this value to get the next batch from the list.
                    When the next_offset value becomes null, the list is complete.

                ``[query_params.limit]`` {int}: The number of items that must be returned per request from the list.
                    Minimum: 1

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
                result.append(Alerts(
                    self.form_response_body(item))
                )
        except Exception as error:
            return (None, response, error)
        return (result, response, None)

    @zdx_params
    def list_historical(self, query_params=None) -> tuple:
        """
        Returns a list of alert history rules defined across an organization.
        All alert history rules are returned if the search filter is not specified. 
        The default is set to the previous 2 hours.
        Alert history rules have an Ended On date.
        Note: Cannot exceed the 14-day time range limit for alert rules.

        Args:
            query_params {dict}: Map of query parameters for the request.
            
                ``[query_params.from]`` {int}: The start time (in seconds) for the query. 
                    The value is entered in Unix Epoch. 
                    If not entered, returns the data for the last 2 hours.
                    
                ``[query_params.to]`` {int}: The end time (in seconds) for the query.
                    The value is entered in Unix Epoch.
                    If not entered, returns the data for the last 2 hours.
                    
                ``[query_params.dept]`` {str}: The department ID. You can add multiple department IDs.

                ``[query_params.loc]`` {str}: The Zscaler location ID. You can add multiple location IDs.

                ``[query_params.geo]`` {str}: The active geolocation ID. You can add multiple active geolocation IDs.

                ``[query_params.offset]`` {str}: The next_offset value from the last request.
                    You must enter this value to get the next batch from the list.
                    When the next_offset value becomes null, the list is complete.

                ``[query_params.limit]`` {int}: The number of items that must be returned per request from the list.
                    Minimum: 1

        Returns:
            :obj:`Tuple`: The list of alert history rules.

        Examples:
            List all ongoing alerts in ZDX for the past 2 hours:

            >>> for alert in zdx.alerts.list_historical():
            ...     print(alert)

            List all ongoing alerts in ZDX for the past 24 hours:

            >>> for alert in zdx.alerts.list_historical(since=24):
            ...     print(alert)
        """
        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._zdx_base_endpoint}
            /alerts/historical
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
                result.append(Alerts(
                    self.form_response_body(item))
                )
        except Exception as error:
            return (None, response, error)
        return (result, response, None)

    @zdx_params
    def get_alert(self, alert_id: str):
        """
        Returns details of a single alert including the impacted department, 
        Zscaler locations, geolocation, and alert trigger.

        Args:
            alert_id (str): The unique ID for the alert.

        Returns:
            :obj:`Tuple`: The ZDX alert detail resource record.

        Examples:
            Get information for the device with an ID of 123456789.
            >>> device = zdx.alerts.get_alert('123456789')

            Get information for the device with an ID of 123456789 for the last 24 hours.
            >>> device = zdx.alerts.get_alert('123456789', since=24)

        """
        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._zdx_base_endpoint}
            /alerts/{alert_id}
        """
        )

        body = {}
        headers = {}

        request, error = self._request_executor\
            .create_request(http_method, api_url, body, headers)

        if error:
            return (None, None, error)

        response, error = self._request_executor\
            .execute(request, AlertDetails)
        if error:
            return (None, response, error)

        try:
            result = AlertDetails(
                self.form_response_body(response.get_body())
            )
        except Exception as error:
            return (None, response, error)
        return (result, response, None)

    @zdx_params
    def list_affected_devices(self, alert_id, query_params=None) -> tuple:
        """
        Returns a list of all affected devices associated with
        an alert rule in conjunction with provided filters.
        (e.g., impacted department, locations, and geolocation) by using the Alert ID provided.

        Args:
            alert_id (str): The unique ID for the alert.

        Keyword Args:
            query_params {dict}: Map of query parameters for the request.
            
                ``[query_params.from]`` {int}: The start time (in seconds) for the query. 
                    The value is entered in Unix Epoch. 
                    If not entered, returns the data for the last 2 hours.
                    
                ``[query_params.to]`` {int}: The end time (in seconds) for the query.
                    The value is entered in Unix Epoch.
                    If not entered, returns the data for the last 2 hours.
                    
                ``[query_params.dept]`` {str}: The department ID. You can add multiple department IDs.

                ``[query_params.loc]`` {str}: The Zscaler location ID. You can add multiple location IDs.

                ``[query_params.geo]`` {str}: The active geolocation ID. You can add multiple active geolocation IDs.

                ``[query_params.offset]`` {str}: The next_offset value from the last request.
                    You must enter this value to get the next batch from the list.
                    When the next_offset value becomes null, the list is complete.

                ``[query_params.limit]`` {int}: The number of items that must be returned per request from the list.
                    Minimum: 1

                ``[query_params.location_groups]`` {int}: The location group ID. You can add multiple location group IDs.
                    Minimum: 1
                    
        Returns:
            :obj:`Tuple`: The list of software in ZDX.

        Examples:
            List of all affected devices associated with an alert rule for the past 2 hours:

            >>> for alert in zdx.alerts.list_affected_devices():
            ...     print(alert)

            List of all affected devices associated with an alert rule in ZDX for the past 24 hours:

            >>> for alert in zdx.alerts.list_affected_devices(since=24):
            ...     print(alert)
        """
        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._zdx_base_endpoint}
            /alerts/{alert_id}/affected_devices
        """
        )

        query_params = query_params or {}

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
                result.append(AlertDetails(
                    self.form_response_body(item))
                )
        except Exception as error:
            return (None, response, error)
        return (result, response, None)
