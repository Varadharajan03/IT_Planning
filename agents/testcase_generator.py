import json
from schemas.models import OutputArtifacts
from graph.state import GraphState
from config.settings import get_llm
from langchain_core.prompts import ChatPromptTemplate

def generate_test_artifacts_node(state: GraphState) -> dict:
    """
    A LangGraph node that analyzes flexible input and produces a strictly structured output.
    """
    print("🤖 Executing agent node with structured output...")
    requirements = state.get("requirements")
    if not requirements:
        raise ValueError("Requirements are missing from the state.")

    # Get the configured LLM from the settings file
    llm = get_llm()
    
    # Force the LLM to adhere to our OutputArtifacts model
    structured_llm = llm.with_structured_output(OutputArtifacts)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert QA Engineer. Analyze the provided project requirements document and generate a comprehensive set of user stories and test cases. The output MUST strictly follow the provided JSON schema."),
        ("human", "Here are the project requirements:\n\n{requirements_json}")
    ])

    chain = prompt | structured_llm
    response = chain.invoke({"requirements_json": json.dumps(requirements, indent=2)})

    return {"artifacts": response.dict()}

