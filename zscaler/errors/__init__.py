import json
class Error:
    """
    Base Error Class
    """

    def __init__(self):
        self.message = ""

    def __repr__(self):
        return str({"message": self.message})


class HTTPError(Error):
    def __init__(self, url, response, response_body):
        self.status = response.status_code
        self.url = url
        self.message = f"HTTP {self.status} {response_body}"


class ZscalerAPIError(Error):
    def __init__(self, url, response, response_body):
        self.status = response.status_code
        self.url = url
        self.response_body = json.dumps(response_body)
        self.message = f"ZSCALER HTTP {url} {self.status} {self.response_body}"


class ZscalerBaseException(Exception):
    def __init__(self, url, response, response_body):
        self.status = response.status_code
        self.url = url
        self.response_body = json.dumps(response_body)
        self.message = f"ZSCALER HTTP {url} {self.status} {self.response_body}"

    def __repr__(self):
        return str({"message": self.message})
    def __str__(self):
        return self.message


class HTTPException(ZscalerBaseException):
    pass


class ZscalerAPIException(ZscalerBaseException):
    pass
