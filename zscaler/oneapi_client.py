import requests
import logging
import os

from zscaler.config.config_setter import ConfigSetter
from zscaler.config.config_validator import ConfigValidator
from zscaler.request_executor import RequestExecutor
from zscaler.cache.no_op_cache import NoOpCache
from zscaler.cache.zscaler_cache import ZscalerCache
from zscaler.oneapi_oauth_client import OAuth
from zscaler.logger import setup_logging
from zscaler.zia.zia_service import ZIAService
from zscaler.zpa.zpa_service import ZPAService


# Zscaler Client Connector APIs
class Client:
    """A Zscaler client object"""

    def __init__(self, user_config: dict = {}):
        client_config_setter = ConfigSetter()
        client_config_setter._apply_config({"client": user_config})
        self._config = client_config_setter.get_config()

        # Retrieve optional customerId from config or environment
        self._customer_id = self._config["client"].get("customerId", os.getenv("ZSCALER_CUSTOMER_ID"))

        # Prune unnecessary configuration fields
        self._config = client_config_setter._prune_config(self._config)

        # Validate configuration
        ConfigValidator(self._config)

        self._client_id = self._config["client"]["clientId"]
        self._client_secret = self._config["client"].get("clientSecret", None)
        self._private_key = self._config["client"].get("privateKey", None)
        self._vanity_domain = self._config["client"]["vanityDomain"]
        self._cloud = self._config["client"].get("cloud", "PRODUCTION")
        self._auth_token = None
        self._api_version = self._config["client"].get("api_version", "v1")

        # Handle cache
        cache = NoOpCache()
        if self._config["client"]["cache"]["enabled"]:
            if user_config.get("cacheManager") is None:
                time_to_idle = self._config["client"]["cache"]["defaultTti"]
                time_to_live = self._config["client"]["cache"]["defaultTtl"]
                cache = ZscalerCache(time_to_live, time_to_idle)
            else:
                cache = user_config.get("cacheManager")

        self._request_executor = user_config.get("requestExecutor", RequestExecutor)(
            self._config, cache, user_config.get("httpClient", None)
        )

        # Setup logging
        setup_logging()

        if self._config["client"]["logging"]["enabled"]:
            logger = logging.getLogger("zscaler-sdk-python")
            logger.disabled = False

        # Initialize the request executor
        self._request_executor = user_config.get("requestExecutor", RequestExecutor)(
            self._config, cache, user_config.get("httpClient", None)
        )

        # Lazy load ZIA and ZPA clients
        self._zia = None
        self._zpa = None

        # super().__init__()

    def authenticate(self):
        """
        Handles authentication by using either client_secret or private_key.
        """
        oauth_client = OAuth(self._request_executor, self._config)
        self._auth_token = oauth_client._get_access_token()

        # Update the default headers by setting the Authorization Bearer token
        self._request_executor._default_headers.update({"Authorization": f"Bearer {self._auth_token}"})
        print(f"Authentication complete. Token set: {self._auth_token}")

    @property
    def zcc(self) -> ZPAService:
        if self._zcc is None:
            self._zcc = ZPAService(self)
        return self._zcc

    @property
    def zia(self) -> ZIAService:
        if self._zia is None:
            self._zia = ZIAService(self)
        return self._zia

    @property
    def zpa(self) -> ZPAService:
        if self._zpa is None:
            self._zpa = ZPAService(self._request_executor, self._config)
        return self._zpa


    def __enter__(self):
        """
        Automatically create and set session within context manager.
        """
        # Create and set up a session using 'requests' library for sync.
        self._session = requests.Session()
        self._request_executor.set_session(self._session)
        self.authenticate()  # Authenticate when entering the context
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Automatically close session within context manager."""
        self._session.close()

    """
    Getters
    """

    def get_config(self):
        return self._config

    def get_request_executor(self):
        return self._request_executor

    """
    Misc
    """

    def set_custom_headers(self, headers):
        self._request_executor.set_custom_headers(headers)

    def clear_custom_headers(self):
        self._request_executor.clear_custom_headers()

    def get_custom_headers(self):
        return self._request_executor.get_custom_headers()

    def get_default_headers(self):
        return self._request_executor.get_default_headers()
