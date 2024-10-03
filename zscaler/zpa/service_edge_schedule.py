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

import os
from zscaler.api_client import APIClient
from zscaler.zpa.models.service_edge_schedule import ServiceEdgeSchedule
from zscaler.utils import format_url, snake_to_camel


class ServiceEdgeScheduleAPI(APIClient):
    """
    A Client object for the Service Edge Schedule resource.
    """

    def __init__(self):
        super().__init__()
        self._base_url = ""
    
    def get_service_edge_schedule(self, customer_id=None, **kwargs) -> tuple:
        """
        Returns the configured Service Edge Schedule frequency.

        Args:
            customer_id (str, optional): Unique identifier of the ZPA tenant. If not provided, will look up from env var.

        Returns:
            tuple: A tuple containing (ServiceEdgeSchedule, Response, error)
        """
        customer_id = customer_id or os.getenv("ZPA_CUSTOMER_ID")
        if not customer_id:
            return (
                None,
                None,
                ValueError(
                    "customer_id is required either as a function argument or as an environment variable ZPA_CUSTOMER_ID"
                ),
            )
        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._base_url}
            /connectorSchedule
        """
        )

        microtenant_id = kwargs.pop("microtenant_id", None)
        params = {"microtenantId": microtenant_id} if microtenant_id else {}

        request, error = self._request_executor.create_request(http_method, api_url, params=params)
        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request)
        if error:
            return (None, response, error)

        result = ServiceEdgeSchedule(response.get_body())
        return (result, response, None)

    def add_service_edge_schedule(self, frequency, interval, disabled, enabled, **kwargs) -> tuple:
        """
        Configure an App Connector schedule frequency to delete inactive connectors based on the configured frequency.

        Args:
            frequency (str): Frequency at which disconnected App Connectors are deleted.
            interval (str): Interval for the frequency value.
            disabled (bool): Whether to include disconnected connectors for deletion.
            enabled (bool): Whether the deletion setting is enabled.

        Returns:
            tuple: A tuple containing (ServiceEdgeSchedule, Response, error)
        """
        customer_id = kwargs.get("customer_id") or os.getenv("ZPA_CUSTOMER_ID")
        if not customer_id:
            return (
                None,
                None,
                ValueError(
                    "customer_id is required either as a function argument or as an environment variable ZPA_CUSTOMER_ID"
                ),
            )
        http_method = "post".upper()
        api_url = format_url(
            f"""
            {self._base_url}
            /connectorSchedule
        """
        )

        payload = {
            "customerId": customer_id,
            "frequency": frequency,
            "frequencyInterval": interval,
            "deleteDisabled": disabled,
            "enabled": enabled,
        }

        for key, value in kwargs.items():
            payload[snake_to_camel(key)] = value

        request, error = self._request_executor.create_request(http_method, api_url, json=payload)
        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request)
        if error:
            return (None, response, error)

        result = ServiceEdgeSchedule(payload)
        return (result, response, None)

    def update_service_edge_schedule(self, scheduler_id: str, frequency, interval, disabled, enabled, **kwargs) -> tuple:
        """
        Updates App Connector schedule frequency to delete inactive connectors based on the configured frequency.

        Args:
            scheduler_id (str): Unique identifier for the schedule.
            frequency (str): Frequency at which disconnected App Connectors are deleted.
            interval (str): Interval for the frequency value.
            disabled (bool): Whether to include disconnected connectors for deletion.
            enabled (bool): Whether the deletion setting is enabled.

        Returns:
            tuple: A tuple containing (ServiceEdgeSchedule, Response, error)
        """
        customer_id = kwargs.get("customer_id") or os.getenv("ZPA_CUSTOMER_ID")
        if not customer_id:
            return (
                None,
                None,
                ValueError(
                    "customer_id is required either as a function argument or as an environment variable ZPA_CUSTOMER_ID"
                ),
            )

        http_method = "put".upper()
        api_url = format_url(
            f"""
            {self._base_url}
            /connectorSchedule/{scheduler_id}
        """
        )
        
        payload = {
            "customerId": customer_id,
            "frequency": frequency,
            "frequencyInterval": interval,
            "deleteDisabled": disabled,
            "enabled": enabled,
        }

        for key, value in kwargs.items():
            payload[snake_to_camel(key)] = value

        request, error = self._request_executor.create_request(http_method, api_url, json=payload)
        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request)
        if error:
            return (None, response, error)

        updated_schedule, _, error = self.get_connector_schedule(customer_id=customer_id)
        return (updated_schedule, response, None)


