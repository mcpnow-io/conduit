from typing import Any, Dict, List, Optional, Union


def build_search_params(
    query_key: Optional[str] = None,
    constraints: Optional[Dict[str, Any]] = None,
    attachments: Optional[Dict[str, Any]] = None,
    order: Optional[Union[str, List[str]]] = None,
    before: Optional[str] = None,
    after: Optional[str] = None,
    limit: int = 100,
    **kwargs,
) -> Dict[str, Any]:
    """
    Build standardized search parameters for Phabricator API calls.

    Args:
        query_key: Builtin query key for the search
        constraints: Search constraints dictionary
        attachments: Attachments to include in results
        order: Result ordering (string or list of columns)
        before: Cursor for previous page
        after: Cursor for next page
        limit: Maximum number of results to return
        **kwargs: Additional search parameters

    Returns:
        Dictionary of built search parameters
    """
    params = {"limit": limit}

    if query_key:
        params["queryKey"] = query_key

    if constraints:
        flattened_constraints = dict(flatten_params(constraints, "constraints"))
        params.update(flattened_constraints)

    if attachments:
        flattened_attachments = dict(flatten_params(attachments, "attachments"))
        params.update(flattened_attachments)

    if order:
        params["order"] = order

    if before:
        params["before"] = before

    if after:
        params["after"] = after

    # Add any additional parameters
    params.update(kwargs)

    return params


def build_transaction_params(
    transactions: List[Dict[str, Any]],
    object_identifier: Optional[str] = None,
    **kwargs,
) -> Dict[str, Any]:
    """
    Build standardized transaction parameters for Phabricator API calls.

    Args:
        transactions: List of transaction objects
        object_identifier: Existing object identifier to update
        **kwargs: Additional transaction parameters

    Returns:
        Dictionary of built transaction parameters
    """
    params = {}

    if object_identifier:
        params["objectIdentifier"] = object_identifier

    if transactions:
        params = {
            **{k: v for k, v in flatten_params(transactions, "transactions")},
            **params,
        }

    # Add any additional parameters
    params.update(kwargs)

    return params


def flatten_params(d: Any, prefix: str = "") -> List[tuple]:
    """
    Flatten nested dictionary parameters for API requests.

    This function is moved from src/client/base.py to centralize
    parameter flattening logic.

    Args:
        d: Dictionary, list, or primitive value to flatten
        prefix: Prefix for the parameter names

    Returns:
        List of (key, value) tuples for flattened parameters
    """
    params = []
    if isinstance(d, dict):
        for k, v in d.items():
            if prefix:
                new_prefix = f"{prefix}[{k}]"
            else:
                new_prefix = str(k)
            params.extend(flatten_params(v, new_prefix))
    elif isinstance(d, list):
        for i, v in enumerate(d):
            new_prefix = f"{prefix}[{i}]"
            params.extend(flatten_params(v, new_prefix))
    else:
        params.append((prefix, d))
    return params
