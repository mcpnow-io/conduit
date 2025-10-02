"""Tests for serialization utilities."""

import pytest

from src.utils.serialization import (
    deserialize_json_field,
    is_json_serializable,
    safe_serialize,
    serialize_dict_field,
    serialize_json_params,
    serialize_list_field,
)


class TestSerializeJsonParams:
    """Test JSON parameter serialization."""

    def test_serialize_json_params_with_lists(self):
        """Test serializing parameters with list values."""
        params = {
            "ids": [1, 2, 3],
            "names": ["alice", "bob"],
            "status": "active",
        }

        result = serialize_json_params(params)

        assert result["ids"] == "[1, 2, 3]"
        assert result["names"] == '["alice", "bob"]'
        assert result["status"] == "active"

    def test_serialize_json_params_with_dicts(self):
        """Test serializing parameters with dict values."""
        params = {
            "constraints": {"status": "open", "priority": "high"},
            "metadata": {"key": "value"},
        }

        result = serialize_json_params(params)

        assert result["constraints"] == '{"status": "open", "priority": "high"}'
        assert result["metadata"] == '{"key": "value"}'

    def test_serialize_json_params_mixed_types(self):
        """Test serializing parameters with mixed types."""
        params = {
            "ids": [1, 2, 3],
            "status": "active",
            "count": 5,
            "constraints": {"type": "bug"},
            "enabled": True,
        }

        result = serialize_json_params(params)

        assert result["ids"] == "[1, 2, 3]"
        assert result["status"] == "active"
        assert result["count"] == 5
        assert result["constraints"] == '{"type": "bug"}'
        assert result["enabled"] is True

    def test_serialize_json_params_empty(self):
        """Test serializing empty parameters."""
        params = {}

        result = serialize_json_params(params)

        assert result == {}

    def test_serialize_json_params_no_serializable_types(self):
        """Test serializing parameters with no list/dict values."""
        params = {
            "status": "active",
            "count": 5,
            "enabled": True,
        }

        result = serialize_json_params(params)

        assert result == params

    def test_serialize_json_params_original_unchanged(self):
        """Test that original parameters are not modified."""
        params = {
            "ids": [1, 2, 3],
            "status": "active",
        }

        original = params.copy()
        serialize_json_params(params)

        assert params == original


class TestSerializeListField:
    """Test list field serialization."""

    def test_serialize_list_field_simple(self):
        """Test serializing a simple list."""
        data = [1, 2, 3]

        result = serialize_list_field(data)

        assert result == "[1, 2, 3]"

    def test_serialize_list_field_strings(self):
        """Test serializing a list of strings."""
        data = ["alice", "bob", "charlie"]

        result = serialize_list_field(data)

        assert result == '["alice", "bob", "charlie"]'

    def test_serialize_list_field_mixed(self):
        """Test serializing a mixed list."""
        data = [1, "string", True, None]

        result = serialize_list_field(data)

        assert result == '[1, "string", true, null]'

    def test_serialize_list_field_empty(self):
        """Test serializing an empty list."""
        data = []

        result = serialize_list_field(data)

        assert result == "[]"

    def test_serialize_list_field_nested(self):
        """Test serializing a nested list."""
        data = [[1, 2], [3, 4]]

        result = serialize_list_field(data)

        assert result == "[[1, 2], [3, 4]]"


class TestSerializeDictField:
    """Test dictionary field serialization."""

    def test_serialize_dict_field_simple(self):
        """Test serializing a simple dictionary."""
        data = {"key": "value", "count": 5}

        result = serialize_dict_field(data)

        assert result == '{"key": "value", "count": 5}'

    def test_serialize_dict_field_nested(self):
        """Test serializing a nested dictionary."""
        data = {
            "user": {"name": "alice", "age": 30},
            "settings": {"theme": "dark"},
        }

        result = serialize_dict_field(data)

        assert '"user": {"name": "alice", "age": 30}' in result
        assert '"settings": {"theme": "dark"}' in result

    def test_serialize_dict_field_empty(self):
        """Test serializing an empty dictionary."""
        data = {}

        result = serialize_dict_field(data)

        assert result == "{}"

    def test_serialize_dict_field_special_types(self):
        """Test serializing dictionary with special types."""
        data = {
            "active": True,
            "count": None,
            "list": [1, 2, 3],
        }

        result = serialize_dict_field(data)

        assert '"active": true' in result
        assert '"count": null' in result
        assert '"list": [1, 2, 3]' in result


class TestSafeSerialize:
    """Test safe serialization."""

    def test_safe_serialize_valid_types(self):
        """Test safe serialization with valid types."""
        assert safe_serialize("string") == '"string"'
        assert safe_serialize(123) == "123"
        assert safe_serialize(True) == "true"
        assert safe_serialize(None) == "null"
        assert safe_serialize([1, 2, 3]) == "[1, 2, 3]"
        assert safe_serialize({"key": "value"}) == '{"key": "value"}'

    def test_safe_serialize_unserializable(self):
        """Test safe serialization with unserializable types."""

        # Function cannot be serialized
        def test_func():
            pass

        with pytest.raises(ValueError) as exc_info:
            safe_serialize(test_func)

        assert "Cannot serialize value" in str(exc_info.value)

    def test_safe_serialize_complex_object(self):
        """Test safe serialization with complex object."""

        class CustomObject:
            def __str__(self):
                return "custom object"

        obj = CustomObject()

        with pytest.raises(ValueError) as exc_info:
            safe_serialize(obj)

        assert "Cannot serialize value" in str(exc_info.value)


class TestDeserializeJsonField:
    """Test JSON field deserialization."""

    def test_deserialize_json_field_valid(self):
        """Test deserializing valid JSON strings."""
        assert deserialize_json_field('{"key": "value"}') == {"key": "value"}
        assert deserialize_json_field("[1, 2, 3]") == [1, 2, 3]
        assert deserialize_json_field('"string"') == "string"
        assert deserialize_json_field("123") == 123
        assert deserialize_json_field("true") is True
        assert deserialize_json_field("null") is None

    def test_deserialize_json_field_invalid(self):
        """Test deserializing invalid JSON strings."""
        with pytest.raises(ValueError) as exc_info:
            deserialize_json_field('{"invalid": json}')

        assert "Invalid JSON field" in str(exc_info.value)

    def test_deserialize_json_field_empty_string(self):
        """Test deserializing empty string."""
        with pytest.raises(ValueError) as exc_info:
            deserialize_json_field("")

        assert "Invalid JSON field" in str(exc_info.value)

    def test_deserialize_json_field_malformed(self):
        """Test deserializing malformed JSON."""
        with pytest.raises(ValueError) as exc_info:
            deserialize_json_field('{"unclosed": "object"')

        assert "Invalid JSON field" in str(exc_info.value)


class TestIsJsonSerializable:
    """Test JSON serializability checking."""

    def test_is_json_serializable_valid_types(self):
        """Test checking valid JSON serializable types."""
        assert is_json_serializable("string") is True
        assert is_json_serializable(123) is True
        assert is_json_serializable(True) is True
        assert is_json_serializable(None) is True
        assert is_json_serializable([1, 2, 3]) is True
        assert is_json_serializable({"key": "value"}) is True
        assert is_json_serializable([]) is True
        assert is_json_serializable({}) is True

    def test_is_json_serializable_invalid_types(self):
        """Test checking invalid JSON serializable types."""

        def test_func():
            pass

        class CustomObject:
            pass

        assert is_json_serializable(test_func) is False
        assert is_json_serializable(CustomObject()) is False

    def test_is_json_serializable_complex_nested(self):
        """Test checking complex nested structures."""
        data = {
            "users": [
                {"name": "alice", "active": True},
                {"name": "bob", "active": False},
            ],
            "count": 2,
            "metadata": None,
        }

        assert is_json_serializable(data) is True

    def test_is_json_serializable_with_invalid_nested(self):
        """Test checking structure with invalid nested content."""

        def test_func():
            pass

        data = {
            "valid": "data",
            "invalid": test_func,
        }

        assert is_json_serializable(data) is False
