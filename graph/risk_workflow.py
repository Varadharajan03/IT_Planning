from langgraph.graph import StateGraph, END
from agents.risk_analysis_agent import analyze_risks

def run_risk_workflow(prd, sector, category, search_results):
    def risk_node(state):
        thinking, risks = analyze_risks(state["prd"], state["search_results"])
        return {
            "sector": state["sector"],
            "category": state["category"],
            "thinking": thinking,
            "risk_analysis": risks
        }

    builder = StateGraph()
    builder.add_node("analyze", risk_node)
    builder.set_entry_point("analyze")
    builder.set_finish_point(END)

    graph = builder.compile()

    result = graph.invoke({
        "prd": prd,
        "sector": sector,
        "category": category,
        "search_results": search_results
    })

    return result
