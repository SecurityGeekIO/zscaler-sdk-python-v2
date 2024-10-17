from zscaler.utils import zcc_param_map
from zscaler.api_client import APIClient
from zscaler.zcc.models.secrets_otp import OtpResponse
from zscaler.zcc.models.secrets_passwords import Passwords


class SecretsAPI(APIClient):

    def __init__(self, request_executor):
        self._request_executor = request_executor
        self._base_endpoint = "/zcc/papi/public/v1"

    def get_otp(self, device_id: str):
        """
        Returns the OTP code for the specified device id.

        Args:
            device_id (str): The unique id for the enrolled device that the OTP will be obtained for.

        Returns:
            OtpResponse: An instance of OtpResponse containing the requested OTP code for the specified device id.
        """
        payload = {"udid": device_id}
        api_url = f"{self._base_endpoint}/getOtp"

        request, error = self._request_executor.create_request("get", api_url, params=payload)
        if error:
            return None, None, error

        response, error = self._request_executor.execute(request)
        if error:
            return None, response, error

        try:
            result = OtpResponse(self.form_response_body(response.get_body()))
        except Exception as error:
            return (None, response, error)
        return (result, response, None)

    def get_passwords(self, username: str, os_type: str = "windows") -> tuple:
        """
        Return passwords for the specified username and device OS type.

        Args:
            username (str): The username that the device belongs to.
            os_type (str): The OS Type for the device, defaults to `windows`. Valid options are:

                - ios
                - android
                - windows
                - macos
                - linux

        Returns:
            Passwords: An instance of Passwords containing passwords for the specified username's device.
        """
        # Simplify the os_type argument, raise an error if the user supplies the wrong one.
        os_type = zcc_param_map["os"].get(os_type, None)
        if not os_type:
            raise ValueError("Invalid os_type specified. Check the pyZscaler documentation for valid os_type options.")

        params = {
            "username": username,
            "osType": os_type,
        }

        api_url = f"{self._base_endpoint}/getPasswords"
        request, error = self._request_executor.create_request("get", api_url, params=params)
        if error:
            return None, None, error

        response, error = self._request_executor.execute(request)
        if error:
            return None, response, error

        try:
            result = Passwords(self.form_response_body(response.get_body()))
        except Exception as error:
            return (None, response, error)
        return (result, response, None)
