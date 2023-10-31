# -*- coding: utf-8 -*-

# Copyright (c) 2023, Zscaler Inc.
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.


import base64
import json
import logging
import re
import time

from box import Box, BoxList
from restfly import APIIterator

logger = logging.getLogger("zscaler-sdk-python")


def snake_to_camel(name: str):
    """Converts Python Snake Case to Zscaler's lower camelCase."""
    if "_" not in name:
        return name
    # Edge-cases where camelCase is breaking
    edge_cases = {
        "routable_ip": "routableIP",
        "is_name_l10n_tag": "isNameL10nTag",
        "name_l10n_tag": "nameL10nTag",
        "surrogate_ip": "surrogateIP",
        "surrogate_ip_enforced_for_known_browsers": "surrogateIPEnforcedForKnownBrowsers",
    }
    return edge_cases.get(name, name[0].lower() + name.title()[1:].replace("_", ""))


def recursive_snake_to_camel(data):
    """Recursively convert dictionary keys from snake_case to camelCase."""
    if isinstance(data, dict):
        return {snake_to_camel(key): recursive_snake_to_camel(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [recursive_snake_to_camel(item) for item in data]
    else:
        return data


def chunker(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


# Recursive function to convert all keys and nested keys from snake case
# to camel case.
def convert_keys(data):
    if isinstance(data, (list, BoxList)):
        return [convert_keys(inner_dict) for inner_dict in data]
    elif isinstance(data, (dict, Box)):
        new_dict = {}
        for k in data.keys():
            v = data[k]
            new_key = snake_to_camel(k)
            new_dict[new_key] = convert_keys(v) if isinstance(v, (dict, list)) else v
        return new_dict
    else:
        return data


def keys_exists(element: dict, *keys):
    """
    Check if *keys (nested) exists in `element` (dict).
    """
    if not isinstance(element, dict):
        raise AttributeError("keys_exists() expects dict as first argument.")
    if not keys:
        raise AttributeError("keys_exists() expects at least two arguments, one given.")

    _element = element
    for key in keys:
        try:
            _element = _element[key]
        except KeyError:
            return False
    return True


# Takes a tuple if id_groups, kwargs and the payload dict; reformat for API call
def add_id_groups(id_groups: list, kwargs: dict, payload: dict):
    for entry in id_groups:
        if kwargs.get(entry[0]):
            payload[entry[1]] = [{"id": param_id} for param_id in kwargs.pop(entry[0])]
    return


def transform_clientless_apps(clientless_app_ids):
    transformed_apps = []
    for app in clientless_app_ids:
        # Transform each attribute in app as needed by your API
        transformed_apps.append(
            {
                "name": app["name"],
                "applicationProtocol": app["application_protocol"],
                "applicationPort": app["application_port"],
                "certificateId": app["certificate_id"],
                "trustUntrustedCert": app["trust_untrusted_cert"],
                "enabled": app["enabled"],
                "domain": app["domain"],
            }
        )
    return transformed_apps


def format_clientless_apps(clientless_apps):
    # Implement this function to format clientless_apps as needed for the update request
    # This is just a placeholder example
    formatted_apps = []
    for app in clientless_apps:
        formatted_app = {
            "id": app["id"],  # use the correct key
            # Add other necessary attributes and format them as needed
        }
        formatted_apps.append(formatted_app)
    return formatted_apps


def obfuscate_api_key(seed: list):
    now = int(time.time() * 1000)
    n = str(now)[-6:]
    r = str(int(n) >> 1).zfill(6)
    key = "".join(seed[int(str(n)[i])] for i in range(len(str(n))))
    for j in range(len(r)):
        key += seed[int(r[j]) + 2]

    return {"timestamp": now, "key": key}


# ZPA Token refresh and caching logic
def token_is_about_to_expire(token_fetch_time):
    """Check if the token is about to expire using the timestamp."""
    token_life_seconds = 3600
    buffer_time = 10

    # Check if the time since the token was fetched + buffer exceeds the token's life
    if (time.time() - token_fetch_time) > (token_life_seconds - buffer_time):
        return True
    return False


def is_token_expired(token_string):
    # If token string is None or empty, consider it expired
    if not token_string:
        logger.warning("Token string is None or empty. Requesting a new token.")
        return True

    try:
        # Split the token into its parts
        parts = token_string.split(".")
        if len(parts) != 3:
            return True

        # Decode the payload
        payload_bytes = base64.urlsafe_b64decode(parts[1] + "==")  # Padding might be needed
        payload = json.loads(payload_bytes)

        # Check expiration time
        if "exp" in payload:
            # Deduct 10 seconds to account for any possible latency or clock skew
            expiration_time = payload["exp"] - 10
            if time.time() > expiration_time:
                return True

        return False

    except Exception as e:
        logger.error(f"Error checking token expiration: {str(e)}")
        return True


def pick_version_profile(kwargs: list, payload: list):
    # Used in ZPA endpoints.
    # This function is used to convert the name of the version profile to
    # the version profile id. This means our users don't need to look up the
    # version profile id mapping themselves.

    version_profile = kwargs.pop("version_profile", None)
    if version_profile:
        payload["overrideVersionProfile"] = True
        if version_profile == "default":
            payload["versionProfileId"] = 0
        elif version_profile == "previous_default":
            payload["versionProfileId"] = 1
        elif version_profile == "new_release":
            payload["versionProfileId"] = 2


def remove_cloud_suffix(str_name: str) -> str:
    """
    Removes appended cloud name (e.g. "(zscalerthree.net)") from the string.

    Args:
        str_name (str): The string from which to remove the cloud name.

    Returns:
        str: The string without the cloud name.
    """
    reg = re.compile(r"(.*)\s+\([a-zA-Z0-9\-_\.]*\)\s*$")
    res = reg.sub(r"\1", str_name)
    return res.strip()


class Iterator(APIIterator):
    """Iterator class."""

    page_size = 500

    def __init__(self, api, path: str = "", **kw):
        """Initialize Iterator class."""
        super().__init__(api, **kw)

        self.path = path
        self.max_items = kw.pop("max_items", 0)
        self.max_pages = kw.pop("max_pages", 0)
        self.payload = {}
        if kw:
            self.payload = {snake_to_camel(key): value for key, value in kw.items()}

    def _get_page(self) -> None:
        """Iterator function to get the page."""
        resp = self._api.get(
            self.path,
            params={**self.payload, "page": self.num_pages + 1},
        )
        try:
            # If we are using ZPA then the API will return records under the
            # 'list' key.
            self.page = resp.get("list") or []
        except AttributeError:
            # If the list key doesn't exist then we're likely using ZIA so just
            # return the full response.
            self.page = resp
        finally:
            # If we use the default retry-after logic in Restfly then we are
            # going to keep seeing 429 messages in stdout. ZIA and ZPA have a
            # standard 1 sec rate limit on the API endpoints with pagination so
            # we are going to include it here.
            time.sleep(1)
