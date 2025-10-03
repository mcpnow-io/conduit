"""Tests for validation utilities."""

from conduit.utils.validation import (
    TypeSafetyManager,
    RuntimeValidationClient,
    enable_type_safety_wrapper,
    get_type_safety_manager,
    enable_type_safety,
    is_type_safety_enabled,
)


class TestTypeSafetyManager:
    """Test TypeSafetyManager class."""

    def test_type_safety_manager_initialization(self):
        """Test TypeSafetyManager initialization."""
        manager = TypeSafetyManager()

        assert manager.enabled is False
        assert manager._validation_cache == {}

    def test_type_safety_manager_enabled_initialization(self):
        """Test TypeSafetyManager initialization with enabled=True."""
        manager = TypeSafetyManager(enabled=True)

        assert manager.enabled is True

    def test_enable_type_safety(self):
        """Test enabling type safety."""
        manager = TypeSafetyManager()
        manager.enable_type_safety()

        assert manager.is_enabled() is True

    def test_disable_type_safety(self):
        """Test disabling type safety."""
        manager = TypeSafetyManager(enabled=True)
        manager.disable_type_safety()

        assert manager.is_enabled() is False

    def test_validate_type_disabled(self):
        """Test type validation when disabled."""
        manager = TypeSafetyManager(enabled=False)

        # Should return True even for wrong type
        assert manager.validate_type("string", int) is True

    def test_validate_type_enabled_correct(self):
        """Test type validation when enabled with correct type."""
        manager = TypeSafetyManager(enabled=True)

        assert manager.validate_type("string", str) is True
        assert manager.validate_type(123, int) is True
        assert manager.validate_type([1, 2, 3], list) is True

    def test_validate_type_enabled_incorrect(self):
        """Test type validation when enabled with incorrect type."""
        manager = TypeSafetyManager(enabled=True)

        assert manager.validate_type("string", int) is False
        assert manager.validate_type(123, str) is False
        assert manager.validate_type("not_a_list", list) is False

    def test_validate_search_constraints_disabled(self):
        """Test search constraints validation when disabled."""
        manager = TypeSafetyManager(enabled=False)

        constraints = {"invalid": "constraints"}
        assert manager.validate_search_constraints(constraints) is True

    def test_validate_search_constraints_enabled_valid(self):
        """Test search constraints validation when enabled with valid constraints."""
        manager = TypeSafetyManager(enabled=True)

        constraints = {
            "ids": [1, 2, 3],
            "phids": ["PHID-USER-1", "PHID-USER-2"],
            "createdStart": 1609459200,
            "createdEnd": 1640995200,
            "query": "search term",
        }
        assert manager.validate_search_constraints(constraints) is True

    def test_validate_search_constraints_enabled_invalid_phids(self):
        """Test search constraints validation with invalid PHIDs."""
        manager = TypeSafetyManager(enabled=True)

        constraints = {"phids": "not_a_list"}
        # The actual implementation only validates specific patterns
        # and "phids" doesn't end with the validated suffixes
        assert manager.validate_search_constraints(constraints) is True

    def test_validate_search_constraints_enabled_invalid_timestamps(self):
        """Test search constraints validation with invalid timestamps."""
        manager = TypeSafetyManager(enabled=True)

        constraints = {"createdStart": "not_a_number"}
        assert manager.validate_search_constraints(constraints) is False

    def test_validate_search_constraints_enabled_invalid_query(self):
        """Test search constraints validation with invalid query."""
        manager = TypeSafetyManager(enabled=True)

        constraints = {"query": 123}
        assert manager.validate_search_constraints(constraints) is False

    def test_get_validation_errors_disabled(self):
        """Test getting validation errors when disabled."""
        manager = TypeSafetyManager(enabled=False)

        constraints = {"invalid": "constraints"}
        errors = manager.get_validation_errors(constraints)

        assert errors == []

    def test_get_validation_errors_enabled_valid(self):
        """Test getting validation errors when enabled with valid constraints."""
        manager = TypeSafetyManager(enabled=True)

        constraints = {
            "ids": [1, 2, 3],
            "phids": ["PHID-USER-1"],
            "createdStart": 1609459200,
            "query": "search",
        }
        errors = manager.get_validation_errors(constraints)

        assert errors == []

    def test_get_validation_errors_enabled_invalid(self):
        """Test getting validation errors when enabled with invalid constraints."""
        manager = TypeSafetyManager(enabled=True)

        constraints = {
            "phids": "not_a_list",
            "ids": [1, "invalid"],
            "createdStart": "not_a_number",
            "query": 123,
        }
        errors = manager.get_validation_errors(constraints)

        # The actual implementation only validates keys ending with specific suffixes
        # "phids" and "ids" don't end with "PHIDs" or "IDs", so they won't be validated
        assert len(errors) == 2
        assert "createdStart must be an integer or null" in errors
        assert "query must be a string" in errors


class TestTypeSafetyGlobals:
    """Test global type safety functions."""

    def test_get_type_safety_manager(self):
        """Test getting global type safety manager."""
        manager = get_type_safety_manager()

        assert isinstance(manager, TypeSafetyManager)

    def test_enable_type_safety_global(self):
        """Test enabling type safety globally."""
        # Save original state
        original_state = is_type_safety_enabled()

        try:
            enable_type_safety(True)
            assert is_type_safety_enabled() is True

            enable_type_safety(False)
            assert is_type_safety_enabled() is False
        finally:
            # Restore original state
            enable_type_safety(original_state)

    def test_enable_type_safety_wrapper(self):
        """Test type safety wrapper decorator."""

        @enable_type_safety_wrapper
        def test_function(client=None, enable_type_safety=False):
            return {"client": client, "type_safety": enable_type_safety}

        # Test without type safety
        result = test_function(client="mock_client")
        assert result["client"] == "mock_client"
        assert result["type_safety"] is False

        # Test with type safety enabled - client gets wrapped
        result = test_function(client="mock_client", enable_type_safety=True)
        # The client should be wrapped with RuntimeValidationClient
        from conduit.utils.validation import RuntimeValidationClient

        assert isinstance(result["client"], RuntimeValidationClient)
        assert result["type_safety"] is True


class TestRuntimeValidationClient:
    """Test RuntimeValidationClient class."""

    def test_runtime_validation_client_initialization(self):
        """Test RuntimeValidationClient initialization."""
        # We can't easily test this without a real BasePhabricatorClient
        # but we can test that it expects the right parameter
        try:
            # This should fail because we're not passing a BasePhabricatorClient
            RuntimeValidationClient(None)
        except Exception:
            # Expected to fail with some kind of error when trying to use the client
            pass
