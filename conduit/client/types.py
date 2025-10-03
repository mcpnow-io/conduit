import inspect
import typing
from functools import wraps
from typing import Any, Callable, Dict, List, Literal, Optional, TypedDict, Union

PHID = str
PolicyID = str


def validate_types(func: Callable) -> Callable:
    """
    Decorator to validate function arguments and return values at runtime.

    Args:
        func: Function to validate

    Returns:
        Wrapped function with type validation
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get function signature and type hints
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        # Get type hints
        type_hints = get_type_hints(func)

        # Validate arguments
        for param_name, value in bound_args.arguments.items():
            if param_name in type_hints and param_name != "return":
                expected_type = type_hints[param_name]
                if not _is_valid_type(value, expected_type):
                    raise TypeError(
                        f"Argument '{param_name}' expected type {expected_type}, "
                        f"got {type(value)} with value {value!r}"
                    )

        # Call function
        result = func(*args, **kwargs)

        # Validate return value
        if "return" in type_hints:
            expected_return_type = type_hints["return"]
            if not _is_valid_type(result, expected_return_type):
                raise TypeError(
                    f"Function '{func.__name__}' expected return type {expected_return_type}, "
                    f"got {type(result)} with value {result!r}"
                )

        return result

    return wrapper


def _is_valid_type(value: Any, expected_type: Any) -> bool:
    """
    Check if a value matches the expected type.

    Args:
        value: Value to validate
        expected_type: Expected type

    Returns:
        True if value matches expected type, False otherwise
    """
    # Handle Any type
    if expected_type is Any:
        return True

    # Handle regular types
    if not hasattr(expected_type, "__origin__"):
        return isinstance(value, expected_type)

    # Handle generic types
    origin = expected_type.__origin__

    # Handle Union types
    if origin is Union:
        return _handle_union_type(value, expected_type)

    # Handle List types
    if origin is list:
        return _handle_list_type(value, expected_type)

    # Handle Dict types
    if origin is dict:
        return _handle_dict_type(value, expected_type)

    # Handle Literal types
    if origin is Literal:
        return _handle_literal_type(value, expected_type)

    # Handle TypedDict
    if _is_typeddict(expected_type):
        return _handle_typeddict_type(value, expected_type)

    return False


def _handle_union_type(value: Any, expected_type: Any) -> bool:
    """Handle Union type validation."""
    # Handle Optional (Union[T, NoneType])
    if type(None) in expected_type.__args__:
        return value is None or _is_valid_type(
            value, next(t for t in expected_type.__args__ if t is not type(None))
        )
    # Handle regular Union
    return any(_is_valid_type(value, t) for t in expected_type.__args__)


def _handle_list_type(value: Any, expected_type: Any) -> bool:
    """Handle List type validation."""
    if not isinstance(value, list):
        return False
    element_type = expected_type.__args__[0]
    return all(_is_valid_type(item, element_type) for item in value)


def _handle_dict_type(value: Any, expected_type: Any) -> bool:
    """Handle Dict type validation."""
    if not isinstance(value, dict):
        return False
    key_type, value_type = expected_type.__args__
    return all(
        _is_valid_type(k, key_type) and _is_valid_type(v, value_type)
        for k, v in value.items()
    )


def _handle_literal_type(value: Any, expected_type: Any) -> bool:
    """Handle Literal type validation."""
    return value in expected_type.__args__


def _is_typeddict(expected_type: Any) -> bool:
    """Check if a type is a TypedDict."""
    return (
        hasattr(expected_type, "__origin__")
        and expected_type.__origin__ is dict
        and hasattr(expected_type, "__annotations__")
    )


def _handle_typeddict_type(value: Any, expected_type: Any) -> bool:
    """Handle TypedDict type validation."""
    # Check basic structure
    if not isinstance(value, dict):
        return False

    # Get required and optional fields
    required_fields, optional_fields = _get_typeddict_fields(expected_type)

    # Check required fields
    for field_name in required_fields:
        if field_name not in value:
            return False
        if not _is_valid_type(
            value[field_name], expected_type.__annotations__[field_name]
        ):
            return False

    # Check optional fields
    for field_name in optional_fields:
        if field_name in value and not _is_valid_type(
            value[field_name], expected_type.__annotations__[field_name]
        ):
            return False

    return True


def _get_typeddict_fields(expected_type: Any) -> tuple[set, set]:
    """Get required and optional fields from a TypedDict."""
    required_fields = set()
    optional_fields = set()

    for field_name, field_type in expected_type.__annotations__.items():
        if hasattr(field_type, "__origin__") and field_type.__origin__ is Union:
            # Check if it's Optional (Union[T, NoneType])
            if type(None) in field_type.__args__:
                optional_fields.add(field_name)
            else:
                required_fields.add(field_name)
        else:
            required_fields.add(field_name)

    return required_fields, optional_fields


def get_type_hints(obj: Any) -> Dict[str, Any]:
    """
    Get type hints for an object, handling compatibility issues.

    Args:
        obj: Object to get type hints for

    Returns:
        Dictionary of type hints
    """
    try:
        return typing.get_type_hints(obj)
    except (NameError, TypeError):
        # Fallback for older Python versions or complex objects
        return getattr(obj, "__annotations__", {})


def validate_search_constraints(
    constraints: Dict[str, Any], constraint_type: str
) -> bool:
    """
    Validate search constraints for different entity types.

    Args:
        constraints: Dictionary of search constraints
        constraint_type: Type of entity being searched

    Returns:
        True if constraints are valid, False otherwise
    """
    constraint_schemas = {
        "user": {
            "ids": lambda x: isinstance(x, list) and all(isinstance(i, int) for i in x),
            "phids": lambda x: isinstance(x, list)
            and all(isinstance(i, str) for i in x),
            "usernames": lambda x: isinstance(x, list)
            and all(isinstance(i, str) for i in x),
            "nameLike": lambda x: isinstance(x, str),
            "isAdmin": lambda x: isinstance(x, bool),
            "isDisabled": lambda x: isinstance(x, bool),
            "isBot": lambda x: isinstance(x, bool),
            "createdStart": lambda x: isinstance(x, int),
            "createdEnd": lambda x: isinstance(x, int),
            "query": lambda x: isinstance(x, str),
        },
        "task": {
            "ids": lambda x: isinstance(x, list) and all(isinstance(i, int) for i in x),
            "phids": lambda x: isinstance(x, list)
            and all(isinstance(i, str) for i in x),
            "assigned": lambda x: isinstance(x, list)
            and all(isinstance(i, str) for i in x),
            "authorPHIDs": lambda x: isinstance(x, list)
            and all(isinstance(i, str) for i in x),
            "statuses": lambda x: isinstance(x, list)
            and all(isinstance(i, str) for i in x),
            "priorities": lambda x: isinstance(x, list)
            and all(isinstance(i, int) for i in x),
            "projects": lambda x: isinstance(x, list)
            and all(isinstance(i, str) for i in x),
            "subscribers": lambda x: isinstance(x, list)
            and all(isinstance(i, str) for i in x),
            "createdStart": lambda x: isinstance(x, int),
            "createdEnd": lambda x: isinstance(x, int),
            "modifiedStart": lambda x: isinstance(x, int),
            "modifiedEnd": lambda x: isinstance(x, int),
            "query": lambda x: isinstance(x, str),
            "hasParents": lambda x: isinstance(x, bool),
            "hasSubtasks": lambda x: isinstance(x, bool),
            "withUnassigned": lambda x: isinstance(x, bool),
            "ownerPHIDs": lambda x: isinstance(x, list)
            and all(isinstance(i, str) for i in x),
            "spacePHIDs": lambda x: isinstance(x, list)
            and all(isinstance(i, str) for i in x),
        },
        "repository": {
            "ids": lambda x: isinstance(x, list) and all(isinstance(i, int) for i in x),
            "phids": lambda x: isinstance(x, list)
            and all(isinstance(i, str) for i in x),
            "names": lambda x: isinstance(x, list)
            and all(isinstance(i, str) for i in x),
            "callsigns": lambda x: isinstance(x, list)
            and all(isinstance(i, str) for i in x),
            "vcs": lambda x: isinstance(x, str) and x in ["git", "hg", "svn"],
            "status": lambda x: isinstance(x, str) and x in ["active", "inactive"],
        },
    }

    if constraint_type not in constraint_schemas:
        return False

    schema = constraint_schemas[constraint_type]

    for key, value in constraints.items():
        # Accept additional constraint keys that are not explicitly
        # modelled in the schema to preserve forward compatibility.
        if key not in schema:
            continue
        if not schema[key](value):
            return False

    return True


def validate_api_response(response: Dict[str, Any], expected_structure: str) -> bool:
    """
    Validate API response structure.

    Args:
        response: API response to validate
        expected_structure: Expected response structure type

    Returns:
        True if response is valid, False otherwise
    """
    structure_schemas = {
        "user_search": {
            "data": list,
            "cursor": dict,
            "query": dict,
            "maps": dict,
        },
        "task_search": {
            "data": list,
            "cursor": dict,
            "query": dict,
            "maps": dict,
        },
        "repository_search": {
            "data": list,
            "cursor": dict,
        },
    }

    if expected_structure == "single_entity":
        # Legacy endpoints such as user.query return a dictionary keyed by
        # PHID instead of the modern {"result": {...}} wrapper. Accept any
        # dictionary payload here to remain compatible with the actual API
        # responses.
        return isinstance(response, dict)

    if expected_structure not in structure_schemas:
        return False

    schema = structure_schemas[expected_structure]

    for key, expected_type in schema.items():
        if key not in response:
            return False
        if not isinstance(response[key], expected_type):
            return False

    return True


def check_type_compatibility() -> Dict[str, Any]:
    """
    Check type compatibility across the codebase.

    Returns:
        Dictionary with type compatibility information
    """
    compatibility_report = {
        "typedict_definitions": [],
        "validation_rules": [],
        "client_methods": [],
        "api_responses": [],
        "issues": [],
    }

    # Analyze TypedDict definitions
    for name, obj in globals().items():
        if hasattr(obj, "__origin__") and obj.__origin__ is dict:
            try:
                annotations = getattr(obj, "__annotations__", {})
                compatibility_report["typedict_definitions"].append(
                    {
                        "name": name,
                        "fields": list(annotations.keys()),
                        "total_fields": len(annotations),
                    }
                )
            except (AttributeError, TypeError):
                # Skip objects that don't have annotations
                continue

    # Analyze validation rules
    compatibility_report["validation_rules"] = [
        "user_search_constraints",
        "task_search_constraints",
        "repository_search_constraints",
        "api_response_validation",
    ]

    # Analyze client methods
    compatibility_report["client_methods"] = [
        "search_users",
        "search_tasks",
        "search_repositories",
        "get_task_details",
        "get_user_details",
    ]

    return compatibility_report


class ManiphestTaskInfo(TypedDict):
    """Enhanced task information with strict typing."""

    id: int
    phid: PHID
    authorPHID: PHID
    ownerPHID: Optional[PHID]
    ccPHIDs: List[PHID]
    status: str
    statusName: str
    isClosed: bool
    priority: int  # Numeric priority (0-100)
    priorityColor: str
    title: str
    description: str
    projectPHIDs: List[PHID]
    uri: str
    auxiliary: List[Any]
    objectName: str
    dateCreated: int  # Unix timestamp
    dateModified: int  # Unix timestamp
    dependsOnTaskPHIDs: List[PHID]
    points: Optional[float]
    attached: List[Dict[str, Any]]  # File attachments


class UserInfo(TypedDict):
    """Enhanced user information with strict typing."""

    phid: PHID
    userName: str
    realName: str
    image: str
    uri: str
    roles: List[str]
    primaryEmail: str
    dateCreated: int  # Unix timestamp
    dateModified: int  # Unix timestamp
    isDisabled: bool
    isBot: bool
    isAdmin: bool
    mfaEnabled: bool
    policies: Dict[str, str]  # policy_name -> policy_value


# Search-related types for user.search
class UserSearchConstraints(TypedDict, total=False):
    """Constraints for user.search API"""

    ids: List[int]
    phids: List[PHID]
    usernames: List[str]
    nameLike: str
    isAdmin: bool
    isDisabled: bool
    isBot: bool
    isMailingList: bool
    needsApproval: bool
    mfa: bool
    createdStart: int  # epoch timestamp
    createdEnd: int  # epoch timestamp
    query: str  # fulltext search


class UserSearchAttachments(TypedDict, total=False):
    """Attachments for user.search API"""

    availability: bool


class UserSearchCursor(TypedDict, total=False):
    """Cursor information for paging through search results"""

    limit: int
    after: Optional[str]
    before: Optional[str]
    order: Optional[str]


class UserSearchFields(TypedDict, total=False):
    """Fields returned in user search results"""

    username: str
    realName: str
    roles: List[str]
    dateCreated: int
    dateModified: int
    policy: dict  # map of capabilities to policies


class UserSearchAttachmentData(TypedDict, total=False):
    """Attachment data in user search results"""

    availability: dict


class UserSearchResult(TypedDict):
    """Enhanced user search result with strict typing."""

    id: int
    type: Literal["USER"]
    phid: PHID
    fields: UserSearchFields
    attachments: Optional[UserSearchAttachmentData]


class UserSearchResults(TypedDict):
    """Complete user search results structure"""

    data: List[UserSearchResult]
    cursor: UserSearchCursor
    query: dict
    maps: dict


# Transaction types for maniphest.edit
class ManiphestTaskTransactionBase(TypedDict):
    type: str


class ManiphestTaskTransactionParent(ManiphestTaskTransactionBase):
    type: Literal["parent"]
    value: PHID


class ManiphestTaskColumnPosition(TypedDict, total=False):
    columnPHID: PHID
    beforePHIDs: List[PHID]
    afterPHIDs: List[PHID]


class ManiphestTaskTransactionColumn(ManiphestTaskTransactionBase):
    type: Literal["column"]
    value: Union[PHID, List[PHID], List[ManiphestTaskColumnPosition]]


class ManiphestTaskTransactionSpace(ManiphestTaskTransactionBase):
    type: Literal["space"]
    value: PHID


class ManiphestTaskTransactionTitle(ManiphestTaskTransactionBase):
    type: Literal["title"]
    value: str


class ManiphestTaskTransactionOwner(ManiphestTaskTransactionBase):
    type: Literal["owner"]
    value: Union[PHID, None]


class ManiphestTaskTransactionStatus(ManiphestTaskTransactionBase):
    type: Literal["status"]
    value: str


class ManiphestTaskTransactionPriority(ManiphestTaskTransactionBase):
    type: Literal["priority"]
    value: str


class ManiphestTaskTransactionDescription(ManiphestTaskTransactionBase):
    type: Literal["description"]
    value: str


class ManiphestTaskTransactionParentsAdd(ManiphestTaskTransactionBase):
    type: Literal["parents.add"]
    value: List[PHID]


class ManiphestTaskTransactionParentsRemove(ManiphestTaskTransactionBase):
    type: Literal["parents.remove"]
    value: List[PHID]


class ManiphestTaskTransactionParentsSet(ManiphestTaskTransactionBase):
    type: Literal["parents.set"]
    value: List[PHID]


class ManiphestTaskTransactionSubtasksAdd(ManiphestTaskTransactionBase):
    type: Literal["subtasks.add"]
    value: List[PHID]


class ManiphestTaskTransactionSubtasksRemove(ManiphestTaskTransactionBase):
    type: Literal["subtasks.remove"]
    value: List[PHID]


class ManiphestTaskTransactionSubtasksSet(ManiphestTaskTransactionBase):
    type: Literal["subtasks.set"]
    value: List[PHID]


class ManiphestTaskTransactionView(ManiphestTaskTransactionBase):
    """Change the view policy of the object."""

    type: Literal["view"]
    value: str


class ManiphestTaskTransactionEdit(ManiphestTaskTransactionBase):
    """Change the edit policy of the object."""

    type: Literal["edit"]
    value: str


class ManiphestTaskTransactionProjectsAdd(ManiphestTaskTransactionBase):
    type: Literal["projects.add"]
    value: List[PHID]


class ManiphestTaskTransactionProjectsRemove(ManiphestTaskTransactionBase):
    type: Literal["projects.remove"]
    value: List[PHID]


class ManiphestTaskTransactionProjectsSet(ManiphestTaskTransactionBase):
    type: Literal["projects.set"]
    value: List[PHID]


class ManiphestTaskTransactionSubscribersAdd(ManiphestTaskTransactionBase):
    type: Literal["subscribers.add"]
    value: List[PHID]


class ManiphestTaskTransactionSubscribersRemove(ManiphestTaskTransactionBase):
    type: Literal["subscribers.remove"]
    value: List[PHID]


class ManiphestTaskTransactionSubscribersSet(ManiphestTaskTransactionBase):
    type: Literal["subscribers.set"]
    value: List[PHID]


class ManiphestTaskTransactionSubtype(ManiphestTaskTransactionBase):
    type: Literal["subtype"]
    value: str


class ManiphestTaskTransactionComment(ManiphestTaskTransactionBase):
    type: Literal["comment"]
    value: str


class ManiphestTaskTransactionMFA(ManiphestTaskTransactionBase):
    type: Literal["mfa"]
    value: bool


# Union type for all possible transaction types
ManiphestTaskTransaction = Union[
    ManiphestTaskTransactionParent,
    ManiphestTaskTransactionColumn,
    ManiphestTaskTransactionSpace,
    ManiphestTaskTransactionTitle,
    ManiphestTaskTransactionOwner,
    ManiphestTaskTransactionStatus,
    ManiphestTaskTransactionPriority,
    ManiphestTaskTransactionDescription,
    ManiphestTaskTransactionParentsAdd,
    ManiphestTaskTransactionParentsRemove,
    ManiphestTaskTransactionParentsSet,
    ManiphestTaskTransactionSubtasksAdd,
    ManiphestTaskTransactionSubtasksRemove,
    ManiphestTaskTransactionSubtasksSet,
    ManiphestTaskTransactionView,
    ManiphestTaskTransactionEdit,
    ManiphestTaskTransactionProjectsAdd,
    ManiphestTaskTransactionProjectsRemove,
    ManiphestTaskTransactionProjectsSet,
    ManiphestTaskTransactionSubscribersAdd,
    ManiphestTaskTransactionSubscribersRemove,
    ManiphestTaskTransactionSubscribersSet,
    ManiphestTaskTransactionSubtype,
    ManiphestTaskTransactionComment,
    ManiphestTaskTransactionMFA,
]


# Search-related types for maniphest.search
class ManiphestSearchConstraints(TypedDict, total=False):
    """Constraints for maniphest.search API"""

    ids: List[int]
    phids: List[PHID]
    assigned: List[str]  # usernames or PHIDs
    authorPHIDs: List[PHID]
    statuses: List[str]
    priorities: List[int]
    subtypes: List[str]
    columnPHIDs: List[PHID]
    hasParents: bool
    hasSubtasks: bool
    parentIDs: List[int]
    subtaskIDs: List[int]
    createdStart: int  # epoch timestamp
    createdEnd: int  # epoch timestamp
    modifiedStart: int  # epoch timestamp
    modifiedEnd: int  # epoch timestamp
    closedStart: int  # epoch timestamp
    closedEnd: int  # epoch timestamp
    closerPHIDs: List[PHID]
    query: str  # fulltext search
    subscribers: List[str]  # usernames or PHIDs
    projects: List[str]  # project names or PHIDs


class ManiphestSearchAttachments(TypedDict, total=False):
    """Attachments for maniphest.search API"""

    columns: bool
    subscribers: bool
    projects: bool


class ManiphestSearchCursor(TypedDict, total=False):
    """Cursor information for paging through search results"""

    limit: int
    after: Optional[str]
    before: Optional[str]
    order: Optional[str]


class ManiphestTaskSearchFields(TypedDict, total=False):
    """Fields returned in search results"""

    name: str  # This is the task title
    description: dict  # Structure: {"raw": "description text"}
    authorPHID: PHID
    ownerPHID: Optional[PHID]
    status: dict  # Structure: {"value": "open", "name": "Open", "color": null}
    priority: (
        dict  # Structure: {"value": 90, "name": "Needs Triage", "color": "violet"}
    )
    points: Optional[float]
    subtype: str
    closerPHID: Optional[PHID]
    dateClosed: Optional[int]
    spacePHID: Optional[PHID]
    dateCreated: int
    dateModified: int
    policy: dict  # map of capabilities to policies


class ManiphestTaskSearchAttachmentData(TypedDict, total=False):
    """Attachment data in search results"""

    subscribers: dict
    projects: dict
    columns: dict


class ManiphestTaskSearchResult(TypedDict):
    """Enhanced task search result with strict typing."""

    id: int
    type: Literal["TASK"]
    phid: PHID
    fields: ManiphestTaskSearchFields
    attachments: Optional[ManiphestTaskSearchAttachmentData]


class ManiphestSearchResults(TypedDict):
    """Complete search results structure"""

    data: List[ManiphestTaskSearchResult]
    cursor: ManiphestSearchCursor
    query: dict
    maps: dict


# Enhanced API response types
class APIResponse(TypedDict):
    """Standard API response structure."""

    result: Dict[str, Any]
    error_info: Optional[Dict[str, Any]]
    cursor: Optional[Dict[str, Any]]


class SuccessResponse(APIResponse):
    """Successful API response."""

    result: Dict[str, Any]
    error_info: None


class ErrorResponse(APIResponse):
    """Error API response."""

    result: None
    error_info: Dict[str, Any]
    error_code: str
    error_message: str
