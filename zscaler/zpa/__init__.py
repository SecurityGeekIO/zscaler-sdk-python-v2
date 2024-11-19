import requests
from zscaler.constants import ZPA_BASE_URLS, DEV_AUTH_URL

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

class ZPALegacyRequestExecutor:
    def __init__(self, config, cache, http_client=None):
        super().__init__(config, cache, http_client)

        cloud = config["client"].get("cloud", "PRODUCTION").upper()
        if cloud not in ZPA_BASE_URLS:
            raise ValueError(
                f"Invalid cloud specified: {cloud}. Valid options are: {', '.join(ZPA_BASE_URLS.keys())}"
            )
        self._base_url = ZPA_BASE_URLS[cloud]
        self._legacy_login_url = f"{DEV_AUTH_URL if cloud == 'DEV' else f'{self._base_url}/signin'}"

    def _get_access_token(self):
        """
        Override the access token retrieval to handle legacy login.
        """
        if not self._access_token:
            params = {
                "client_id": self._config["client"]["clientId"],
                "client_secret": self._config["client"]["clientSecret"],
            }
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            }
            response = requests.post(
                self._legacy_login_url, data=params, headers=headers, timeout=self._request_timeout
            )
            if response.status_code >= 300:
                raise Exception(f"Failed to authenticate with legacy API: {response.text}")
            self._access_token = response.json().get("access_token")
        return self._access_token

    def get_base_url(self, endpoint: str) -> str:
        """
        Override to ensure correct base URL is used for the legacy client.
        """
        return self._base_url
