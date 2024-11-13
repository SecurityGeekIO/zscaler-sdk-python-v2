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
from zscaler.zia.models.pac_files import PacFiles
from zscaler.utils import format_url


class PacFilesAPI(APIClient):
    """
    A Client object for the Rule labels resource.
    """

    _zia_base_endpoint = "/zia/api/v1"

    def __init__(self, request_executor):
        super().__init__()
        self._request_executor: RequestExecutor = request_executor

    def list_pac_files(self, query_params=None) -> tuple:
        """
        Lists pac files in your organization with pagination.
        A subset of pac files can be returned that match a supported
        filter expression or query.

        Args:
            query_params {dict}: Map of query parameters for the request.
                [query_params.search] {str}: Search string for filtering results.

        Returns:
            tuple: A tuple containing (list of Pac Files instances, Response, error)

        Examples:
            List all Pac Files using default settings:
            >>> pac_files, response, err = zia.pac_files.list_pac_files()

        """
        http_method = "get".upper()
        api_url = format_url(f"""
            {self._zia_base_endpoint}
            /pacFiles
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
        response, error = self._request_executor.execute(request)

        if error:
            return (None, response, error)

        try:
            result = []
            for item in response.get_all_pages_results():
                result.append(PacFiles(
                    self.form_response_body(item))
                )
        except Exception as error:
            return (None, response, error)
        return (result, response, None)

    def get_pac_file(self, pac_id: int, query_params=None) -> tuple:
        """
        Retrieves all versions of a PAC file based on the specified ID

        Args:
            pac_id (int): The unique identifier for the Pac File.

        Returns:
            tuple: A tuple containing (Pac File instance, Response, error).
        """
        http_method = "get".upper()
        api_url = format_url(f"""
            {self._zia_base_endpoint}
            /pacFiles/{pac_id}/version
        """)

        query_params = query_params or {}

        request, error = self._request_executor.create_request(
            method=http_method, 
            endpoint=api_url, 
            params=query_params
        )

        if error:
            return (None, None, error)

        response, error = self._request_executor\
            .execute(request, PacFiles)
        if error:
            return (None, response, error)

        try:
            result = PacFiles(
                self.form_response_body(response.get_body())
            )
        except Exception as error:
            return (None, response, error)
        
        return (result, response, None)
    
    def validate_pac_file(self) -> tuple:
        """
        Sends the PAC file content for validation and returns the validation result.

        Args:
            body (str): PAC file content

        Returns:
            tuple: A tuple containing (intermediate CA certificate instance, Response, error).
        """
        http_method = "post".upper()
        api_url = format_url(f"""
            {self._zia_base_endpoint}
            /pacFiles/validate
        """)

        body = {}
        headers = {}

        request, error = self._request_executor\
            .create_request(http_method, api_url, body, headers)
        if error:
            return (None, None, error)

        response, error = self._request_executor\
            .execute(request)
        if error:
            return (None, response, error)

        try:
            result = (
                self.form_response_body(response.get_body())
            )
        except Exception as error:
            return (None, response, error)
        return (result, response, None)

    def delete_pac_file(self, pac_id: int) -> tuple:
        """
        Deletes an existing PAC file including all of its versions based on the specified ID

        Args:
            pac_id (str): Specifies the ID of the PAC file

        Returns:
            tuple: A tuple containing the response object and error (if any).
        """
        http_method = "delete".upper()
        api_url = format_url(f"""
            {self._zia_base_endpoint}
            /pacFiles/{pac_id}
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