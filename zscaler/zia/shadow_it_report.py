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
from zscaler.zia.models.shadow_it_report import ShadowITReport
from zscaler.zia.models.shadow_it_report import CloudapplicationsAndTags
from zscaler.zia.models.shadow_it_report import CloudApplicationBulkUpdate
from zscaler.utils import format_url
from urllib.parse import urlencode

class ShadowITReport(APIClient):
    """
    A Client object for the predefined and custom Cloud Applications resource.
    """
    def __init__(self):
        super().__init__()
        self._base_url = ""

    def list_cloud_applications_list(
            self, query_params=None,
            keep_empty_params=False
    ) -> tuple:
        """
        Enumerates the list of predefined and custom Cloud Applications in your organization with pagination.
        A subset of predefined and custom Cloud Applications can be returned that match a supported
        filter expression or query.

        Args:
            query_params {dict}: Map of query parameters for the request.
                [query_params.page_number] {int}: Specifies the page number. The numbering starts at 0.
                [query_params.limit] {int}: Specifies the maximum number of cloud applications that must be retrieved in a page.
                [query_params.search] {str}: Search string for filtering results.
                [query_params.max_items] {int}: Maximum number of items to fetch before stopping.
                [query_params.max_pages] {int}: Maximum number of pages to request before stopping.
            keep_empty_params {bool}: Whether to include empty parameters in the query string.

        Returns:
            tuple: A tuple containing (list of Rule Labels instances, Response, error)

        Examples:
            List Cloud Applications life using default settings:

            >>> for label in zia.shadow_it_report.list_cloud_applications_list():
            ...   print(label)

            >>> for label in zia.shadow_it_report.list_cloud_applications_list(limit=10):
            ...    print(label)

        """
        http_method = "get".upper()
        api_url = format_url(f"{self._base_url}/cloudApplications/lite")

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
        response, error = self._request_executor.execute(request, CloudapplicationsAndTags)

        if error:
            return (None, response, error)

        try:
            result = []
            for item in response.get_body():
                result.append(CloudapplicationsAndTags(
                    self.form_response_body(item)
                ))
        except Exception as error:
            return (None, response, error)

        return (result, response, None)
    
    def list_custom_tags(self) -> tuple:
            """
            Enumerates the list of custom tags available to assign to cloud applications in your organization with pagination.
            A subset of custom tags can be returned that match a supported

            Returns:
                tuple: A tuple containing (list of Custom Tags instances, Response, error)

            Examples:
                List Cloud Applications life using default settings:

                >>> for tags in zia.shadow_it_report.list_custom_tags():
                ...   print(tags)


            """
            # Set the HTTP method and API URL
            http_method = "get".upper()
            api_url = f"{self._base_url}/customTags"

            # Prepare the request (GET request, no body needed)
            request, error = self._request_executor.create_request(
                http_method, api_url, body=None, headers={}, form=None, keep_empty_params=False
            )

            if error:
                return (None, None, error)

            # Execute the request
            response, error = self._request_executor.execute(request, CloudapplicationsAndTags)

            if error:
                return (None, response, error)

            try:
                result = []
                for item in response.get_body():
                    result.append(CloudapplicationsAndTags(self.form_response_body(item)))
            except Exception as error:
                return (None, response, error)

            return (result, response, None)
    
    def bulk_update_cloud_application(self, application_ids: list, sanctioned_state: str, custom_tags: list = None) -> tuple:
        """
        Updates application status and tag information for predefined or custom cloud applications based on the IDs specified.

        Args:
            application_ids (list): The list of application IDs to update.
            sanctioned_state (str): The sanctioned state of the application (e.g., 'UN_SANCTIONED').
            custom_tags (list, optional): A list of custom tag dictionaries (each containing 'id' and 'name').

        Returns:
            tuple: A tuple containing the response body, the response object, and any error.

        Examples:
            Update cloud applications with new tags and sanctioned state::

                >>> zia.cloudappcontrol.bulk_update_cloud_application(
                ...     [123, 456],
                ...     sanctioned_state="SANCTIONED",
                ...     custom_tags=[{"id": 1, "name": "Tag1"}, {"id": 2, "name": "Tag2"}]
                ... )
        """
        http_method = "put".upper()
        api_url = format_url(f"{self._base_url}/cloudApplications/bulkUpdate")

        # Create payload object using the CloudApplicationBulkUpdate model
        payload_obj = CloudApplicationBulkUpdate({
            "sanctionedState": sanctioned_state,
            "applicationIds": application_ids,
            "customTags": custom_tags if custom_tags is not None else []
        })

        # Convert payload object to the request format
        payload = payload_obj.request_format()

        request, error = self._request_executor.create_request(http_method, api_url, payload, {}, {})
        if error:
            return (None, None, error)

        response, error = self._request_executor.execute(request)

        if error:
            return (None, response, error)

        return (response.get_body(), response, None)
