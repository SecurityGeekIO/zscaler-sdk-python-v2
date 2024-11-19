import requests
from request_executor import RequestExecutor

ZPA_BASE_URLS = {
    "PRODUCTION": "https://config.private.zscaler.com",
    "ZPATWO": "https://config.zpatwo.net",
    "BETA": "https://config.zpabeta.net",
    "GOV": "https://config.zpagov.net",
    "GOVUS": "https://config.zpagov.us",
    "PREVIEW": "https://config.zpapreview.net",
    "QA": "https://config.qa.zpath.net",
    "QA2": "https://pdx2-zpa-config.qa2.zpath.net",
    "DEV": "https://public-api.dev.zpath.net",
}

DEV_AUTH_URL = "https://authn1.dev.zpath.net/authn/v1/oauth/token"


class ZPALegacyRequestExecutor(RequestExecutor):
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
