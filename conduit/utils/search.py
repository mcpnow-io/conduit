from typing import Any, Dict, List, Optional


def build_search_constraints(
    constraints: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> Dict[str, Any]:
    """
    Build standardized search constraints from various inputs.

    Args:
        constraints: Base constraints dictionary
        **kwargs: Additional constraint parameters

    Returns:
        Combined constraints dictionary
    """
    if constraints is None:
        constraints = {}

    # Add any additional constraints from kwargs
    constraints.update(kwargs)

    return constraints


def build_user_search_constraints(
    ids: Optional[List[int]] = None,
    phids: Optional[List[str]] = None,
    usernames: Optional[List[str]] = None,
    name_like: Optional[str] = None,
    is_admin: Optional[bool] = None,
    is_disabled: Optional[bool] = None,
    is_bot: Optional[bool] = None,
    is_mailing_list: Optional[bool] = None,
    needs_approval: Optional[bool] = None,
    mfa: Optional[bool] = None,
    created_start: Optional[int] = None,
    created_end: Optional[int] = None,
    fulltext_query: Optional[str] = None,
    **kwargs,
) -> Dict[str, Any]:
    """
    Build user-specific search constraints.

    Args:
        ids: List of user IDs
        phids: List of user PHIDs
        usernames: List of usernames
        name_like: Filter by name containing this string
        is_admin: Filter by admin status
        is_disabled: Filter by disabled status
        is_bot: Filter by bot status
        is_mailing_list: Filter by mailing list status
        needs_approval: Filter by approval status
        mfa: Filter by MFA enrollment
        created_start: Created after this timestamp
        created_end: Created before this timestamp
        fulltext_query: Full-text search query
        **kwargs: Additional constraints

    Returns:
        User search constraints dictionary
    """
    constraints = {}

    if ids:
        constraints["ids"] = ids
    if phids:
        constraints["phids"] = phids
    if usernames:
        constraints["usernames"] = usernames
    if name_like:
        constraints["nameLike"] = name_like
    if is_admin is not None:
        constraints["isAdmin"] = is_admin
    if is_disabled is not None:
        constraints["isDisabled"] = is_disabled
    if is_bot is not None:
        constraints["isBot"] = is_bot
    if is_mailing_list is not None:
        constraints["isMailingList"] = is_mailing_list
    if needs_approval is not None:
        constraints["needsApproval"] = needs_approval
    if mfa is not None:
        constraints["mfa"] = mfa
    if created_start is not None:
        constraints["createdStart"] = created_start
    if created_end is not None:
        constraints["createdEnd"] = created_end
    if fulltext_query:
        constraints["query"] = fulltext_query

    # Add any additional constraints
    constraints.update(kwargs)

    return constraints


def build_task_search_constraints(
    assigned: Optional[List[str]] = None,
    author_phids: Optional[List[str]] = None,
    statuses: Optional[List[str]] = None,
    priorities: Optional[List[int]] = None,
    projects: Optional[List[str]] = None,
    subscribers: Optional[List[str]] = None,
    fulltext_query: Optional[str] = None,
    has_parents: Optional[bool] = None,
    has_subtasks: Optional[bool] = None,
    created_after: Optional[int] = None,
    created_before: Optional[int] = None,
    modified_after: Optional[int] = None,
    modified_before: Optional[int] = None,
    **kwargs,
) -> Dict[str, Any]:
    """
    Build task-specific search constraints.

    Args:
        assigned: List of assignees
        author_phids: List of author PHIDs
        statuses: List of statuses
        priorities: List of priorities
        projects: List of projects
        subscribers: List of subscribers
        fulltext_query: Full-text search query
        has_parents: Filter by parent tasks
        has_subtasks: Filter by subtasks
        created_after: Created after this timestamp
        created_before: Created before this timestamp
        modified_after: Modified after this timestamp
        modified_before: Modified before this timestamp
        **kwargs: Additional constraints

    Returns:
        Task search constraints dictionary
    """
    constraints = {}

    if assigned:
        constraints["assigned"] = assigned
    if author_phids:
        constraints["authorPHIDs"] = author_phids
    if statuses:
        constraints["statuses"] = statuses
    if priorities:
        constraints["priorities"] = priorities
    if projects:
        constraints["projects"] = projects
    if subscribers:
        constraints["subscribers"] = subscribers
    if fulltext_query:
        constraints["query"] = fulltext_query
    if has_parents is not None:
        constraints["hasParents"] = has_parents
    if has_subtasks is not None:
        constraints["hasSubtasks"] = has_subtasks
    if created_after:
        constraints["createdStart"] = created_after
    if created_before:
        constraints["createdEnd"] = created_before
    if modified_after:
        constraints["modifiedStart"] = modified_after
    if modified_before:
        constraints["modifiedEnd"] = modified_before

    # Add any additional constraints
    constraints.update(kwargs)

    return constraints


def build_repository_search_constraints(
    name_contains: Optional[str] = None,
    vcs_type: Optional[str] = None,
    status: Optional[str] = None,
    callsigns: Optional[List[str]] = None,
    names: Optional[List[str]] = None,
    short_names: Optional[List[str]] = None,
    **kwargs,
) -> Dict[str, Any]:
    """
    Build repository-specific search constraints.

    Args:
        name_contains: Filter by name containing this string
        vcs_type: Filter by VCS type
        status: Filter by status
        callsigns: List of callsigns
        names: List of names
        short_names: List of short names
        **kwargs: Additional constraints

    Returns:
        Repository search constraints dictionary
    """
    constraints = {}

    if name_contains:
        constraints["name"] = name_contains
    if vcs_type:
        constraints["vcs"] = vcs_type
    if status:
        constraints["status"] = status
    if callsigns:
        constraints["callsigns"] = callsigns
    if names:
        constraints["names"] = names
    if short_names:
        constraints["shortNames"] = short_names

    # Add any additional constraints
    constraints.update(kwargs)

    return constraints
