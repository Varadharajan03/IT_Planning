from langgraph.graph import StateGraph, END
from .state import GraphState
from agents.testcase_generator import generate_test_artifacts_node
from agents.risk_analysis_agent import analyze_risks
from typing import TypedDict, Any

class RiskState(TypedDict):
    prd: str
    sector: str
    category: str
    search_results: Any
    thinking: str
    risk_analysis: list

workflow = StateGraph(GraphState)

# Define the single node in our workflow
workflow.add_node("generate_artifacts", generate_test_artifacts_node)

# Set the entry point and finish point of the graph
workflow.set_entry_point("generate_artifacts")
workflow.add_edge("generate_artifacts", END)

# Compile the graph into a runnable app
app = workflow.compile()

def run_risk_workflow(prd, sector, category, search_results):
    def risk_node(state: RiskState) -> RiskState:
        thinking, risks = analyze_risks(state["prd"], state["search_results"])
        return {
            "sector": state["sector"],
            "category": state["category"],
            "thinking": thinking,
            "risk_analysis": risks
        }

    builder = StateGraph(RiskState)
    builder.add_node("analyze", risk_node)
    builder.set_entry_point("analyze")
    builder.add_edge("analyze", END)

    graph = builder.compile()

    result = graph.invoke({
        "prd": prd,
        "sector": sector,
        "category": category,
        "search_results": search_results
    })

    return result