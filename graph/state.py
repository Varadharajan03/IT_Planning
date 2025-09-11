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
    
    # Final consolidated output
    final_output: Dict[str, Any]