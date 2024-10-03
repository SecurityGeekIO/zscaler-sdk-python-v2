import json
import time


class ZscalerAPIResponse:
    """
    Class for defining the wrapper of a Zscaler API response.
    Allows for paginated results to be retrieved easily.
    """

    def __init__(self, request_executor, req, res_details=None, response_body="", data_type=None):
        # Safely handle None values for res_details
        self._url = res_details.url if res_details and hasattr(res_details, 'url') else None
        self._headers = req["headers"] if "headers" in req else {}
        self._resp_headers = res_details.headers if res_details and hasattr(res_details, 'headers') else {}
        self._self = None  # Link to first page of results
        self._body = None  # First page of results
        self._type = data_type
        self._status = res_details.status if res_details and hasattr(res_details, 'status') else None
        self._request_executor = request_executor  # Request Executor for future calls

        # Build response body based on content type (supports only JSON)
        if res_details and hasattr(res_details, 'content_type') and "application/json" in res_details.content_type:
            self.build_json_response(response_body)
        else:
            # Save response as plain text if not JSON
            self._body = response_body

    def get_headers(self):
        """
        Returns the response headers of the Zscaler API Response.
        """
        return self._resp_headers

    def get_body(self):
        """
        Returns the response body of the Zscaler API Response.
        """
        return self._body

    def get_status(self):
        """
        Returns HTTP Status Code of response.
        """
        return self._status

    def build_json_response(self, response_body):
        """
        Converts JSON response text into Python dictionary.
        """
        self._body = json.loads(response_body)

# Move the pagination function outside of the class as a standalone function

def get_paginated_data(
    request_executor,
    path=None,
    params=None,
    expected_status_code=200,
    api_version: str = None,
    search=None,
    search_field="name",
    max_pages=None,
    max_items=None,
    all_entries=False,
    sort_order=None,
    sort_by=None,
    sort_dir=None,
    start_time=None,
    end_time=None,
    microtenant_id=None,
    page=None,
    pagesize=None,
    keep_empty_params=False,
):
    """
    Fetches paginated data from the Zscaler API based on specified parameters and handles various types of API pagination.
    """

    if params is None:
        params = {}

    # If `keep_empty_params` is False, remove any empty params from the dictionary
    if not keep_empty_params:
        params = {k: v for k, v in params.items() if v or v == 0}

    # Initialize the pagination params
    params["page"] = page if page is not None else 1  # Default to page 1
    params["pagesize"] = min(pagesize if pagesize is not None else 20, 500)  # Default pagesize is 20, max 500

    if search:
        params["search"] = f"{search_field} EQ {search}"
    if sort_order:
        params["sortOrder"] = sort_order
    if sort_by:
        params["sortBy"] = sort_by
    if sort_dir:
        params["sortdir"] = sort_dir
    if start_time and end_time:
        params["startTime"] = start_time
        params["endTime"] = end_time
    if all_entries:
        params["allEntries"] = all_entries
    if microtenant_id:
        params["microtenantId"] = microtenant_id

    total_collected = 0
    ret_data = []

    try:
        while True:
            # Use the correct request_executor method, for GET we use `get`
            response, error = request_executor.get(url=path, params=params)

            if error:
                return [], f"Error occurred during request: {error}"

            if response.get("status_code", 200) != expected_status_code:
                return [], f"Unexpected status code {response.get('status_code')}"

            # Process response
            current_response = ZscalerAPIResponse(
                request_executor=request_executor,
                req={"headers": response.get("headers")},
                res_details=response,
                response_body=response.get("body")
            )

            # Collect response data for this page
            ret_data.extend(current_response.get_body().get("list", []))
            total_collected += len(current_response.get_body().get("list", []))

            # Check if we should stop paginating
            if (max_items and total_collected >= max_items) or not current_response.get_body().get("list"):
                break

            params["page"] += 1  # Move to next page

    except Exception as e:
        return [], str(e)

    return ret_data, None
