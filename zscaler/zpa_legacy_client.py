class ZPAClientHelper:
    def __init__(self, request_executor):
        self.request_executor = request_executor

    def _prepare_headers(self):
        """
        Prepares headers with the access token.
        """
        access_token = self.request_executor._get_access_token()
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    def get(self, path, params=None, api_version=None):
        headers = self._prepare_headers()
        request, _ = self.request_executor.create_request(
            "GET", path, params=params, api_version=api_version, headers=headers
        )
        response, error = self.request_executor.execute(request)
        if error:
            raise error
        return response
