import os
import re
from zscaler.zpa import ZPAClientHelper
import jwt
from datetime import datetime, timedelta

PYTEST_MOCK_CLIENT = "pytest_mock_client"


class MockZPAClient(ZPAClientHelper):
    def __init__(self, fs):
        if PYTEST_MOCK_CLIENT in os.environ:
            fs.pause()
            super().__init__()
            fs.resume()
        else:
            super().__init__(
                client_id="client",
                client_secret="client_secret",
                customer_id="216196257331281920",
                cloud="PRODUCTION",
                timeout=240,
                cache=None,
                fail_safe=False,
            )


def mock_token():
    # Define the payload
    payload = {
        "exp": datetime.utcnow() + timedelta(days=1),  # Set expiration to tomorrow
    }

    # Define the secret key (change this to your own secret key)
    secret_key = "your_secret_key_here"

    # Generate the JWT token
    return jwt.encode(payload, secret_key, algorithm="HS256")


def modify_request(request):
    # Modify the request to include a dummy string for authorization header
    request.headers["Authorization"] = "Bearer dummy_token"
    if "/signin" in request.url and request.body:
        # Convert request body from bytes to string
        body_str = request.body.decode("utf-8")

        # Define pattern and replacement strings
        pattern = r"client_id=[^&]+&client_secret=[^&]+"
        repl = "client_id=dummy_client_id&client_secret=dummy_client_secret"

        # Apply regular expression substitution
        modified_body_str = re.sub(pattern, repl, body_str)

        # Convert modified body back to bytes
        request.body = modified_body_str.encode("utf-8")
    return request


def modify_response(response):
    # Modify the response to include dummy strings for authorization header and cookies
    response_body_string = response["body"]["string"]

    # Check if the body is already bytes-like object
    if isinstance(response_body_string, bytes):
        # Encode the string to bytes
        response_body_string = response_body_string.decode("utf-8")

    if re.search(r'"access_token"\s*:\s*"[^"]+"', response_body_string):
        token = '"' + mock_token() + '"'
        response_body_string = re.sub(
            rb'"access_token"\s*:\s*"[^"]+"',  # Use rb prefix to denote bytes regex pattern
            lambda match: b'"access_token": ' + token.encode("utf-8"),  # Encode the replacement string to bytes
            response_body_string.encode("utf-8"),  # Encode the whole string to bytes before applying regex
        )

        # Decode the bytes back to string
        response["body"]["string"] = response_body_string
    return response
