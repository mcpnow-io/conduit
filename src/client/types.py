from typing import Any, List, Literal, Optional, TypedDict, Union

PHID = str
PolicyID = str


class ManiphestTaskInfo(TypedDict):
    id: str
    phid: PHID
    authorPHID: PHID
    ownerPHID: Union[PHID, None]
    ccPHIDs: List[PHID]
    status: str
    statusName: str
    isClosed: bool
    priority: str
    priorityColor: str
    title: str
    description: str
    projectPHIDs: List[PHID]
    uri: str
    auxiliary: List[Any]
    objectName: str
    dateCreated: str  # Unix timestamp
    dateModified: str  # Unix timestamp
    dependsOnTaskPHIDs: List[PHID]


class UserInfo(TypedDict):
    phid: PHID
    userName: str
    realName: str
    image: str
    uri: str
    roles: List[str]
    primaryEmail: str


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
    """Individual task result from search"""

    id: int
    type: str  # Usually "TASK"
    phid: PHID
    fields: ManiphestTaskSearchFields
    attachments: Optional[ManiphestTaskSearchAttachmentData]


class ManiphestSearchResults(TypedDict):
    """Complete search results structure"""

    data: List[ManiphestTaskSearchResult]
    cursor: ManiphestSearchCursor
    query: dict
    maps: dict
