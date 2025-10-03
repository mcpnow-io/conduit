import json
from typing import Any, Dict, List


def serialize_json_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Serialize list fields in parameters to JSON strings.

    This is commonly needed for Phabricator API calls that expect
    certain fields to be passed as JSON-encoded strings.

    Args:
        params: Parameter dictionary to serialize

    Returns:
        Parameter dictionary with list fields serialized to JSON
    """
    serialized_params = params.copy()

    for key, value in serialized_params.items():
        if isinstance(value, (list, dict)):
            serialized_params[key] = json.dumps(value)

    return serialized_params


def serialize_list_field(value: List[Any]) -> str:
    """
    Serialize a list field to JSON string.

    Args:
        value: List value to serialize

    Returns:
        JSON string representation of the list
    """
    return json.dumps(value)


def serialize_dict_field(value: Dict[str, Any]) -> str:
    """
    Serialize a dictionary field to JSON string.

    Args:
        value: Dictionary value to serialize

    Returns:
        JSON string representation of the dictionary
    """
    return json.dumps(value)


def safe_serialize(value: Any) -> str:
    """
    Safely serialize any value to JSON string.

    Args:
        value: Value to serialize

    Returns:
        JSON string representation of the value

    Raises:
        ValueError: If the value cannot be serialized
    """
    try:
        return json.dumps(value)
    except (TypeError, ValueError) as e:
        raise ValueError(f"Cannot serialize value: {str(e)}")


def deserialize_json_field(json_str: str) -> Any:
    """
    Deserialize a JSON string field.

    Args:
        json_str: JSON string to deserialize

    Returns:
        Deserialized Python object

    Raises:
        ValueError: If JSON parsing fails
    """
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON field: {str(e)}")


def is_json_serializable(value: Any) -> bool:
    """
    Check if a value can be serialized to JSON.

    Args:
        value: Value to check

    Returns:
        True if the value is JSON serializable, False otherwise
    """
    try:
        json.dumps(value)
        return True
    except (TypeError, ValueError):
        return False
