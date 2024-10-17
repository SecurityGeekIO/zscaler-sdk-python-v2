from zscaler.zcc.devices import DevicesAPI
from zscaler.zcc.secrets import SecretsAPI


class ZCCService:
    """ZCC Service client, exposing various ZCC APIs."""

    def __init__(self, request_executor):
        self._request_executor = request_executor

    @property
    def devices(self):
        """
        The interface object for the :ref:`ZCC devices interface <zcc-devices>`.

        """
        return DevicesAPI(self._request_executor)

    @property
    def secrets(self):
        """
        The interface object for the :ref:`ZCC secrets interface <zcc-secrets>`.

        """
        return SecretsAPI(self._request_executor)
