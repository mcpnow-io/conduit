from typing import Any, List, TypedDict, Union

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
