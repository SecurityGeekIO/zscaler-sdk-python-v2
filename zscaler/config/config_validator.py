import logging
from zscaler.error_messages import (
    ERROR_MESSAGE_CLIENT_ID_MISSING,
    ERROR_MESSAGE_CLIENT_SECRET_MISSING,
    ERROR_MESSAGE_VANITY_DOMAIN_MISSING,
    ERROR_MESSAGE_CLOUD_MISSING,
    ERROR_MESSAGE_ZPA_CUSTOMER_ID,
    ERROR_MESSAGE_ZPA_MICROTENANT_ID,
    ERROR_MESSAGE_PROXY_MISSING_HOST,
    ERROR_MESSAGE_PROXY_MISSING_AUTH,
    ERROR_MESSAGE_PROXY_INVALID_PORT,
)

logger = logging.getLogger(__name__)


class ConfigValidator:
    """
    This class performs validation checks on the Zscaler Client configuration.
    """

    def __init__(self, config):
        self._config = config
        self.validate_config()

    def validate_config(self):
        """
        Validates the client configuration. Throws a ValueError if invalid.

        Raises:
            ValueError: A configuration provided needs to be corrected.
        """
        errors = []
        client = self._config.get("client", {})
        client_type = self._config.get("clientType", "").lower()

        # Route validation based on client type
        if client_type == "legacy":
            legacy_service = client.get("legacyService", "").lower()
            if legacy_service == "zia":
                logger.info("Validating ZIA Legacy client configuration.")
                errors += self._validate_zia_legacy_config(client)
            elif legacy_service == "zpa":
                logger.info("Validating ZPA Legacy client configuration.")
                errors += self._validate_zpa_legacy_config(client)
            else:
                errors.append("Invalid or missing 'legacyService' for Legacy client.")
        elif client_type == "oneapi":
            logger.info("Validating OneAPI client configuration.")
            errors += self._validate_oneapi_config(client)
        else:
            errors.append(f"Invalid clientType '{client_type}'. Must be 'oneapi' or 'legacy'.")

        # Validate proxy settings (if provided)
        if "proxy" in client:
            proxy_errors = self._validate_proxy_settings(client["proxy"])
            errors += proxy_errors

        # Raise exception if errors exist
        if errors:
            newline = "\n"
            logger.error(f"Configuration validation failed with errors: {errors}")
            raise ValueError(
                f"{newline}Errors:{newline + newline.join(errors) + 2*newline}Please check your configuration."
            )

    def _validate_zia_legacy_config(self, client_config):
        """
        Validates configuration for ZIA Legacy API clients.
        """
        errors = []
        required_fields = ["username", "password", "api_key", "cloud"]

        for field in required_fields:
            if not client_config.get(field):
                errors.append(f"Missing required field '{field}' for ZIA Legacy client.")

        return errors

    def _validate_zpa_legacy_config(self, client_config):
        """
        Validates configuration for ZPA Legacy API clients.
        """
        errors = []
        required_fields = ["clientId", "clientSecret", "customerId"]

        for field in required_fields:
            if not client_config.get(field):
                errors.append(f"Missing required field '{field}' for ZPA Legacy client.")

        return errors

    def _validate_oneapi_config(self, client_config):
        """
        Validates configuration for OneAPI clients.
        """
        errors = []
        required_fields = ["clientId", "vanityDomain"]

        for field in required_fields:
            if not client_config.get(field):
                errors.append(f"Missing required field '{field}' for OneAPI client.")

        # Validate authentication: client_secret or private_key
        client_secret = client_config.get("clientSecret")
        private_key = client_config.get("privateKey")

        if not client_secret and not private_key:
            errors.append("OneAPI client requires either 'clientSecret' or 'privateKey' for authentication.")
            logger.warning("Both client secret and private key are missing.")

        return errors


    def _validate_client_id(self, client_id):
        client_id_errors = []

        # Ensure client ID is provided
        client_id = client_id.strip().lower()
        if not client_id:
            client_id_errors.append(ERROR_MESSAGE_CLIENT_ID_MISSING)
            logging.warning("Client ID is missing.")
        # Detect if default {clientId} placeholder is used
        if "{clientId}".lower() in client_id:
            client_id_errors.append("Client ID contains a placeholder value {clientId}.")
            logging.warning("Client ID contains a placeholder value {clientId}.")

        return client_id_errors

    def _validate_vanity_domain(self, vanity_domain: str):
        vanity_domain_errors = []

        # Log the vanity domain to debug
        # logging.debug(f"Validating vanity domain: {vanity_domain}")

        # Check if vanity domain is None or empty
        if vanity_domain is None:
            vanity_domain_errors.append(ERROR_MESSAGE_VANITY_DOMAIN_MISSING)
            logging.warning("Vanity domain is missing.")
            return vanity_domain_errors

        # Remove whitespaces and lowercase domain for comparisons
        vanity_domain = vanity_domain.strip().lower()

        # Vanity domain is required
        if not vanity_domain:
            vanity_domain_errors.append(ERROR_MESSAGE_VANITY_DOMAIN_MISSING)
            logging.warning("Vanity domain is empty after stripping.")

        # Log result after validation
        # logging.debug(f"Vanity domain after validation: {vanity_domain}")

        return vanity_domain_errors

    def _validate_zpa_customer_id(self, zpa_customer_id: str):
        zpa_errors = []

        # Check if ZPA customer ID is valid (non-empty)
        if not zpa_customer_id:
            zpa_errors.append(ERROR_MESSAGE_ZPA_CUSTOMER_ID)
            logging.warning("ZPA customer ID is missing.")

        return zpa_errors

    def _validate_zpa_microtenant_id(self, zpa_microtenant_id: str):
        zpa_errors = []

        # Check if ZPA microtenant ID is valid (non-empty)
        if not zpa_microtenant_id:
            zpa_errors.append(ERROR_MESSAGE_ZPA_MICROTENANT_ID)
            logging.warning("ZPA microtenant ID is missing.")

        return zpa_errors

    def _validate_cloud(self, cloud: str):
        cloud_errors = []

        # Validate cloud field (optional)
        if cloud and not cloud.strip():
            cloud_errors.append(ERROR_MESSAGE_CLOUD_MISSING)
            logging.warning("Cloud is provided but invalid.")

        return cloud_errors

    def _validate_proxy_settings(self, proxy):
        proxy_errors = []

        # Check if host is provided
        if "host" not in proxy:
            proxy_errors.append(ERROR_MESSAGE_PROXY_MISSING_HOST)
            logging.warning("Proxy host is missing.")

        # Check for username/password if one is provided
        if ("username" in proxy and "password" not in proxy) or ("username" not in proxy and "password" in proxy):
            proxy_errors.append(ERROR_MESSAGE_PROXY_MISSING_AUTH)
            logging.warning("Proxy authentication details are incomplete.")

        # Validate port number
        if "port" in proxy:
            try:
                port_number = int(proxy["port"])
                if not 1 <= port_number <= 65535:
                    raise ValueError
            except (TypeError, ValueError):
                proxy_errors.append(ERROR_MESSAGE_PROXY_INVALID_PORT)
                logging.warning("Proxy port is invalid.")

        return proxy_errors
    
