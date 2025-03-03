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
from zscaler.utils import format_url

class IncidentsAPI(APIClient):

    def __init__(self, request_executor):
        super().__init__()
        self._request_executor: RequestExecutor = request_executor
        self._zwa_base_endpoint = "/zwa/dlp/v1"
        
    def list_incidents(
        self,
        query_params=None
    ) -> tuple:
        """
        Returns information DLP incident details based on the incident ID.

        Args:
            incident_id (str): The ID of the incident.

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
            /incidents
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
                result.append((
                    self.form_response_body(item))
                )
        except Exception as error:
            return (None, response, error)
        return (result, response, None)
