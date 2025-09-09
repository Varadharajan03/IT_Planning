from langgraph.graph import StateGraph, END
from .state import GraphState
from agents.testcase_generator import generate_test_artifacts_node

# Create a new graph
workflow = StateGraph(GraphState)

# Define the single node in our workflow
workflow.add_node("generate_artifacts", generate_test_artifacts_node)

# Set the entry point and finish point of the graph
workflow.set_entry_point("generate_artifacts")
workflow.add_edge("generate_artifacts", END)

# Compile the graph into a runnable app
app = workflow.compile()