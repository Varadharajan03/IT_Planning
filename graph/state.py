from typing import TypedDict, Dict, Any, List

class GraphState(TypedDict):
    """
    Represents the state of our graph for the unified workflow.
    """
    # Input requirements
    project_name: str
    feature_name: str
    industry: str
    target_users: str
    business_context: str
    
    # PRD/FRD output
    prd_output: Dict[str, Any]
    
    # Risk analysis output
    risk_analysis: List[Dict[str, Any]]
    risk_thinking: str
    
    # Test case output
    test_artifacts: Dict[str, Any]
    
    # Task execution output
    task_execution_output: Dict[str, Any]
    
    # Resource optimization output
    resource_optimization: Dict[str, Any]
    
    # Final consolidated output
    final_output: Dict[str, Any]



class JiraResourceOptimizationState(TypedDict):
    """
    State for Jira Resource Optimization Workflow.
    """
    email_data: Dict[str, Any]      # Leave mail details
    team_csv: List[Dict[str, Any]]  # Team details
    member_verified: bool           # Verification result
    tasks: List[Dict[str, Any]]     # Jira tasks
    reallocation: Dict[str, Any]    # Task reassignment result
    notifications: List[str]        # Emails sent