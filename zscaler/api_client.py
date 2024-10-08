from pydash.strings import camel_case


class APIClient:
    """
    Base class for handling responses and converting keys between camelCase and snake_case.
    """
    def __init__(self):
        """
        Automatically set the base URL from the request executor (inherited by each API class).
        """
        # Base URL remains empty in resource classes, filled dynamically in methods
        self._base_url = ""

    @staticmethod
    def form_response_body(body: dict):
        """
        Method to verify the response body from the Zscaler API before
        passing it into the constructor.
        Args:
            body (dict): Zscaler API response body
        """
        result = {}
        for key, val in body.items():
            if val is None:
                continue
            if not isinstance(val, dict):
                result[camel_case(key)] = val
            else:
                result[camel_case(key)] = APIClient.form_response_body(val)
        return result

    @staticmethod
    def format_request_body(body: dict):
        """
        Method to format the request body from snake_case to camelCase.
        Args:
            body (dict): API request body
        """
        result = {}
        for key, val in body.items():
            if val is None:
                continue
            if not isinstance(val, dict):
                result[camel_case(key)] = val
            else:
                result[camel_case(key)] = APIClient.format_request_body(val)
        return result
