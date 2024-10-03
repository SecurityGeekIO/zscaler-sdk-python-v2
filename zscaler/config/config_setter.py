import os
import yaml
from zscaler.constants import _GLOBAL_YAML_PATH, _LOCAL_YAML_PATH
from flatdict import FlatDict


class ConfigSetter:
    """
    This class sets up the configuration for the Zscaler Client
    """

    _ZSCALER = "ZSCALER"
    _DEFAULT_CONFIG = {
        "client": {
            "clientId": "",
            "clientSecret": "",
            "privateKey": "",
            "vanityDomain": "",
            "cloud": "",
            "userAgent": "",
            "customerId": "",
            "microtenantId": "",
            "sandboxToken": "",
            "connectionTimeout": 30,
            "requestTimeout": 0,
            "cache": {"enabled": False, "defaultTtl": 300, "defaultTti": 300},
            "logging": {"enabled": False, "verbose": False},  # Default logging is disabled  # Default verbosity
            "proxy": {"port": "", "host": "", "username": "", "password": ""},
            "rateLimit": {"maxRetries": 2, "maxBackoff": 0},
        },
        "testing": {"disableHttpsCheck": False},
    }

    def __init__(self):
        """
        Constructor for Configuration Setter class. Sets default config
        and checks for configuration settings to update config.
        """
        # Create configuration using default config
        self._config = ConfigSetter._DEFAULT_CONFIG
        # Update configuration
        self._update_config()
        # Setup logging based on config
        self._setup_logging()

    def get_config(self):
        """
        Return Zscaler client configuration

        Returns:
            dict -- Dictionary containing the client configuration
        """
        return self._config

    def _prune_config(self, config):
        """
        This method cleans up the configuration object by removing fields
        with no value
        """
        flat_current_config = FlatDict(config, delimiter="_")
        for key in flat_current_config.keys():
            if flat_current_config.get(key) == "":
                del flat_current_config[key]

        return flat_current_config.as_dict()

    def _update_config(self):
        """
        Updates the configuration of the Zscaler Client by:
        1. Applying default values
        2. Checking for a global Zscaler config YAML
        3. Checking for a local Zscaler config YAML
        4. Checking for corresponding ENV variables
        """
        self._apply_default_values()

        if os.path.exists(_GLOBAL_YAML_PATH):
            self._apply_yaml_config(_GLOBAL_YAML_PATH)

        if os.path.exists(_LOCAL_YAML_PATH):
            self._apply_yaml_config(_LOCAL_YAML_PATH)

        self._apply_env_config()

    def _setup_logging(self):
        """
        Setup logging based on configuration.
        """
        logging_enabled = self._config["client"]["logging"].get("enabled", False)
        verbose_logging = self._config["client"]["logging"].get("verbose", False)

        if logging_enabled:
            os.environ["ZSCALER_SDK_LOG"] = "true"
            os.environ["ZSCALER_SDK_VERBOSE"] = "true" if verbose_logging else "false"
        else:
            os.environ["ZSCALER_SDK_LOG"] = "false"

    def _apply_default_values(self):
        """Apply default values to default client configuration"""
        pass

    def _apply_yaml_config(self, path: str):
        """This method applies a YAML configuration to the Zscaler Client Config"""
        config = {}
        with open(path, "r") as file:
            config = yaml.load(file, Loader=yaml.SafeLoader)
        self._apply_config(config.get("zscaler", {}))

    def _apply_env_config(self):
        """
        This method checks the environment variables for any Zscaler
        configuration parameters and applies them if available.
        """
        flattened_config = FlatDict(self._config, delimiter="_")
        flattened_keys = flattened_config.keys()

        updated_config = FlatDict({}, delimiter="_")

        for key in flattened_keys:
            env_key = ConfigSetter._ZSCALER + "_" + key.upper()
            env_value = os.environ.get(env_key, None)

            if env_value is not None:
                updated_config[key] = env_value
        self._apply_config(updated_config.as_dict())

    def _apply_config(self, new_config: dict):
        """Apply a config dictionary to the current config, overwriting values"""
        flat_current_client = FlatDict(self._config["client"], delimiter="_")
        flat_current_testing = FlatDict(self._config["testing"], delimiter="_")

        flat_new_client = FlatDict(new_config.get("client", {}), delimiter="_")
        flat_new_testing = FlatDict(new_config.get("testing", {}), delimiter="_")

        flat_current_client.update(flat_new_client)
        flat_current_testing.update(flat_new_testing)

        self._config = {"client": flat_current_client.as_dict(), "testing": flat_current_testing.as_dict()}
