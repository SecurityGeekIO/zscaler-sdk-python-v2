from zscaler.api_client import APIClient
import json

from zscaler.zcc.models.manage_pass import ManagePassResponseContract


class ManagePassAPI(APIClient):

    def __init__(self, request_executor):
        self._request_executor = request_executor
        self._base_endpoint = "/zcc/papi/public/v1"

    def update_manage_pass(self, manage_pass):
        """
        Updates the manage pass settings.

        Args:
            manage_pass (dict): A dictionary containing manage pass settings.

        Returns:
            dict: A dictionary containing the response from the API.
        """
        api_url = f"{self._base_endpoint}/managePass"
        # Ensure app_segment is a dictionary
        if isinstance(manage_pass, dict):
            body = manage_pass
        else:
            body = manage_pass.as_dict()

        request, error = self._request_executor.create_request("post", api_url, body=body)
        if error:
            return None, None, error

        response, error = self._request_executor.execute(request)
        if error:
            return None, response, error

        try:
            result = ManagePassResponseContract(self.form_response_body(response.get_body()))
        except Exception as error:
            return (None, response, error)
        return (result, response, None)
