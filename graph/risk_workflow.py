from langgraph.graph import StateGraph, END
from .state import GraphState
from agents.testcase_generator import generate_test_artifacts_node
from agents.risk_analysis_agent import analyze_risks
from typing import TypedDict, Any

# Define state schema for the risk workflow
class RiskState(TypedDict):
    prd: str
    sector: str
    category: str
    search_results: Any  # Use Any for flexibility, or specify a type if known
    thinking: str
    risk_analysis: list  # Adjust type based on analyze_risks output

# Original workflow for test case generation
workflow = StateGraph(GraphState)

# Define the single node in the original workflow
workflow.add_node("generate_artifacts", generate_test_artifacts_node)

# Set the entry point and finish point of the original workflow
workflow.set_entry_point("generate_artifacts")
workflow.add_edge("generate_artifacts", END)

# Compile the original graph into a runnable app
app = workflow.compile()

# New risk analysis workflow
def run_risk_workflow(prd, sector, category, search_results):
    def risk_node(state: RiskState) -> RiskState:
        thinking, risks = analyze_risks(state["prd"], state["search_results"])
        return {
            "sector": state["sector"],
            "category": state["category"],
            "thinking": thinking,
            "risk_analysis": risks
        }

    builder = StateGraph(RiskState)  # Use RiskState as the state schema
    builder.add_node("analyze", risk_node)
    builder.set_entry_point("analyze")
    builder.add_edge("analyze", END)  # Corrected to use add_edge

    graph = builder.compile()

    result = graph.invoke({
        "prd": prd,
        "sector": sector,
        "category": category,
        "search_results": search_results
    })

    return result