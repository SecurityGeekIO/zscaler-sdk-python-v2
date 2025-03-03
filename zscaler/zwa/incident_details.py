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
from zscaler.zwa.models.incident_details import IncidentDLPDetails
from zscaler.utils import format_url

class IncidentDetailAPI(APIClient):

    def __init__(self, request_executor):
        super().__init__()
        self._request_executor: RequestExecutor = request_executor
        self._zwa_base_endpoint = "/zwa/dlp/v1"
        
    def get_incident_details(
        self,
        incident_id: str,
        query_params=None
    ) -> tuple:
        """
        Returns information DLP incident details based on the incident ID.

        Args:
            incident_id (str): The ID of the incident.

        Keyword Args:
            query_params {dict}: Map of query parameters for the request.
            
                ``[query_params.fields]`` {list}: The fields associated with the DLP incident. 
                    For example, sourceActions, contentInfo, status, resolution, etc.

        Returns:
            :obj:`Tuple`: The incident details information.

        Examples:
            Return information on the application with the ID of 999999999:

            >>> apps, _, err = client.zdx.apps.get_app('1')
            ... if err:
            ...      print(f"Error listing application: {err}")
            ...     return
            ... for app in apps:
            ...     print(app.as_dict())
        """
        http_method = "get".upper()
        api_url = format_url(
            f"""
            {self._zwa_base_endpoint}
            /incidents/{incident_id}
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
            result = [IncidentDLPDetails(
                self.form_response_body(response.get_body()))]  
        except Exception as error:
            return (None, response, error)

        return (result, response, None)
    
    def delete_incident(self, incident_id: int) -> tuple:
        """
        Deletes the specified Incident for specified ID.

        Args:
            label_id (str): The unique identifier of the Incident.

        Returns:
            tuple: A tuple containing the response object and error (if any).
        """
        http_method = "delete".upper()
        api_url = format_url(f"""
            {self._zia_base_endpoint}
            /incidents/{incident_id}
        """)

        params = {}

        request, error = self._request_executor\
            .create_request(http_method, api_url, params=params)
        if error:
            return (None, None, error)

        response, error = self._request_executor\
            .execute(request)
        if error:
            return (None, response, error)
        return (None, response, None)
