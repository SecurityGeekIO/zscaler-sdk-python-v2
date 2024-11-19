import os
import re
import time
import requests

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
        from zscaler.request_executor import RequestExecutor  # Lazy import here
        request, _ = self.request_executor.create_request("GET", path, params=params, headers=headers)
        response, error = self.request_executor.execute(request)
        if error:
            raise error
        return response


class ZIALegacyRequestExecutor:
    """
    Legacy Request Executor for ZIA API.
    """

    def __init__(self, config, cache, http_client=None):
        """
        Initializes the ZIA Legacy Request Executor.

        Args:
            config (dict): Configuration dictionary containing client details.
            cache (object): Optional cache object.
            http_client (object): Optional custom HTTP client.
        """
        # Delay import of RequestExecutor to avoid circular dependency
        from zscaler.request_executor import RequestExecutor
        self._executor = RequestExecutor(config, cache, http_client)

        self._username = config["client"].get("username")
        self._password = config["client"].get("password")
        self._api_key = config["client"].get("api_key")
        self._cloud = config["client"].get("cloud") or os.getenv("ZIA_CLOUD", "zscaler").lower()

        if not self._username or not self._password or not self._api_key:
            raise ValueError("Missing required fields: 'username', 'password', and 'api_key' are mandatory.")

        # Construct the base URL dynamically
        self._base_url = f"https://zsapi.{self._cloud}.net/api/v1"
        self._login_url = f"{self._base_url}/authenticatedSession"
        self._session_id = None

    def _get_session_id(self):
        """
        Retrieves a session ID for the ZIA legacy client.
        """
        if not self._session_id:
            api_key_chars = list(self._api_key)
            api_obf = self._obfuscate_api_key(api_key_chars)

            payload = {
                "apiKey": api_obf["key"],
                "username": self._username,
                "password": self._password,
                "timestamp": api_obf["timestamp"],
            }
            response = requests.post(
                self._login_url, json=payload, headers={"Content-Type": "application/json"}, timeout=240
            )

            if response.status_code >= 300:
                raise Exception(f"Failed to authenticate with ZIA legacy API: {response.text}")

            self._session_id = self._extract_jsession_id(response.headers)
        return self._session_id

    def _obfuscate_api_key(self, api_key_chars):
        """
        Obfuscates the API key for ZIA legacy login.
        """
        timestamp = int(time.time() * 1000)
        obfuscated_key = [
            chr(ord(char) ^ (timestamp >> (8 * (i % 4)) & 255)) for i, char in enumerate(api_key_chars)
        ]
        return {"key": "".join(obfuscated_key), "timestamp": timestamp}

    def _extract_jsession_id(self, headers):
        """
        Extracts the JSESSIONID from the response headers.
        """
        session_id_str = headers.get("Set-Cookie", "")
        if not session_id_str:
            raise ValueError("No Set-Cookie header received")

        match = re.search(r"JSESSIONID=(.*?);", session_id_str)
        if not match:
            raise ValueError("Couldn't find JSESSIONID in header value")
        return match.group(1)

    def get_base_url(self, endpoint: str) -> str:
        """
        Overrides the base URL logic for ZIA legacy client.
        """
        return self._base_url
