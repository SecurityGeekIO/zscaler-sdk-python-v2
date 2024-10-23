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
from zscaler.zcc.zcc_service import ZCCService
from zscaler.zia.zia_service import ZIAService
from zscaler.zpa.zpa_service import ZPAService

# Configure logging
setup_logging(logger_name="zscaler-sdk-python")
logger = logging.getLogger(__name__)


# Zscaler Client Connector APIs
class Client:
    """A Zscaler client object"""

    def __init__(self, user_config: dict = {}):
        logger.debug("Initializing Client with user configuration.")
        client_config_setter = ConfigSetter()
        client_config_setter._apply_config({"client": user_config})
        self._config = client_config_setter.get_config()
        logger.debug(f"Configuration applied: {self._config}")

        # Retrieve optional customerId from config or environment
        self._customer_id = self._config["client"].get("customerId", os.getenv("ZSCALER_CUSTOMER_ID"))
        logger.debug(f"Customer ID set to: {self._customer_id}")

        # Prune unnecessary configuration fields
        self._config = client_config_setter._prune_config(self._config)
        logger.debug(f"Configuration after pruning: {self._config}")

        # Validate configuration
        ConfigValidator(self._config)
        logger.debug("Configuration validated successfully.")

        self._client_id = self._config["client"]["clientId"]
        self._client_secret = self._config["client"].get("clientSecret", None)
        self._private_key = self._config["client"].get("privateKey", None)
        self._vanity_domain = self._config["client"]["vanityDomain"]
        self._cloud = self._config["client"].get("cloud", "PRODUCTION")
        self._auth_token = None

        # Handle cache
        cache = NoOpCache()
        if self._config["client"]["cache"]["enabled"]:
            if user_config.get("cacheManager") is None:
                time_to_idle = self._config["client"]["cache"]["defaultTti"]
                time_to_live = self._config["client"]["cache"]["defaultTtl"]
                cache = ZscalerCache(time_to_live, time_to_idle)
                logger.debug(f"Using default cache with TTL: {time_to_live}, TTI: {time_to_idle}")
            else:
                cache = user_config.get("cacheManager")
                logger.debug("Using custom cache manager.")

        self._request_executor = user_config.get("requestExecutor", RequestExecutor)(
            self._config, cache, user_config.get("httpClient", None)
        )
        logger.debug("Request executor initialized.")

        # Lazy load ZIA and ZPA clients
        self._zia = None
        self._zpa = None
        self._zcc = None
        logger.debug("Client initialized successfully.")

    def authenticate(self):
        """
        Handles authentication by using either client_secret or private_key.
        """
        logger.debug("Starting authentication process.")
        oauth_client = OAuth(self._request_executor, self._config)
        self._auth_token = oauth_client._get_access_token()
        logger.debug("Authentication successful. Access token obtained.")

        # Update the default headers by setting the Authorization Bearer token
        self._request_executor._default_headers.update({"Authorization": f"Bearer {self._auth_token}"})
        logger.debug("Authorization header updated with access token.")

    @property
    def zcc(self) -> ZCCService:
        if self._zcc is None:
            self._zcc = ZCCService(self)
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
        logger.debug("Entering context manager, setting up session.")
        # Create and set up a session using 'requests' library for sync.
        self._session = requests.Session()
        self._request_executor.set_session(self._session)
        self.authenticate()  # Authenticate when entering the context
        logger.debug("Session setup and authentication complete.")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Automatically close session within context manager."""
        logger.debug("Exiting context manager, closing session.")
        self._session.close()
        logger.debug("Session closed.")

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
