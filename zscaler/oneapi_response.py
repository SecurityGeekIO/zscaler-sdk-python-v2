import json


class ZscalerAPIResponse:
    """
    Class for defining the wrapper of a Zscaler API response.
    Handles paginated results and accounts for service-specific behavior like
    ZPA, ZIA, ZCC pagination and ZDX with offset/limit pagination.
    """

    # Default and max page sizes for ZPA, ZIA, and ZDX
    SERVICE_PAGE_LIMITS = {
        "ZPA": {"default": 20, "max": 500},
        "ZIA": {"default": 100, "max": 1000},
        "ZDX": {"default": 10, "min": 1},  # ZDX has limit with minimum 1
    }

    def __init__(
        self,
        request_executor,
        req,
        service_type,
        res_details=None,
        response_body="",
        data_type=None,
        max_items=None,
        max_pages=None,
        all_entries=False,
        sort_order=None,
        sort_by=None,
        sort_dir=None,
        start_time=None,
        end_time=None,
    ):
        # Safely handle None values for res_details
        self._url = res_details.url if res_details and hasattr(res_details, "url") else None
        self._headers = req.get("headers", {})  # Headers for the request
        self._params = req.get("params", {})  # Query parameters like filtering and pagination
        self._resp_headers = res_details.headers if res_details and hasattr(res_details, "headers") else {}
        self._body = None  # First page of results
        self._type = data_type
        self._status = res_details.status if res_details and hasattr(res_details, "status") else None
        self._request_executor = request_executor  # Request Executor for future calls

        # Custom options
        self._max_items = max_items  # Max number of items to return, if provided
        self._max_pages = max_pages  # Max number of pages to return, if provided
        self._items_fetched = 0  # Tracks the total number of items fetched
        self._pages_fetched = 0  # Tracks the total number of pages fetched

        # Pagination and query parameters
        self._service_type = service_type
        self._offset = self._params.get("offset", 0)  # Start with offset 0 for ZDX
        self._limit = self.validate_page_size(self._params.get("limit"), service_type)  # Validate limit for ZDX
        self._next_offset = None  # To track next_offset for ZDX
        self._list = []  # To store the list of results

        # Adding optional query parameters for ZPA
        if all_entries:
            self._params["allEntries"] = True
        if sort_order:
            self._params["sortOrder"] = sort_order
        if sort_by:
            self._params["sortBy"] = sort_by
        if sort_dir:
            self._params["sortDir"] = sort_dir
        if start_time:
            self._params["startTime"] = start_time
        if end_time:
            self._params["endTime"] = end_time

        # Build response body based on content type (supports only JSON)
        if res_details:
            content_type = res_details.headers.get("Content-Type", "").lower()
            if "application/json" in content_type:
                self.build_json_response(response_body)
            else:
                # Attempt to parse as JSON, if fails, save as plain text
                try:
                    self.build_json_response(response_body)
                except json.JSONDecodeError:
                    # Save response as plain text if not JSON
                    self._body = response_body
        else:
            # If no res_details, assume it's JSON and try to parse
            try:
                self.build_json_response(response_body)
            except json.JSONDecodeError:
                # Save response as plain text if not JSON
                self._body = response_body

    def validate_page_size(self, page_size, service_type):
        """
        Validates the page size based on the service type.
        Uses service-specific max and default page sizes.
        """
        limits = self.SERVICE_PAGE_LIMITS.get(service_type, {})
        max_page_size = limits.get("max", 100)  # Default max if service_type not found
        default_page_size = limits.get("default", 20)  # Default page size

        # If page_size is not provided, use default; otherwise, cap it at the max limit.
        if page_size is None:
            return default_page_size
        return min(max(int(page_size), limits.get("min", 1)), max_page_size)

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
        Converts JSON response text into Python dictionary or list depending on the service.
        Handles ZPA's totalPages/totalCount, ZIA's raw list response, and ZDX offset/limit.
        """
        self._body = json.loads(response_body)

        if isinstance(self._body, list):
            # ZIA response is just a list of items
            self._list = self._body
        elif self._service_type == "ZDX":
            # ZDX response structure with offset and limit handling
            self._list = self._body.get("items", [])
            self._next_offset = self._body.get("next_offset")
        else:
            # ZPA response contains structured metadata like totalPages
            self._list = self._body.get("list", [])
            if self._service_type == "ZPA":
                self._total_pages = int(self._body.get("totalPages", 1))  # totalPages from the API response
                self._total_count = int(self._body.get("totalCount", 0))  # totalCount from the API response

        # Track the number of items fetched in the current page
        self._items_fetched += len(self._list)
        self._pages_fetched += 1

    def get_total_count(self):
        """
        Returns the total number of items in the API response (if available for ZPA).
        """
        if self._service_type == "ZPA":
            return self._total_count
        return None  # ZIA and ZDX do not provide totalCount

    def has_next(self):
        """
        Determines if there are more pages to fetch.
        - For ZPA: Checks if the current page is less than totalPages.
        - For ZIA and ZCC: Continues fetching until no data is returned.
        - For ZDX: Continues fetching until next_offset becomes null.
        - Custom: Stops if max_items or max_pages limits are reached.
        """
        if self._max_items is not None and self._items_fetched >= self._max_items:
            return False  # Stop if we've reached the max number of items
        if self._max_pages is not None and self._pages_fetched >= self._max_pages:
            return False  # Stop if we've reached the max number of pages

        if self._service_type == "ZPA":
            return self._page < self._total_pages
        elif self._service_type == "ZDX":
            return self._next_offset is not None
        else:
            return bool(self._list)  # For ZIA and ZCC, stop when no data is returned

    def next(self):
        """
        Fetches the next page of results.
        - Stops for ZIA and ZCC when no data is returned.
        - For ZPA, stops when the total number of pages is reached.
        - For ZDX, stops when next_offset becomes null.
        - Custom: Stops if max_items or max_pages limits are reached.
        """
        if not self.has_next():
            return []  # No more pages to fetch

        # Update the request with the next_offset for ZDX or page for ZPA/ZIA/ZCC
        if self._service_type == "ZDX":
            self._params["offset"] = self._next_offset
        else:
            self._page += 1
            self._params["page"] = self._page

        req = {"headers": self._headers, "params": self._params}  # Include filters like search, sort, etc.

        # Fire the request for the next page
        next_response = self._request_executor.fire_request("GET", req)
        response_body = next_response.get("body", {})

        # Update the response with the new page's data
        self.build_json_response(response_body)

        # Stop if no data was returned (especially for ZIA and ZDX)
        if not self._list:
            return []

        return self._list


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
                response_body=response.get("body"),
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
