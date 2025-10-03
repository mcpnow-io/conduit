from typing import Any, Callable, Dict, Optional, TypeVar

from conduit.client.types import (
    validate_api_response,
    validate_search_constraints,
    validate_types,
)

# Import for type checking only to avoid circular imports
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from conduit.client.base import BasePhabricatorClient

T = TypeVar("T")


class TypeSafetyManager:
    """Manager for type safety features and configurations."""

    def __init__(self, enabled: bool = False):
        self.enabled = enabled
        self._validation_cache = {}

    def enable_type_safety(self):
        """Enable type safety features."""
        self.enabled = True

    def disable_type_safety(self):
        """Disable type safety features."""
        self.enabled = False

    def is_enabled(self) -> bool:
        """Check if type safety is enabled."""
        return self.enabled

    def validate_type(self, value: Any, expected_type: type) -> bool:
        """
        Validate that a value matches the expected type.

        Args:
            value: The value to validate
            expected_type: The expected type

        Returns:
            True if validation passes, False otherwise
        """
        if not self.enabled:
            return True

        try:
            # Basic type checking
            if not isinstance(value, expected_type):
                return False

            # Additional validation can be added here
            # For example, checking list contents, dict keys, etc.

            return True

        except (TypeError, ValueError):
            return False

    def validate_search_constraints(self, constraints: dict) -> bool:
        """
        Validate search constraints for common patterns.

        Args:
            constraints: Dictionary of search constraints

        Returns:
            True if constraints are valid, False otherwise
        """
        if not self.enabled:
            return True

        # Validate common constraint patterns
        for key, value in constraints.items():
            if key.endswith("PHIDs") or key.endswith("IDs"):
                if not isinstance(value, list):
                    return False
                if not all(isinstance(item, (str, int)) for item in value):
                    return False
            elif key.endswith("Start") or key.endswith("End"):
                if not isinstance(value, (int, type(None))):
                    return False
            elif key == "query":
                if not isinstance(value, str):
                    return False

        return True

    def get_validation_errors(self, constraints: dict) -> list[str]:
        """
        Get detailed validation errors for constraints.

        Args:
            constraints: Dictionary of search constraints

        Returns:
            List of validation error messages
        """
        errors = []

        if not self.enabled:
            return errors

        for key, value in constraints.items():
            if key.endswith("PHIDs") or key.endswith("IDs"):
                if not isinstance(value, list):
                    errors.append(f"{key} must be a list")
                elif not all(isinstance(item, (str, int)) for item in value):
                    errors.append(f"All items in {key} must be strings or integers")
            elif key.endswith("Start") or key.endswith("End"):
                if not isinstance(value, (int, type(None))):
                    errors.append(f"{key} must be an integer or null")
            elif key == "query":
                if not isinstance(value, str):
                    errors.append("query must be a string")

        return errors


class RuntimeValidationClient:
    """Phabricator client with runtime type validation and error checking."""

    def __init__(self, base_client: "BasePhabricatorClient"):
        self.base_client = base_client

    @validate_types
    def search_users(
        self,
        constraints: Optional[Dict[str, Any]] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """
        Search for users with type-safe constraints.

        Args:
            constraints: User search constraints (validated)
            limit: Maximum number of results

        Returns:
            Validated user search results
        """
        # Validate constraints
        if constraints and not validate_search_constraints(constraints, "user"):
            raise ValueError("Invalid user search constraints")

        # Call base client
        result = self.base_client.user.search(constraints=constraints, limit=limit)

        # Validate response
        if not validate_api_response(result, "user_search"):
            raise ValueError("Invalid user search response structure")

        return result

    @validate_types
    def search_tasks(
        self,
        constraints: Optional[Dict[str, Any]] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """
        Search for tasks with type-safe constraints.

        Args:
            constraints: Task search constraints (validated)
            limit: Maximum number of results

        Returns:
            Validated task search results
        """
        # Validate constraints
        if constraints and not validate_search_constraints(constraints, "task"):
            raise ValueError("Invalid task search constraints")

        # Call base client
        result = self.base_client.maniphest.search_tasks(
            constraints=constraints, limit=limit
        )

        # Validate response
        if not validate_api_response(result, "task_search"):
            raise ValueError("Invalid task search response structure")

        return result

    @validate_types
    def get_user_info(self, phid: str) -> Dict[str, Any]:
        """
        Get detailed user information with type validation.

        Args:
            phid: User PHID

        Returns:
            Validated user information
        """
        # Validate PHID format
        if not isinstance(phid, str) or not phid.startswith("PHID-"):
            raise ValueError("Invalid PHID format")

        # Call base client
        result = self.base_client.user.query(phids=[phid])

        # Validate response
        if not validate_api_response(result, "single_entity"):
            raise ValueError("Invalid user info response structure")

        return result

    @validate_types
    def get_task_info(self, phid: str) -> Dict[str, Any]:
        """
        Get detailed task information with type validation.

        Args:
            phid: Task PHID

        Returns:
            Validated task information
        """
        # Validate PHID format
        if not isinstance(phid, str) or not phid.startswith("PHID-"):
            raise ValueError("Invalid PHID format")

        # Call base client
        result = self.base_client.maniphest.query_tasks(phids=[phid])

        # Validate response
        if not validate_api_response(result, "single_entity"):
            raise ValueError("Invalid task info response structure")

        return result

    def check_type_compatibility(self) -> Dict[str, Any]:
        """
        Check type compatibility across the codebase.

        Returns:
            Dictionary with type compatibility information
        """
        from conduit.client.types import check_type_compatibility

        return check_type_compatibility()


def enable_type_safety_wrapper(func: Callable) -> Callable:
    """
    Decorator to enable type safety for MCP tools.

    Args:
        func: The function to wrap with type safety

    Returns:
        The wrapped function with type safety enabled
    """

    def wrapper(*args, **kwargs):
        # Check if type safety is enabled in kwargs
        enable_type_safety = kwargs.get("enable_type_safety", False)

        if enable_type_safety:
            try:
                from conduit.utils.validation import RuntimeValidationClient

                # Get client and wrap it with type safety
                client = kwargs.get("client")
                if client:
                    type_safe_client = RuntimeValidationClient(client)
                    kwargs["client"] = type_safe_client

            except ImportError:
                # Type safety module not available, proceed without it
                pass

        return func(*args, **kwargs)

    return wrapper


# Global type safety manager instance
type_safety_manager = TypeSafetyManager()


def get_type_safety_manager() -> TypeSafetyManager:
    """Get the global type safety manager instance."""
    return type_safety_manager


def enable_type_safety(enabled: bool = True):
    """Enable or disable type safety globally."""
    type_safety_manager.enabled = enabled


def is_type_safety_enabled() -> bool:
    """Check if type safety is globally enabled."""
    return type_safety_manager.enabled
