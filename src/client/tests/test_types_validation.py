#!/usr/bin/env python3

import os
import sys
from typing import Any, Dict, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from src.client.base import BasePhabricatorClient
from src.utils import RuntimeValidationClient
from src.client.types import (
    ManiphestTaskInfo,
    ManiphestTaskSearchResult,
    UserInfo,
    UserSearchResult,
    check_type_compatibility,
    validate_api_response,
    validate_search_constraints,
    validate_types,
)


def test_type_validation_decorator():
    """Test the type validation decorator."""
    print("Testing type validation decorator...")

    @validate_types
    def test_function(x: int, y: str, z: Optional[Dict[str, Any]] = None) -> str:
        return f"{x}: {y}: {z}"

    # Test valid inputs
    result = test_function(42, "hello", {"key": "value"})
    assert result == "42: hello: {'key': 'value'}"
    print("✓ Valid inputs work correctly")

    # Test invalid inputs
    try:
        test_function("not_an_int", "hello")
        assert False, "Should have raised TypeError"
    except TypeError as e:
        print(f"✓ Invalid input correctly rejected: {e}")

    print("Type validation decorator tests passed!\n")


def test_constraint_validation():
    """Test constraint validation functions."""
    print("Testing constraint validation...")

    # Test user constraints
    user_constraints = {
        "ids": [1, 2, 3],
        "usernames": ["alice", "bob"],
        "nameLike": "test",
        "isAdmin": True,
    }

    assert validate_search_constraints(user_constraints, "user")
    print("✓ User constraints validation works")

    # Test task constraints
    task_constraints = {
        "ids": [1, 2, 3],
        "statuses": ["open", "closed"],
        "priorities": [90, 80],
        "query": "bug",
    }

    assert validate_search_constraints(task_constraints, "task")
    print("✓ Task constraints validation works")

    # Unknown keys should be ignored for forward compatibility
    unknown_constraints = {"invalid_field": "value"}
    assert validate_search_constraints(unknown_constraints, "user")
    print("✓ Unknown constraint keys are ignored")

    # Invalid value types are still rejected
    bad_type_constraints = {"ids": "not-a-list"}
    assert not validate_search_constraints(bad_type_constraints, "user")
    print("✓ Invalid constraint value types are rejected")

    print("Constraint validation tests passed!\n")


def test_api_response_validation():
    """Test API response validation."""
    print("Testing API response validation...")

    # Test valid user search response
    valid_user_response = {
        "data": [
            {
                "id": 1,
                "type": "USER",
                "phid": "PHID-USER-123",
                "fields": {"username": "alice"},
                "attachments": None,
            }
        ],
        "cursor": {"limit": 100},
        "query": {},
        "maps": {},
    }

    assert validate_api_response(valid_user_response, "user_search")
    print("✓ Valid user search response validation works")

    # Test valid task search response
    valid_task_response = {
        "data": [
            {
                "id": 1,
                "type": "TASK",
                "phid": "PHID-TASK-123",
                "fields": {"name": "Test task"},
                "attachments": None,
            }
        ],
        "cursor": {"limit": 100},
        "query": {},
        "maps": {},
    }

    assert validate_api_response(valid_task_response, "task_search")
    print("✓ Valid task search response validation works")

    # Test invalid response
    invalid_response = {"missing": "data"}
    assert not validate_api_response(invalid_response, "user_search")
    print("✓ Invalid response correctly rejected")

    print("API response validation tests passed!\n")


def test_enhanced_types():
    """Test enhanced type definitions."""
    print("Testing enhanced type definitions...")

    # Test ManiphestTaskInfo
    task_info: ManiphestTaskInfo = {
        "id": 123,
        "phid": "PHID-TASK-123",
        "authorPHID": "PHID-USER-456",
        "ownerPHID": "PHID-USER-789",
        "ccPHIDs": ["PHID-USER-101"],
        "status": "open",
        "statusName": "Open",
        "isClosed": False,
        "priority": 90,
        "priorityColor": "violet",
        "title": "Test Task",
        "description": "A test task",
        "projectPHIDs": ["PHID-PROJ-202"],
        "uri": "https://example.com/T123",
        "auxiliary": [],
        "objectName": "T123",
        "dateCreated": 1640995200,
        "dateModified": 1640995200,
        "dependsOnTaskPHIDs": [],
        "points": 5.0,
        "attached": [],
    }

    assert isinstance(task_info, dict)
    print("✓ Enhanced ManiphestTaskInfo type works")

    # Test UserInfo
    user_info: UserInfo = {
        "phid": "PHID-USER-123",
        "userName": "alice",
        "realName": "Alice Smith",
        "image": "https://example.com/avatar.jpg",
        "uri": "https://example.com/user/alice",
        "roles": ["user"],
        "primaryEmail": "alice@example.com",
        "dateCreated": 1640995200,
        "dateModified": 1640995200,
        "isDisabled": False,
        "isBot": False,
        "isAdmin": False,
        "mfaEnabled": True,
        "policies": {"default": "policy-123"},
    }

    assert isinstance(user_info, dict)
    print("✓ Enhanced UserInfo type works")

    # Test UserSearchResult
    user_search_result: UserSearchResult = {
        "id": 1,
        "type": "USER",
        "phid": "PHID-USER-123",
        "fields": {"username": "alice"},
        "attachments": None,
    }

    assert isinstance(user_search_result, dict)
    print("✓ Enhanced UserSearchResult type works")

    # Test ManiphestTaskSearchResult
    task_search_result: ManiphestTaskSearchResult = {
        "id": 1,
        "type": "TASK",
        "phid": "PHID-TASK-123",
        "fields": {"name": "Test task"},
        "attachments": None,
    }

    assert isinstance(task_search_result, dict)
    print("✓ Enhanced ManiphestTaskSearchResult type works")

    print("Enhanced type definitions tests passed!\n")


def test_type_compatibility():
    """Test type compatibility checking."""
    print("Testing type compatibility...")

    compatibility_report = check_type_compatibility()

    assert "typedict_definitions" in compatibility_report
    assert "validation_rules" in compatibility_report
    assert "client_methods" in compatibility_report
    assert "issues" in compatibility_report

    print(
        f"✓ Type compatibility report generated with {len(compatibility_report['typedict_definitions'])} TypedDict definitions"
    )
    print("✓ Type compatibility checking works")

    print("Type compatibility tests passed!\n")


def test_type_safe_client():
    """Test type-safe client wrapper."""
    print("Testing type-safe client wrapper...")

    # Create a mock user client
    class MockUserClient:
        def search(
            self, constraints: Optional[Dict[str, Any]] = None, limit: int = 100
        ) -> Dict[str, Any]:
            return {
                "data": [
                    {
                        "id": 1,
                        "type": "USER",
                        "phid": "PHID-USER-123",
                        "fields": {"username": "alice"},
                        "attachments": None,
                    }
                ],
                "cursor": {"limit": 100},
                "query": {},
                "maps": {},
            }

    # Create a mock maniphest client
    class MockManiphestClient:
        def search_tasks(
            self, constraints: Optional[Dict[str, Any]] = None, limit: int = 100
        ) -> Dict[str, Any]:
            return {
                "data": [
                    {
                        "id": 1,
                        "type": "TASK",
                        "phid": "PHID-TASK-123",
                        "fields": {"name": "Test task"},
                        "attachments": None,
                    }
                ],
                "cursor": {"limit": 100},
                "query": {},
                "maps": {},
            }

    # Create a mock base client
    class MockBaseClient(BasePhabricatorClient):
        def __init__(self):
            # Don't call super().__init__ to avoid requiring real API credentials
            self.user = MockUserClient()
            self.maniphest = MockManiphestClient()

        def _make_request(
            self, method: str, params: Dict[str, Any] = None
        ) -> Dict[str, Any]:
            # This method won't be called since we're using the mock clients directly
            return {}

    # Create type-safe client
    mock_client = MockBaseClient()
    type_safe_client = RuntimeValidationClient(mock_client)

    # Test user search
    user_constraints = {"usernames": ["alice"]}
    result = type_safe_client.search_users(constraints=user_constraints)
    assert "data" in result
    print("✓ Type-safe user search works")

    # Test task search
    task_constraints = {"statuses": ["open"]}
    result = type_safe_client.search_tasks(constraints=task_constraints)
    assert "data" in result
    print("✓ Type-safe task search works")

    # Test compatibility check
    compatibility = type_safe_client.check_type_compatibility()
    assert "typedict_definitions" in compatibility
    print("✓ Type-safe client compatibility check works")

    print("Type-safe client tests passed!\n")


def main():
    """Run all tests."""
    print("Starting type system implementation tests...\n")

    try:
        test_type_validation_decorator()
        test_constraint_validation()
        test_api_response_validation()
        test_enhanced_types()
        test_type_compatibility()
        test_type_safe_client()

        print("All tests passed! Type system implementation is working correctly.")
        return True

    except Exception as e:
        print(f"Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
