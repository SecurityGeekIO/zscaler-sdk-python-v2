class ZIAClientHelper:
    """
    Helper class for interacting with the ZIA Legacy API.
    """

    def __init__(self, request_executor):
        self.request_executor = request_executor

    def _prepare_headers(self):
        """
        Prepares headers with the JSESSIONID for authentication.
        """
        session_id = self.request_executor._get_session_id()
        return {
            "Cookie": f"JSESSIONID={session_id}",
            "Content-Type": "application/json",
        }

    def get(self, path, params=None):
        """
        Executes a GET request to the ZIA API.
        """
        headers = self._prepare_headers()
        request, _ = self.request_executor.create_request("GET", path, params=params, headers=headers)
        response, error = self.request_executor.execute(request)
        if error:
            raise error
        return response
