from zscaler.zpa.application_segment import ApplicationSegmentAPI
from zscaler.zpa.server_groups import ServerGroupsAPI

class ZPAService:
    """ZPA Service client, exposing various ZPA APIs."""

    def __init__(self, request_executor):
        self._request_executor = request_executor
        self._app_segments = None
        self._server_groups = None

    @property
    def app_segments(self):
        """Lazy load ApplicationSegmentAPI."""
        if self._app_segments is None:
            self._app_segments = ApplicationSegmentAPI(self._request_executor)
        return self._app_segments

    @property
    def server_groups(self):
        """Lazy load ServerGroupsAPI."""
        if self._server_groups is None:
            self._server_groups = ServerGroupsAPI(self._request_executor)
        return self._server_groups
