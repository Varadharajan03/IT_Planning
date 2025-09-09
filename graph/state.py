from typing import TypedDict, Dict, Any

class GraphState(TypedDict):
    """
    Represents the state of our graph.
    """
    requirements: Dict[str, Any]
    artifacts: Dict[str, Any]