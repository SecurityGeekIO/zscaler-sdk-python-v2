from zscaler.v1_legacy.zpa_legacy_request_executor import ZPALegacyRequestExecutor
from zscaler.v1_legacy.zia_legacy_request_executor import ZIALegacyRequestExecutor
from zscaler.request_executor import RequestExecutor
from zscaler.zpa_legacy_client import ZPAClientHelper
from zscaler.zia_legacy_client import ZIAClientHelper
from zscaler.zpa.zpa_service import ZPAService


class ClientFactory:
    @staticmethod
    def create_client(client_type: str, config: dict, service: str = "zpa"):
        """
        Factory to create the appropriate Zscaler client.

        Args:
            client_type (str): "legacy" or "oneapi"
            config (dict): Client configuration
            service (str): "zpa" or "zia"

        Returns:
            ZPAClientHelper, ZPAService, ZIAClientHelper, or appropriate object.
        """
        if client_type == "legacy":
            if service == "zpa":
                request_executor = ZPALegacyRequestExecutor(config, None)
                return ZPAClientHelper(request_executor)
            elif service == "zia":
                request_executor = ZIALegacyRequestExecutor(config, None)
                return ZIAClientHelper(request_executor)
            else:
                raise ValueError(f"Unsupported legacy service: {service}")
        elif client_type == "oneapi":
            if service == "zpa":
                request_executor = RequestExecutor(config, None)
                return ZPAService(request_executor)
            else:
                raise ValueError(f"Unsupported OneAPI service: {service}")
        else:
            raise ValueError(f"Unknown client type: {client_type}")
