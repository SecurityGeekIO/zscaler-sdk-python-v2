
import re

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