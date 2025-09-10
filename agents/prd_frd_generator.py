import json
from typing import Dict, List, Any, TypedDict

from langgraph.graph import StateGraph, END
from graph.state import GraphState
from config.settings import get_llm
from langchain_core.prompts import ChatPromptTemplate
from schemas.models import OutputPrd


class AgentState(TypedDict):
    project_name: str
    feature_name: str
    industry: str
    target_users: str
    business_context: str
    messages: List[Dict[str, str]]
    prd_draft: Dict[str, Any]
    frd_draft: List[Dict[str, Any]]
    final_output: Dict[str, Any]
    step: str


def correct_json_structure(json_data: dict) -> dict:
    """
    Corrects the structure of the provided JSON by removing duplicates, fixing FRD entries,
    and standardizing the overview field.

    Args:
        json_data (dict): The input JSON data with PRD and FRD details.

    Returns:
        dict: The corrected JSON structure.
    """
    # Create a deep copy to avoid modifying the input
    import copy
    corrected_data = copy.deepcopy(json_data)

    # Standardize the overview field in PRD
    if "prd" in corrected_data and "overview" in corrected_data["prd"]:
        # Clean up the overview to remove any trailing or problematic characters
        overview = corrected_data["prd"]["overview"].strip()
        # Ensure overview is concise and properly formatted
        corrected_data["prd"]["overview"] = overview.replace("\n", " ").replace("  ", " ")

    # Process FRD entries
    if "frd" in corrected_data:
        # Remove any empty objects
        corrected_data["frd"] = [entry for entry in corrected_data["frd"] if entry]

        # Fix each FRD entry
        for entry in corrected_data["frd"]:
            # Remove duplicate acceptance criteria
            if "acceptanceCriteria" in entry:
                entry["acceptanceCriteria"] = list(dict.fromkeys(entry["acceptanceCriteria"]))

            # Remove duplicate fields by keeping the first occurrence
            if isinstance(entry.get("title"), list):
                entry["title"] = entry["title"][0] if entry["title"] else ""
            if isinstance(entry.get("description"), list):
                entry["description"] = entry["description"][0] if entry["description"] else ""
            if isinstance(entry.get("priority"), list):
                entry["priority"] = entry["priority"][0] if entry["priority"] else "Medium"

    return corrected_data


def _gather_requirements(state: AgentState) -> AgentState:
    print("🔍 Gathering requirements...")
    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a senior product analyst. Analyze inputs and extract personas, goals, risks, success metrics."),
        (
            "human",
            (
                """
                Analyze the following project details and extract key information:

                Project: {project_name}
                Feature: {feature_name}
                Industry: {industry}
                Target Users: {target_users}
                Business Context: {business_context}

                Identify:
                1) Primary personas and goals
                2) Key business objectives
                3) Potential risks and challenges
                4) Success metrics

                Return a concise markdown summary.
                """
            ),
        ),
    ])

    msg = (prompt | llm).invoke(state)
    state["messages"].append({"role": "assistant", "content": getattr(msg, "content", ""), "step": "requirements_analysis"})
    state["step"] = "requirements_gathered"
    return state


def _generate_prd(state: AgentState) -> AgentState:
    print("📋 Generating PRD...")
    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert PRD writer. Return only JSON matching the requested schema."),
        (
            "human",
            (
                """
                Create a comprehensive PRD for:
                Project: {project_name}
                Feature: {feature_name}

                Context from requirements analysis:
                {last_message}

                Return JSON with fields:
                ```json
                {{
                  "overview": "...",
                  "personas": [{{"name": "...", "goals": ["..."]}}],
                  "business_goals": ["..."],
                  "success_metrics": ["..."],
                  "risks": ["..."]
                }}
                ```
                """
            ),
        ),
    ])

    last_message = state["messages"][-1]["content"] if state["messages"] else ""
    msg = (prompt | llm).invoke({**state, "last_message": last_message})
    text = getattr(msg, "content", "").strip()

    try:
        if text.startswith("```json") and text.endswith("```"):
            text = text[7:-3]
        elif text.startswith("```") and text.endswith("```"):
            text = text[3:-3]
        prd = json.loads(text)
    except Exception:
        prd = {
            "overview": f"AI-powered {state['feature_name']} for {state['project_name']}",
            "personas": [{"name": "Primary User", "goals": ["Access core functionality"]}],
            "business_goals": ["Improve user experience"],
            "success_metrics": ["User adoption > 80%"],
            "risks": ["Low user adoption"],
        }

    state["prd_draft"] = prd
    state["step"] = "prd_generated"
    return state


def _generate_frd(state: AgentState) -> AgentState:
    print("⚙️ Generating FRD...")
    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a senior product engineer. Return only JSON array of FR items."),
        (
            "human",
            (
                """
                Based on the PRD for {project_name} - {feature_name}, create 4-6 functional requirements.

                PRD Context:
                {prd_json}

                Each item must have:
                ```json
                {{
                  "id": "FR-1",
                  "title": "...",
                  "description": "...",
                  "acceptanceCriteria": ["...", "...", "..."],
                  "priority": "High|Medium|Low"
                }}
                ```
                Return only the JSON array.
                """
            ),
        ),
    ])

    prd_json = json.dumps(state["prd_draft"], indent=2)
    msg = (prompt | llm).invoke({**state, "prd_json": prd_json})
    text = getattr(msg, "content", "").strip()

    try:
        if text.startswith("```json") and text.endswith("```"):
            text = text[7:-3]
        elif text.startswith("```") and text.endswith("```"):
            text = text[3:-3]
        frd = json.loads(text)
        if not isinstance(frd, list):
            frd = [frd]
    except Exception:
        frd = [
            {
                "id": "FR-1",
                "title": f"Core {state['feature_name']} Functionality",
                "description": f"Implement the main features of {state['feature_name']}",
                "acceptanceCriteria": ["Feature is accessible", "Feature performs as expected"],
                "priority": "High",
            }
        ]

    state["frd_draft"] = frd
    state["step"] = "frd_generated"
    return state


def _refine_and_validate(state: AgentState) -> AgentState:
    print("✨ Refining and validating documents...")
    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a meticulous reviewer. Provide 3-5 concise improvement notes."),
        (
            "human",
            (
                """
                Review and refine the following PRD and FRD for consistency and completeness.

                PRD:
                {prd_json}

                FRD:
                {frd_json}

                Check for alignment, missing critical functionality, unclear criteria, and priority.
                Return concise bullet points.
                """
            ),
        ),
    ])

    prd_json = json.dumps(state["prd_draft"], indent=2)
    frd_json = json.dumps(state["frd_draft"], indent=2)
    msg = (prompt | llm).invoke({"prd_json": prd_json, "frd_json": frd_json})
    state["messages"].append({"role": "assistant", "content": getattr(msg, "content", ""), "step": "validation_feedback"})
    state["step"] = "documents_validated"
    return state


def _finalize_output(state: AgentState) -> AgentState:
    print("📄 Finalizing output...")
    final_output = {
        "projectName": state["project_name"],
        "featureName": state["feature_name"],
        "prd": state["prd_draft"],
        "frd": state["frd_draft"],
    }
    # Apply the correction function to the final output
    state["final_output"] = correct_json_structure(final_output)
    state["step"] = "completed"
    return state


def _build_graph() -> StateGraph:
    workflow = StateGraph(AgentState)
    workflow.add_node("gather_requirements", _gather_requirements)
    workflow.add_node("generate_prd", _generate_prd)
    workflow.add_node("generate_frd", _generate_frd)
    workflow.add_node("refine_and_validate", _refine_and_validate)
    workflow.add_node("finalize_output", _finalize_output)

    workflow.set_entry_point("gather_requirements")
    workflow.add_edge("gather_requirements", "generate_prd")
    workflow.add_edge("generate_prd", "generate_frd")
    workflow.add_edge("generate_frd", "refine_and_validate")
    workflow.add_edge("refine_and_validate", "finalize_output")
    workflow.add_edge("finalize_output", END)
    return workflow.compile()


def run_prd_frd(project_name: str, feature_name: str, industry: str = "", target_users: str = "", business_context: str = "") -> Dict[str, Any]:
    graph = _build_graph()
    initial_state: AgentState = {
        "project_name": project_name,
        "feature_name": feature_name,
        "industry": industry,
        "target_users": target_users,
        "business_context": business_context,
        "messages": [],
        "prd_draft": {},
        "frd_draft": [],
        "final_output": {},
        "step": "initialized",
    }
    final_state = graph.invoke(initial_state)
    return final_state["final_output"]


def generate_prd_frd_node(state: GraphState) -> dict:
    """LangGraph node to plug into your workflow. Expects state["requirements"]."""
    req = state.get("requirements", {}) or {}

    # If input already matches OutputPrd, validate and passthrough
    if isinstance(req, dict) and all(k in req for k in ("projectName", "featureName", "prd", "frd")):
        try:
            validated = OutputPrd(**req)
            return {"prd": validated.model_dump()}
        except Exception:
            pass

    project_name = req.get("projectName") or req.get("project") or "Unnamed Project"
    feature_name = req.get("featureName") or req.get("feature") or "Core Feature"
    industry = req.get("industry", "")
    target_users = req.get("target_users", req.get("targetUsers", ""))
    business_context = req.get("business_context", req.get("context", ""))

    result = run_prd_frd(project_name, feature_name, industry, target_users, business_context)
    return {"prd": result}