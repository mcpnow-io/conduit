from typing import Any, List, Literal, TypedDict, Union

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


class ManiphestTaskTransactionCommitsAdd(ManiphestTaskTransactionBase):
    type: Literal["commits.add"]
    value: List[PHID]


class ManiphestTaskTransactionCommitsRemove(ManiphestTaskTransactionBase):
    type: Literal["commits.remove"]
    value: List[PHID]


class ManiphestTaskTransactionCommitsSet(ManiphestTaskTransactionBase):
    type: Literal["commits.set"]
    value: List[PHID]


class ManiphestTaskTransactionView(ManiphestTaskTransactionBase):
    type: Literal["view"]
    value: str


class ManiphestTaskTransactionEdit(ManiphestTaskTransactionBase):
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
    ManiphestTaskTransactionCommitsAdd,
    ManiphestTaskTransactionCommitsRemove,
    ManiphestTaskTransactionCommitsSet,
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
