from pydantic import BaseModel
from typing import List, Dict, Any

class JiraTask(BaseModel):
    key: str
    summary: str
    priority: str
    assignee: str
    status: str
    dueDate: str | None

class ReallocationResult(BaseModel):
    reassignedTasks: List[Dict[str, Any]]
    targetUser: str
