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
from zscaler.zdx.models.call_quality_metrics import CallQualityMetrics
from zscaler.zdx.models.devices import Devices
from zscaler.zdx.models.device_model_info import DeviceModelInfo
from zscaler.zdx.models.device_app_score_trend import DeviceAppScoreTrend
from zscaler.zdx.models.device_apps_webprobes import DeviceWebProbePageFetch
from zscaler.zdx.models.device_app_cloud_path_probes import DeviceAppCloudPathProbes
from zscaler.zdx.models.device_cloud_path_probes_metric import DeviceCloudPathProbesMetric
from zscaler.zdx.models.device_cloud_path_probes_hopdata import DeviceCloudPathProbesHopData
from zscaler.utils import format_url, zdx_params

class DevicesAPI(APIClient):
    
    def __init__(self, request_executor):
        super().__init__()
        self._request_executor: RequestExecutor = request_executor
        self._zdx_base_endpoint = "/zdx/v1"

    @zdx_params
    def list_devices(
        self,
        query_params=None
    ) -> tuple:
        """
        Returns a list of all active devices and its basic details.
        If the time range is not specified, the endpoint defaults to the previous 2 hours. 

        Keyword Args:
            query_params {dict}: Map of query parameters for the request.
            
                ``[query_params.since]`` {int}: The number of hours to look back for devices.
                    
                ``[query_params.location_id]`` {int}: The unique ID for the location.

                ``[query_params.department_id]`` {str}: The unique ID for the department.

                ``[query_params.geo_id]`` {str}: The unique ID for the geolocation.
                
                ``[query_params.user_ids]`` {list}: List of user IDs.                             

                ``[query_params.emails]`` {list}: List of email addresses.    

                ``[query_params.mac_address]`` {str}: MAC address of the device.

                ``[query_params.private_ipv4]`` {str}: Private IPv4 address of the device.

        Returns:
            :obj:`Tuple`: The list of devices in ZDX.

        Examples:
            List all devices in ZDX for the past 2 hours:

            >>> for device in zdx.devices.list_devices():

            List all devices in ZDX for the past 24 hours:

            >>> for device in zdx.devices.list_devices(since=24):

        """
        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._zdx_base_endpoint}
            /devices
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
                result.append(Devices(
                    self.form_response_body(item))
                )
        except Exception as error:
            return (None, response, error)
        return (result, response, None)

    @zdx_params
    def get_device(
        self,
        device_id: str, 
        query_params=None
    ) -> tuple:
        """
        Returns a single device in ZDX.

        Args:
            device_id (str): The unique ID for the device.

        Keyword Args:
            query_params {dict}: Map of query parameters for the request.
            
                ``[query_params.since]`` {int}: The number of hours to look back for devices.

        Returns:
            :obj:`Tuple`: The ZDX device resource record.

        Examples:
            Get information for the device with an ID of 123456789.
            >>> device = zdx.devices.get_device('123456789')

            Get information for the device with an ID of 123456789 for the last 24 hours.
            >>> device = zdx.devices.get_device('123456789', since=24)

        """
        http_method = "get".upper()
        api_url = format_url(f"""
            {self._zdx_base_endpoint}
            /devices/{device_id}
        """)

        query_params = query_params or {}
        
        body = {}
        headers = {}

        request, error = self._request_executor\
            .create_request(http_method, api_url, body, headers, params=query_params)

        if error:
            return (None, None, error)

        response, error = self._request_executor\
            .execute(request, DeviceModelInfo)
        if error:
            return (None, response, error)

        try:
            result = DeviceModelInfo(
                self.form_response_body(response.get_body())
            )
        except Exception as error:
            return (None, response, error)
        return (result, response, None)

    @zdx_params
    def get_device_apps(
        self,
        device_id: str,
        query_params=None
    ) -> tuple:
        """
        Returns a list of all active applications for a device.

        Args:
            device_id (str): The unique ID for the device.

        Keyword Args:
            query_params {dict}: Map of query parameters for the request.
            
                ``[query_params.since]`` {int}: The number of hours to look back for devices.

        Returns:
            :obj:`Tuple`: The list of active applications for the device.

        Examples:
            Print a list of active applications for a device.

            >>> for app in zdx.devices.get_device_apps('123456789'):
            ...     print(app)

            Print a list of active applications for a device for the last 24 hours.

            >>> for app in zdx.devices.get_device_apps('123456789', since=24):
            ...     print(app)

        """
        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._zdx_base_endpoint}
            /devices/{device_id}/apps
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
                result.append(self.form_response_body(item))
        except Exception as error:
            return (None, response, error)
        return (result, response, None)

    def get_device_app(
        self,
        device_id: str,
        app_id: str
    ) -> tuple:
        """
        Returns a single application for a device.

        Args:
            device_id (str): The unique ID for the device.
            app_id (str): The unique ID for the application.

        Returns:
            :obj:`Tuple`: The application resource record.

        Examples:
            Print a single application for a device.

            >>> app = zdx.devices.get_device_app('123456789', '987654321')
            ... print(app)

        """
        http_method = "get".upper()
        api_url = format_url(f"""
            {self._zdx_base_endpoint}
            /devices/{device_id}/apps/{app_id}
        """)

        body = {}
        headers = {}

        request, error = self._request_executor\
            .create_request(http_method, api_url, body, headers)

        if error:
            return (None, None, error)

        response, error = self._request_executor\
            .execute(request, DeviceAppScoreTrend)
        if error:
            return (None, response, error)

        try:
            result = DeviceAppScoreTrend(
                self.form_response_body(response.get_body())
            )
        except Exception as error:
            return (None, response, error)
        return (result, response, None)

    @zdx_params
    def get_web_probes(
        self,
        device_id: str,
        app_id: str,
        query_params=None
    ) -> tuple:
        """
        Returns a list of all active web probes for a specific application being used by a device.

        Args:
            device_id (str): The unique ID for the device.
            app_id (str): The unique ID for the application.

        Keyword Args:
            query_params {dict}: Map of query parameters for the request.
            
                ``[query_params.since]`` {int}: The number of hours to look back for devices.

        Returns:
            :obj:`Tuple`: The list of web probes for the application.

        Examples:
            Print a list of web probes for an application.

            >>> for probe in zdx.devices.get_web_probes('123456789', '987654321'):
            ...     print(probe)

        """
        http_method = "get".upper()
        api_url = format_url(f"""
            {self._zdx_base_endpoint}
            /devices/{device_id}/apps/{app_id}/web-probes
        """)

        query_params = query_params or {}

        # Prepare request body and headers
        body = {}
        headers = {}

        # Create the request
        request, error = self._request_executor\
            .create_request(http_method, api_url, body, headers, params=query_params)

        if error:
            return (None, None, error)

        # Execute the request
        response, error = self._request_executor\
            .execute(request)

        if error:
            return (None, response, error)

        try:
            result = []
            for item in response.get_results():
                result.append(self.form_response_body(item))
        except Exception as error:
            return (None, response, error)
        return (result, response, None)

    @zdx_params
    def get_web_probe(
        self, device_id: str,
        app_id: str,
        probe_id: str,
        query_params=None
    ) -> tuple:
        """
        Returns a single web probe for a specific application being used by a device.

        Args:
            device_id (str): The unique ID for the device.
            app_id (str): The unique ID for the application.
            probe_id (str): The unique ID for the web probe.

        Keyword Args:
            query_params {dict}: Map of query parameters for the request.
            
                ``[query_params.since]`` {int}: The number of hours to look back for devices.

        Returns:
            :obj:`Tuple`: The web probe resource record.

        Examples:
            Print a single web probe for an application.

            >>> probe = zdx.devices.get_web_probe('123456789', '987654321', '123987456')
            ... print(probe)

        """
        http_method = "get".upper()
        api_url = format_url(f"""
            {self._zdx_base_endpoint}
            /devices/{device_id}/apps/{app_id}/web-probes/{probe_id}
        """)

        query_params = query_params or {}
        
        body = {}
        headers = {}

        request, error = self._request_executor\
            .create_request(http_method, api_url, body, headers, params=query_params)

        if error:
            return (None, None, error)

        response, error = self._request_executor\
            .execute(request, DeviceWebProbePageFetch)
        if error:
            return (None, response, error)

        try:
            result = []
            for item in response.get_results():
                result.append(DeviceWebProbePageFetch(
                    self.form_response_body(item))
                )
        except Exception as error:
            return (None, response, error)
        return (result, response, None)

    @zdx_params
    def list_cloudpath_probes(
        self,
        device_id: str,
        app_id: str,
        query_params=None
    ) -> tuple:
        """
        Returns a list of all active cloudpath probes for a specific application being used by a device.

        Args:
            device_id (str): The unique ID for the device.
            app_id (str): The unique ID for the application.

        Keyword Args:
            since (int): The number of hours to look back for devices.

        Returns:
            :obj:`Tuple`: The list of cloudpath probes for the application.

        Examples:
            Print a list of cloudpath probes for an application.

            >>> for probe in zdx.devices.list_cloudpath_probes('123456789', '987654321'):
            ...     print(probe)

        """
        http_method = "get".upper()
        api_url = format_url(f"""
            {self._zdx_base_endpoint}
            /devices/{device_id}/apps/{app_id}/cloudpath-probes
        """)

        query_params = query_params or {}

        # Prepare request body and headers
        body = {}
        headers = {}

        # Create the request
        request, error = self._request_executor\
            .create_request(http_method, api_url, body, headers, params=query_params)

        if error:
            return (None, None, error)

        # Execute the request
        response, error = self._request_executor\
            .execute(request)

        if error:
            return (None, response, error)

        try:
            result = []
            for item in response.get_results():
                result.append(DeviceAppCloudPathProbes(
                    self.form_response_body(item))
                )
        except Exception as error:
            return (None, response, error)
        return (result, response, None)
    
    @zdx_params
    def get_cloudpath_probe(
        self,
        device_id: str,
        app_id: str,
        probe_id: str,
        query_params=None):
        """
        Returns a single cloudpath probe for a specific application being used by a device.

        Args:
            device_id (str): The unique ID for the device.
            app_id (str): The unique ID for the application.
            probe_id (str): The unique ID for the cloudpath probe.

        Keyword Args:
            since (int): The number of hours to look back for devices.

        Returns:
            :obj:`Tuple`: The cloudpath probe resource record.

        Examples:
            Print a single cloudpath probe for an application.

            >>> probe = zdx.devices.get_cloudpath_probe('123456789', '987654321', '123987456')
            ... print(probe)

        """
        http_method = "get".upper()
        api_url = format_url(f"""
            {self._zdx_base_endpoint}
            /devices/{device_id}/apps/{app_id}/cloudpath-probes/{probe_id}
        """)

        query_params = query_params or {}
        
        body = {}
        headers = {}

        request, error = self._request_executor\
            .create_request(http_method, api_url, body, headers, params=query_params)

        if error:
            return (None, None, error)

        response, error = self._request_executor\
            .execute(request, DeviceCloudPathProbesMetric)
        if error:
            return (None, response, error)

        try:
            result = []
            for item in response.get_results():
                result.append(DeviceCloudPathProbesMetric(
                    self.form_response_body(item))
                )
        except Exception as error:
            return (None, response, error)
        return (result, response, None)

    @zdx_params
    def get_cloudpath(
        self,
        device_id: str,
        app_id: str,
        probe_id: str,
        query_params=None
    ) -> tuple:
        """
        Returns a single cloudpath for a specific application being used by a device.

        Args:
            device_id (str): The unique ID for the device.
            app_id (str): The unique ID for the application.
            probe_id (str): The unique ID for the cloudpath probe.

        Keyword Args:
            since (int): The number of hours to look back for devices.

        Returns:
            :obj:`Tuple`: The cloudpath resource record.

        Examples:
            Print a single cloudpath for an application.

            >>> cloudpath = zdx.devices.get_cloudpath('123456789', '987654321', '123987456')
            ... print(cloudpath)

        """
        http_method = "get".upper()
        api_url = format_url(f"""
            {self._zdx_base_endpoint}
            /devices/{device_id}/apps/{app_id}/cloudpath-probes/{probe_id}/cloudpath
        """)

        query_params = query_params or {}

        body = {}
        headers = {}

        request, error = self._request_executor\
            .create_request(http_method, api_url, body, headers, params=query_params)

        if error:
            return (None, None, error)

        response, error = self._request_executor\
            .execute(request)

        if error:
            return (None, response, error)

        try:
            result = []
            for item in response.get_results():
                result.append(DeviceCloudPathProbesHopData(
                    self.form_response_body(item))
                )
        except Exception as error:
            return (None, response, error)
        return (result, response, None)

    @zdx_params
    def get_call_quality_metrics(
        self,
        device_id: str,
        app_id: str,
        query_params=None
    ) -> tuple:
        """
        Returns a single call quality metrics for a specific application being used by a device.

        Args:
            device_id (str): The unique ID for the device.
            app_id (str): The unique ID for the application.

        Keyword Args:
            since (int): The number of hours to look back for devices.

        Returns:
            :obj:`Tuple`: The call quality metrics resource record.

        Examples:
            Print call quality metrics for an application.

            >>> metrics = zdx.devices.get_call_quality_metrics('123456789', '987654321')
            ... print(metrics)

        """
        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._zdx_base_endpoint}
            /devices/{device_id}/apps/{app_id}/call-quality-metrics
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
                result.append(CallQualityMetrics(
                    self.form_response_body(item))
                )
        except Exception as error:
            return (None, response, error)
        return (result, response, None)

    # @zdx_params
    # def get_health_metrics(self, device_id: str, **kwargs):
    #     """
    #     Returns health metrics trend for a specific device.

    #     Args:
    #         device_id (str): The unique ID for the device.

    #     Keyword Args:
    #         since (int): The number of hours to look back for devices.

    #     Returns:
    #         :obj:`Tuple`: The health metrics resource record.

    #     Examples:
    #         Print health metrics for an application.

    #         >>> metrics = zdx.devices.get_health_metrics('123456789')
    #         ... print(metrics)

    #     """
    #     return self.rest.get(f"devices/{device_id}/health-metrics", params=kwargs)

    # def get_events(self, device_id: str):
    #     """
    #     Returns a list of all events for a specific device.

    #     Args:
    #         device_id (str): The unique ID for the device.

    #     Returns:
    #         :obj:`Tuple`: The list of events for the device.

    #     Examples:
    #         Print a list of events for a device.

    #         >>> for event in zdx.devices.get_events('123456789'):
    #         ...     print(event)

    #     """
    #     return self.rest.get(f"devices/{device_id}/events")

    # def get_deeptrace_webprobe_metrics(self, device_id: str, trace_id: str):
    #     """
    #     Returns web probe metrics for a specific deeptrace.

    #     Args:
    #         device_id (str): The unique ID for the device.
    #         trace_id (str): The unique ID for the deeptrace.

    #     Returns:
    #         :obj:`Tuple`: The deeptrace web probe metrics.

    #     Examples:
    #         Print web probe metrics for a deeptrace.

    #         >>> metrics = zdx.devices.get_deeptrace_webprobe_metrics('123456789', '987654321')
    #         ... print(metrics)

    #     """
    #     return self.rest.get(f"devices/{device_id}/deeptraces/{trace_id}/webprobe-metrics")

    # def get_deeptrace_cloudpath_metrics(self, device_id: str, trace_id: str):
    #     """
    #     Returns cloudpath metrics for a specific deeptrace.

    #     Args:
    #         device_id (str): The unique ID for the device.
    #         trace_id (str): The unique ID for the deeptrace.

    #     Returns:
    #         :obj:`Tuple`: The deeptrace cloudpath metrics.

    #     Examples:
    #         Print cloudpath metrics for a deeptrace.

    #         >>> metrics = zdx.devices.get_deeptrace_cloudpath_metrics('123456789', '987654321')
    #         ... print(metrics)

    #     """
    #     return self.rest.get(f"devices/{device_id}/deeptraces/{trace_id}/cloudpath-metrics")

    # def get_deeptrace_cloudpath(self, device_id: str, trace_id: str):
    #     """
    #     Returns cloudpath for a specific deeptrace.

    #     Args:
    #         device_id (str): The unique ID for the device.
    #         trace_id (str): The unique ID for the deeptrace.

    #     Returns:
    #         :obj:`Tuple`: The deeptrace cloudpath.

    #     Examples:
    #         Print cloudpath for a deeptrace.

    #         >>> metrics = zdx.devices.get_deeptrace_cloudpath('123456789', '987654321')
    #         ... print(metrics)

    #     """
    #     return self.rest.get(f"devices/{device_id}/deeptraces/{trace_id}/cloudpath")

    # def get_deeptrace_health_metrics(self, device_id: str, trace_id: str):
    #     """
    #     Returns health metrics for a specific deeptrace.

    #     Args:
    #         device_id (str): The unique ID for the device.
    #         trace_id (str): The unique ID for the deeptrace.

    #     Returns:
    #         :obj:`Tuple`: The deeptrace health metrics.

    #     Examples:
    #         Print health metrics for a deeptrace.

    #         >>> metrics = zdx.devices.get_deeptrace_health_metrics('123456789', '987654321')
    #         ... print(metrics)

    #     """
    #     return self.rest.get(f"devices/{device_id}/deeptraces/{trace_id}/health-metrics")

    # def get_deeptrace_events(self, device_id: str, trace_id: str):
    #     """
    #     Returns events for a specific deeptrace.

    #     Args:
    #         device_id (str): The unique ID for the device.
    #         trace_id (str): The unique ID for the deeptrace.

    #     Returns:
    #         :obj:`Tuple`: The deeptrace events.

    #     Examples:
    #         Print events for a deeptrace.

    #         >>> events = zdx.devices.get_deeptrace_events('123456789', '987654321')
    #         ... print(events)

    #     """
    #     return self.rest.get(f"devices/{device_id}/deeptraces/{trace_id}/events")

    # def get_deeptrace_top_processes(self, device_id: str, trace_id: str):
    #     """
    #     Returns top processes for a specific deeptrace.

    #     Args:
    #         device_id (str): The unique ID for the device.
    #         trace_id (str): The unique ID for the deeptrace.

    #     Returns:
    #         :obj:`Tuple`: The deeptrace top processes.

    #     Examples:
    #         Print top processes for a deeptrace.

    #         >>> top_processes = zdx.devices.get_deeptrace_top_processes('123456789', '987654321')
    #         ... print(top_processes)

    #     """
    #     return self.rest.get(f"devices/{device_id}/deeptraces/{trace_id}/top-processes")

    # @zdx_params
    # def list_geolocations(self, **kwargs) -> BoxList:
    #     """
    #     Returns a list of all active geolocations configured within the ZDX tenant.

    #     Keyword Args:
    #         since (int): The number of hours to look back for devices.
    #         location_id (str): The unique ID for the location.
    #         parent_geo_id (str): The unique ID for the parent geolocation.
    #         search (str): The search string to filter by name.

    #     Returns:
    #         :obj:`Tuple`: The list of geolocations in ZDX.

    #     Examples:
    #         List all geolocations in ZDX for the past 2 hours:

    #         >>> for geolocation in zdx.admin.list_geolocations():
    #         ...     print(geolocation)

    #     """
    #     filters = GeoLocationFilter(**kwargs).to_dict()
    #     return BoxList(ZDXIterator(self.rest, "active_geo", filters=filters))
