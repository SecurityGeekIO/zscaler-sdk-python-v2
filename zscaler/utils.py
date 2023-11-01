import re
from box import Box, BoxList
from typing import List, Optional, Any, Dict
import re
from requests import Response


# Recursive function to convert all keys and nested keys from camel case
# to snake case.
def convert_keys_to_snake(data):
    if isinstance(data, (list, BoxList)):
        return [convert_keys_to_snake(inner_dict) for inner_dict in data]
    elif isinstance(data, (dict, Box)):
        new_dict = {}
        for k in data.keys():
            v = data[k]
            new_key = camel_to_snake(k)
            new_dict[new_key] = convert_keys_to_snake(v) if isinstance(v, (dict, list)) else v
        return new_dict
    else:
        return data


def camelcaseToSnakeCase(obj):
    """
    Converts keys of a dictionary from camelCase to snake_case.

    Parameters:
    - obj (dict): Dictionary with camelCase keys.

    Returns:
    - dict: Dictionary with snake_case keys.
    """

    new_obj = dict()
    for key, value in obj.items():
        if value is not None:
            new_obj[re.sub(r"(?<!^)(?=[A-Z])", "_", key).lower()] = value
    return new_obj


def snakecaseToCamelcase(obj):
    """
    Converts keys of a dictionary from snake_case to camelCase.

    Parameters:
    - obj (dict): Dictionary with snake_case keys.

    Returns:
    - dict: Dictionary with camelCase keys.
    """
    new_obj = dict()
    for key, value in obj.items():
        if value is not None:
            newKey = "".join(x.capitalize() or "_" for x in key.split("_"))
            newKey = newKey[:1].lower() + newKey[1:]
            new_obj[newKey] = value
    return new_obj


def delete_none(f):
    """
    Decorator to remove None values from a dictionary.

    Parameters:
    - f (function): The function to be decorated.

    Returns:
    - function: Decorated function.
    """


def delete_none(f):
    """
    Decorator to remove None values from a dictionary.

    Parameters:
    - f (function): The function to be decorated.

    Returns:
    - function: Decorated function.
    """

    def wrapper(*args, **kwargs):
        _dict = f(*args, **kwargs)
        if _dict is not None:
            return delete_none_values(_dict)
        return _dict

    return wrapper


def delete_none_values(_dict):
    """
    Recursively removes None values from a dictionary or list.

    Parameters:
    - _dict (Union[dict, list]): The dictionary or list to process.

    Returns:
    - Union[dict, list]: Processed dictionary or list without None values.
    """

    if isinstance(_dict, dict):
        for key, value in list(_dict.items()):
            if isinstance(value, (list, dict, tuple, set)):
                _dict[key] = delete_none_values(value)
            elif value is None or key is None:
                del _dict[key]
    elif isinstance(_dict, (list, set, tuple)):
        _dict = type(_dict)(delete_none_values(item) for item in _dict if item is not None)
    return _dict


def mapRespJSON(self, resp_json):
    if resp_json is None:
        return {}
    return camelcaseToSnakeCase(resp_json)


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


def camel_to_snake(name: str):
    """Converts Python camelCase to Zscaler's lower snake_case."""
    # Edge-cases where camelCase is breaking
    edge_cases = {
        "routableIP": "routable_ip",
        "isNameL10nTag": "is_name_l10n_tag",
        "nameL10nTag": "name_l10n_tag",
        "surrogateIP": "surrogate_ip",
        "surrogateIPEnforcedForKnownBrowsers": "surrogate_ip_enforced_for_known_browsers",
    }
    return edge_cases.get(name, re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower())


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


# Takes a tuple if id_groups, kwargs and the payload dict; reformat for API call
def add_id_groups(id_groups: list, kwargs: dict, payload: dict):
    for entry in id_groups:
        if kwargs.get(entry[0]):
            payload[entry[1]] = [{"id": param_id} for param_id in kwargs.pop(entry[0])]
    return


def format_json_response(
    response: Response,
    box_attrs: Optional[Dict] = None,
    conv_json: bool = True,
    conv_box: bool = True,
):
    """
    A simple utility to handle formatting the response object into either a
    Box object or a Python native object from the JSON response.  The function
    will prefer box over python native if both flags are set to true.  If none
    of the flags are true, or if the content-type header reports as something
    other than "applicagion/json", then the response object is instead
    returned.

    Args:
        response:
            The response object that will be checked against.
        box_attrs:
            The optional box attributed to pass as part of instantiation.
        conv_json:
            A flag handling if we should run the JSON conversion to python
            native datatypes.
        conv_box:
            A flaghandling if we should convert the data to a Box object.

    Returns:
        box.Box:
            If the conv_box flag is True, and the response is a single object,
            then the response is a Box obj.
        box.BoxList:
            If the conv_box flag is True, and the response is a list of
            objects, then the response is a BoxList obj.
        dict:
            If the conv_json flag is True and the  conv_box is False, and the
            response is a single object, then the response is a dict obj.
        list:
            If the conv_json flag is True and conv_box is False, and the
            response is a list of objects, then the response is a list obj.
        requests.Response:
            If neither flag is True, or if the response isn't JSON data, then
            a response object is returned (pass-through).
    """
    content_type = response.headers.get("content-type", "application/json")
    if (conv_json or conv_box) and "application/json" in content_type.lower() and len(response.text) > 0:  # noqa: E124
        if conv_box:
            data = convert_keys_to_snake(response.json())
            if isinstance(data, list):
                return BoxList(data, **box_attrs)
            elif isinstance(data, dict):
                return Box(data, **box_attrs)
        elif conv_json:
            return convert_keys_to_snake(response.json())
    return response

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