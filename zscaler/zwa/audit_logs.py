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
from zscaler.zwa.models.audit_logs import AuditLogs
from zscaler.utils import format_url

class DLPIncidentsAPI(APIClient):

    def __init__(self, request_executor):
        super().__init__()
        self._request_executor: RequestExecutor = request_executor
        self._zwa_base_endpoint = "/zwa/dlp/v1"


    def dlp_incident_search(self, query_params=None, fields=None, time_range=None, **kwargs) -> tuple:
        """
        Filters audit logs based on the specified time period and field values.
        The result includes audit information for every action made by the admins
        in the Workflow Automation Admin Portal and the actions made through APIs.

        The supported field values are:
            - `Action`
            - `Resource`
            - `Admin`
            - `Module`

        The supported time range values are:
            - `Start date and time`
            - `End date and time`

        Args:
            query_params {dict}: Map of query parameters for the request.
                ``[query_params.page]`` {int}: Specifies the page number of the incident in a multi-paginated response.
                                            This field is not required if `page_id` is used.
                ``[query_params.page_size]`` {int}: Specifies the page size (i.e., number of incidents per page). Max: 100.
                ``[query_params.page_id]`` {str}: Specifies the page ID of the incident in a multi-paginated response.
                                                The page ID can be used instead of the page number.

            fields (list, optional): A list of field filters. Example:
                ```
                [
                    {"name": "severity", "value": ["high"]},
                    {"name": "status", "value": ["open", "resolved"]}
                ]
                ```

            time_range (dict, optional): Time range for filtering incidents. Example:
                ```
                {
                    "startTime": "2025-03-03T18:04:52.074Z",
                    "endTime": "2025-03-03T18:04:52.074Z"
                }
                ```

        Returns:
            :obj:`Tuple`: The incident search results.

        Examples:
            Perform an incident search with severity filter:
            ```
            search, _, error = client.zwa.incident_search.dlp_incident_search(
                fields=[{"name": "severity", "value": ["high"]}],
                time_range={"startTime": "2025-03-03T18:04:52.074Z", "endTime": "2025-03-03T18:04:52.074Z"}
            )
            ```
        """
        http_method = "post".upper()
        api_url = format_url(f"{self._zwa_base_endpoint}/customer/audit")

        query_params = query_params or {}

        body = {"fields": fields or [], "timeRange": time_range or {}}

        body.update(kwargs)

        # Create the request
        request, error = self._request_executor.create_request(
            method=http_method,
            endpoint=api_url,
            params=query_params,
            body=body,
        )

        if error:
            return (None, None, error)

        response, error = self._request_executor.\
            execute(request, AuditLogs)
        if error:
            return (None, response, error)

        try:
            result = AuditLogs(
                self.form_response_body(response.get_body())
            )
        except Exception as error:
            return (None, response, error)
        return (result, response, None)