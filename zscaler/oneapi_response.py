import json
import logging
import uuid

logger = logging.getLogger(__name__)


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
        logger.debug("Initializing ZscalerAPIResponse with service_type: %s", service_type)
        self._url = req.get("url", None)
        self._headers = req.get("headers", {})  # Headers for the request
        self._params = req.get("params", {})  # Query parameters like filtering and pagination
        self._resp_headers = res_details.headers if res_details and hasattr(res_details, "headers") else {}
        self._body = None  # First page of results
        self._type = data_type
        self._status = res_details.status_code if res_details and hasattr(res_details, "status_code") else None
        self._request_executor = request_executor  # Request Executor for future calls

        # Custom options
        self._max_items = max_items  # Max number of items to return, if provided
        self._max_pages = max_pages  # Max number of pages to return, if provided
        self._page = 1  # Initialize page for ZPA/ZIA-based pagination
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
                self._build_json_response(response_body)
            else:
                # Attempt to parse as JSON, if fails, save as plain text
                try:
                    self._build_json_response(response_body)
                except json.JSONDecodeError:
                    # Save response as plain text if not JSON
                    self._body = response_body
        else:
            # If no res_details, assume it's JSON and try to parse
            try:
                self._build_json_response(response_body)
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
            logger.debug("Page size not provided, using default: %d", default_page_size)
            return default_page_size
        validated_size = min(max(int(page_size), limits.get("min", 1)), max_page_size)
        logger.debug("Validated page size: %d", validated_size)
        return validated_size

    def get_headers(self):
        """
        Returns the response headers of the Zscaler API Response.
        """
        logger.debug("Fetching response headers")
        return self._resp_headers

    def get_body(self):
        """
        Returns the response body of the Zscaler API Response.
        """
        logger.debug("Fetching response body")
        return self._body

    def get_status(self):
        """
        Returns HTTP Status Code of response.
        """
        logger.debug("Fetching response status code: %s", self._status)
        return self._status

    def _build_json_response(self, response_body):
        """
        Converts JSON response text into Python dictionary or list depending on the service.
        Handles ZPA's totalPages/totalCount, ZIA's raw list response, and ZDX offset/limit.
        """
        logger.debug("Building JSON response")
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
            # Automatically extract the "list" and assign it to self._list
            self._list = self._body.get("list", [])
            if self._service_type == "ZPA":
                self._total_pages = int(self._body.get("totalPages", 1))  # totalPages from the API response
                self._total_count = int(self._body.get("totalCount", 0))  # totalCount from the API response

        # Track the number of items fetched in the current page
        self._items_fetched += len(self._list)
        self._pages_fetched += 1
        logger.debug("Items fetched: %d, Pages fetched: %d", self._items_fetched, self._pages_fetched)

    def get_results(self):
        """
        Return the list of results (automatically extracted from the response).
        """
        logger.debug("Fetching results list")
        return self._list

    def get_all_pages_results(self):
        """
        Fetches and returns all pages of results.
        """
        logger.debug("Starting to fetch all results")

        # Reset pagination tracking variables
        self._items_fetched = 0
        self._pages_fetched = 0
        self._page = 1
        # Start with the current list of results from the first page
        all_results = self._list.copy()
        prev_results = all_results
        self._items_fetched += len(all_results)
        self._pages_fetched += 1
        logger.debug(f"Initial results count: {len(all_results)}")
        # Continue fetching pages as long as there are more pages available
        while self._has_next():
            logger.debug("Fetching next page of results")

            # Fetch the next page of results
            next_page_results = self._next()

            # If no more data is returned, break out of the loop
            if not next_page_results:
                logger.debug("No more data returned, stopping pagination")
                break
            if prev_results == next_page_results:
                # could happen for ZIA
                logger.debug("No new data returned, stopping pagination")
                break
            # Add the results from the next page to the overall results
            all_results.extend(next_page_results)
            self._items_fetched += len(next_page_results)
            self._pages_fetched += 1
            prev_results = next_page_results
            logger.debug(f"Extended results count: {len(all_results)}")

        logger.debug(f"Total results fetched: {len(all_results)}")
        # Return the complete list of results from all pages
        return all_results

    def _has_next(self):
        """
        Determines if there are more pages to fetch.
        - For ZPA: Checks if the current page is less than totalPages.
        - For ZIA and ZCC: Continues fetching until no data is returned.
        - For ZDX: Continues fetching until next_offset becomes null.
        - Custom: Stops if max_items or max_pages limits are reached.
        """
        if self._max_items is not None and self._items_fetched >= self._max_items:
            logger.debug("Reached max items limit: %d", self._max_items)
            return False  # Stop if we've reached the max number of items
        if self._max_pages is not None and self._pages_fetched >= self._max_pages:
            logger.debug("Reached max pages limit: %d", self._max_pages)
            return False  # Stop if we've reached the max number of pages

        if self._service_type == "ZPA":
            has_next = self._page < self._total_pages
            logger.debug("Has next page for ZPA: %s", has_next)
            return has_next
        elif self._service_type == "ZDX":
            has_next = self._next_offset is not None
            logger.debug("Has next page for ZDX: %s", has_next)
            return has_next
        else:
            has_next = bool(self._list)  # For ZIA and ZCC, stop when no data is returned
            logger.debug("Has next page for ZIA/ZCC: %s", has_next)
            return has_next

    def _next(self):
        """
        Fetches the next page of results.
        - Stops for ZIA and ZCC when no data is returned.
        - For ZPA, stops when the total number of pages is reached.
        - For ZDX, stops when next_offset becomes null.
        - Custom: Stops if max_items or max_pages limits are reached.
        """
        if not self._has_next():
            logger.debug("No more pages to fetch")
            return []  # No more pages to fetch

        # Update the request with the next_offset for ZDX or page for ZPA/ZIA/ZCC
        if self._service_type == "ZDX":
            self._params["offset"] = self._next_offset
        else:
            self._page += 1
            self._params["page"] = self._page

        logger.debug("Fetching next page with params: %s", self._params)
        req = {
            "method": "GET",  # Specify the method as GET for pagination
            "url": self._url,  # Add the URL to the request dictionary
            "headers": self._headers,
            "params": self._params,
            "uuid": uuid.uuid4(),  # Generate a unique identifier for the request
        }

        # Fire the request for the next page and unpack the needed values
        _, _, response_body, error = self._request_executor.fire_request(req)

        if error:
            logger.error(f"Error fetching the next page: {error}")
            return [], error

        # Update the response with the new page's data, no need to re-parse response_body
        self._build_json_response(response_body)

        # Stop if no data was returned (especially for ZIA and ZDX)
        if not self._list:
            logger.debug("No data returned for the next page")
            # reset pagination tracking variables
            self._items_fetched = 0
            self._pages_fetched = 0
            self._page = 1
            return []

        return self._list
