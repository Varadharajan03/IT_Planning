import json
from schemas.models import OutputArtifacts
from graph.state import GraphState
from config.settings import get_llm  # <-- IMPORT the centralized model function
from langchain_core.prompts import ChatPromptTemplate

def generate_test_artifacts_node(state: GraphState) -> dict:
    """
    A LangGraph node that uses the centralized Gemini model to generate test artifacts.
    """
    print("🤖 Executing agent node with centralized Gemini config...")
    requirements = state.get("requirements")
    if not requirements:
        raise ValueError("Requirements are missing from the state.")

    # Get the configured LLM from the settings file
    llm = get_llm()
    structured_llm = llm.with_structured_output(OutputArtifacts)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert QA Engineer. Generate a comprehensive set of user stories and test cases based on the provided requirements. Include positive, negative, and edge-case scenarios."),
        ("human", "Project requirements:\n\n{requirements_json}")
    ])

    chain = prompt | structured_llm
    response = chain.invoke({"requirements_json": json.dumps(requirements)})

    return {"artifacts": response.dict()}

