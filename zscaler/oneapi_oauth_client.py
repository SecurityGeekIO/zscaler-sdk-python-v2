import requests
import jwt
import time
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from zscaler.user_agent import UserAgent

class OAuth:
    """
    This class contains the OAuth actions for the Zscaler Client.
    """

    def __init__(self, request_executor, config):
        self._request_executor = request_executor
        self._config = config
        self._access_token = None

    def authenticate(self):
        """
        Main authentication function. Determines which authentication
        method to use (Client Secret or JWT Private Key) and retrieves the
        OAuth access token.

        Returns:
            str: OAuth access token.
        """
        client_id = self._config["client"]["clientId"]
        client_secret = self._config["client"].get("clientSecret", "")
        private_key = self._config["client"].get("privateKey", "")

        if not client_id or (not client_secret and not private_key):
            raise ValueError("No valid client credentials provided")

        # Determine whether to authenticate with client secret or JWT
        if private_key:
            self._access_token = self._authenticate_with_private_key(client_id, private_key)
        else:
            self._access_token = self._authenticate_with_client_secret(client_id, client_secret)

        # Print token for debugging (optional)
        print(f"Access Token: {self._access_token}")

        return self._access_token

    def _authenticate_with_client_secret(self, client_id, client_secret):
        """
        Authenticate using client ID and client secret.

        Args:
            client_id (str): Client ID for authentication.
            client_secret (str): Client secret for authentication.

        Returns:
            str: OAuth access token.
        """
        vanity_domain = self._config["client"]["vanityDomain"]
        cloud = self._config["client"].get("cloud", "PRODUCTION").lower()
        auth_url = self._get_auth_url(vanity_domain, cloud)

        # Log the URL for debugging
        print(f"Auth URL: {auth_url}")

        # Prepare form data (like in the Go SDK)
        form_data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "audience": "https://api.zscaler.com",
        }

        # Log the form data for debugging
        print(f"Form Data: {form_data}")

        user_agent = UserAgent().get_user_agent_string()
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": user_agent, 
        }

        # Log the headers for debugging
        print(f"Headers: {headers}")

        # Synchronous HTTP request (with form data in the body)
        response = requests.post(auth_url, data=form_data, headers=headers)

        if response.status_code >= 300:
            print(f"Error Response: {response.text}")  # Log the full error response
            raise Exception(f"Error authenticating: {response.status_code}, {response.text}")

        token_data = response.json()
        return token_data["access_token"]

    def _authenticate_with_private_key(self, client_id, private_key_path):
        """
        Authenticate using client ID and JWT private key.

        Args:
            client_id (str): Client ID for authentication.
            private_key_path (str): Path to the private key file.

        Returns:
            str: OAuth access token.
        """
        vanity_domain = self._config["client"]["vanityDomain"]
        cloud = self._config["client"].get("cloud", "PRODUCTION").lower()
        auth_url = self._get_auth_url(vanity_domain, cloud)

        # Log the URL for debugging
        print(f"Auth URL: {auth_url}")

        # Read and load the private key
        with open(private_key_path, "rb") as key_file:
            private_key = serialization.load_pem_private_key(key_file.read(), password=None, backend=default_backend())

        # Create JWT for client assertion
        now = int(time.time())
        payload = {
            "iss": client_id,
            "sub": client_id,
            "aud": "https://api.zscaler.com",
            "exp": now + 600,  # 10 minutes expiration
        }

        # Generate the assertion using RS256 algorithm
        assertion = jwt.encode(payload, private_key, algorithm="RS256")

        # Log the assertion for debugging
        print(f"JWT Assertion: {assertion}")

        # Prepare form data
        form_data = {
            "grant_type": "client_credentials",
            "client_assertion": assertion,
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "audience": "https://api.zscaler.com",
        }

        user_agent = UserAgent().get_user_agent_string()
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": user_agent,
        }

        # Log form data and headers for debugging
        print(f"Form Data: {form_data}")
        print(f"Headers: {headers}")

        # Synchronous HTTP request
        response = requests.post(auth_url, data=form_data, headers=headers)

        if response.status_code >= 300:
            print(f"Error Response: {response.text}")  # Log the full error response
            raise Exception(f"Error authenticating: {response.status_code}, {response.text}")

        token_data = response.json()
        return token_data["access_token"]

    def _get_access_token(self):
        """
        Retrieves or generates the OAuth access token for the Zscaler OneAPI Client
        
        Returns:
            str, Exception: Tuple of the access token, error that was raised
            (if any)
        """
        if not self._access_token:
            self._access_token = self.authenticate()
        return self._access_token
    
    def _get_auth_url(self, vanity_domain, cloud):
        """
        Determines the OAuth2 provider URL based on the vanity domain and cloud.

        Args:
            vanity_domain (str): Vanity domain for the authentication URL.
            cloud (str): Cloud environment (e.g., "production", "stage").

        Returns:
            str: The fully constructed authentication URL.
        """
        if cloud == "production":
            return f"https://{vanity_domain}.zslogin.net/oauth2/v1/token"
        else:
            return f"https://{vanity_domain}.zslogin{cloud}.net/oauth2/v1/token"

    def clear_access_token(self):
        """
        Clear the current OAuth access token.
        """
        self._access_token = None
        self._request_executor._default_headers.pop("Authorization", None)
