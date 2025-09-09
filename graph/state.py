from typing import TypedDict, Dict, Any, List

class GraphState(TypedDict):
    """
    State for Jira Resource Optimization Workflow.
    """
    email_data: Dict[str, Any]      # Leave mail details
    team_csv: List[Dict[str, Any]]  # Team details
    member_verified: bool           # Verification result
    tasks: List[Dict[str, Any]]     # Jira tasks
    reallocation: Dict[str, Any]    # Task reassignment result
    notifications: List[str]        # Emails sent


class GraphState(TypedDict):
    """
    Represents the state of our graph.
    """
    requirements: Dict[str, Any]
    artifacts: Dict[str, Any]
