import json
from typing import Dict, List, Any, TypedDict

from langgraph.graph import StateGraph, END
from graph.state import GraphState
from config.settings import get_llm
from langchain_core.prompts import ChatPromptTemplate
from schemas.models import OutputPrd


def _analyze_brd_for_project_details(uploaded_documents: List[Dict[str, Any]]) -> Dict[str, str]:
    """Analyze BRD documents to extract project name and feature name."""
    if not uploaded_documents:
        return {"project_name": "BRD-Based Project", "feature_name": "BRD Analysis"}
    
    llm = get_llm()
    
    # Combine all document content for analysis
    combined_content = ""
    document_titles = []
    
    for doc in uploaded_documents:
        doc_name = doc.get('name', 'Unknown')
        doc_content = doc.get('content', 'No content available')
        document_titles.append(doc_name)
        
        # Add document name and content
        combined_content += f"\n\n=== Document: {doc_name} ===\n"
        combined_content += doc_content[:2000]  # First 2000 chars for analysis
        if len(doc_content) > 2000:
            combined_content += "...[content truncated]"
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert business analyst. Extract the main project name and primary feature/capability from BRD documents. Be concise and specific."),
        (
            "human",
            (
                """
                Analyze the following BRD document(s) and extract:
                1. The main PROJECT NAME (what is the overall project/system being built?)
                2. The primary FEATURE NAME (what is the main feature/capability being described?)
                
                Document titles: {document_titles}
                
                Document content:
                {combined_content}
                
                Guidelines:
                - Look for project names in titles, headers, or explicit project references
                - Look for feature names in requirements sections, feature lists, or capability descriptions
                - If multiple features exist, identify the most important or primary one
                - Be specific and avoid generic terms like "System" or "Platform" unless that's truly the name
                - If unclear, make reasonable inferences based on the content
                
                Return ONLY a JSON object with exactly this format:
                {{
                  "project_name": "Specific Project Name",
                  "feature_name": "Primary Feature Name"
                }}
                """
            ),
        ),
    ])
    
    try:
        msg = (prompt | llm).invoke({
            "document_titles": ", ".join(document_titles),
            "combined_content": combined_content
        })
        text = getattr(msg, "content", "").strip()
        
        # Parse JSON response
        if text.startswith("```json") and text.endswith("```"):
            text = text[7:-3]
        elif text.startswith("```") and text.endswith("```"):
            text = text[3:-3]
        
        result = json.loads(text)
        
        # Validate and clean the results
        project_name = result.get("project_name", "BRD-Based Project").strip()
        feature_name = result.get("feature_name", "BRD Analysis").strip()
        
        # Fallback to document title if extraction failed
        if project_name in ["BRD-Based Project", "Unknown Project", "Project", ""] and document_titles:
            # Try to derive project name from first document title
            first_title = document_titles[0]
            # Remove file extension
            if '.' in first_title:
                first_title = first_title.rsplit('.', 1)[0]
            # Clean up common BRD/document prefixes
            project_name = first_title.replace('BRD', '').replace('brd', '').replace('_', ' ').replace('-', ' ').strip()
            if not project_name:
                project_name = "BRD-Based Project"
        
        return {
            "project_name": project_name,
            "feature_name": feature_name
        }
        
    except Exception as e:
        print(f"Error analyzing BRD for project details: {e}")
        # Fallback logic using document titles
        if document_titles:
            first_title = document_titles[0]
            if '.' in first_title:
                first_title = first_title.rsplit('.', 1)[0]
            project_name = first_title.replace('BRD', '').replace('brd', '').replace('_', ' ').replace('-', ' ').strip()
            if not project_name:
                project_name = "BRD-Based Project"
            return {
                "project_name": project_name,
                "feature_name": "Core Functionality"
            }
        
        return {"project_name": "BRD-Based Project", "feature_name": "BRD Analysis"}


class AgentState(TypedDict):
    project_name: str
    feature_name: str
    industry: str
    target_users: str
    business_context: str
    uploaded_documents: List[Dict[str, Any]]
    it_domain: str
    technology_stack: str
    compliance_requirements: str
    messages: List[Dict[str, str]]
    prd_draft: Dict[str, Any]
    architecture_draft: Dict[str, Any]
    frd_draft: List[Dict[str, Any]]
    final_output: Dict[str, Any]
    step: str


def _gather_requirements(state: AgentState) -> AgentState:
    print("🔍 Gathering requirements...")
    llm = get_llm()

    # Extract project details from BRD documents first
    if state.get("uploaded_documents"):
        print("📄 Analyzing BRD documents for project details...")
        extracted_details = _analyze_brd_for_project_details(state["uploaded_documents"])
        
        # Update state with extracted project details
        state["project_name"] = extracted_details["project_name"]
        state["feature_name"] = extracted_details["feature_name"]
        
        print(f"✅ Extracted Project: {state['project_name']}")
        print(f"✅ Extracted Feature: {state['feature_name']}")

    # Process uploaded BRD documents for context
    document_context = ""
    if state.get("uploaded_documents"):
        document_context = "\n\n**Business Requirement Document Analysis:**\n"
        for doc in state["uploaded_documents"]:
            doc_name = doc.get('name', 'Unknown')
            doc_content = doc.get('content', 'No content available')
            
            # Enhanced BRD analysis
            document_context += f"- **{doc_name}** ({doc.get('type', 'Unknown type')}):\n"
            document_context += f"  Content: {doc_content[:800]}...\n"
            
            # Extract key BRD sections if available
            if any(keyword in doc_content.lower() for keyword in ['functional requirements', 'business goals', 'stakeholders', 'success metrics']):
                document_context += f"  **BRD Structure Detected**: Contains structured business requirements\n"

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a senior product analyst. Analyze inputs and extract personas, goals, risks, success metrics. Pay special attention to any uploaded documents for additional context."),
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
                {document_context}

                Identify:
                1) Primary personas and goals
                2) Key business objectives
                3) Potential risks and challenges
                4) Success metrics
                5) Additional insights from uploaded documents (if any)

                Return a concise markdown summary.
                """
            ),
        ),
    ])

    msg = (prompt | llm).invoke({**state, "document_context": document_context})
    state["messages"].append({"role": "assistant", "content": getattr(msg, "content", ""), "step": "requirements_analysis"})
    state["step"] = "requirements_gathered"
    return state


def _generate_prd(state: AgentState) -> AgentState:
    print("📋 Generating PRD...")
    llm = get_llm()

    # Include BRD context in PRD generation
    document_context = ""
    if state.get("uploaded_documents"):
        document_context = "\n\n**Business Requirement Document Information:**\n"
        for doc in state["uploaded_documents"]:
            doc_content = doc.get('content', 'No content available')
            document_context += f"- **{doc.get('name', 'Unknown')}**: {doc_content[:500]}...\n"
    
    # Get IT-specific context from state
    it_domain = state.get("it_domain", "")
    technology_stack = state.get("technology_stack", "")
    compliance_requirements = state.get("compliance_requirements", "")
    
    it_context = ""
    if it_domain or technology_stack or compliance_requirements:
        it_context = "\n\n**IT-Specific Context:**\n"
        if it_domain:
            it_context += f"- IT Domain: {it_domain}\n"
        if technology_stack:
            it_context += f"- Technology Stack: {technology_stack}\n"
        if compliance_requirements:
            it_context += f"- Compliance Requirements: {compliance_requirements}\n"

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert IT Product Requirements Document writer. Focus on IT industry best practices and technical requirements. Return only JSON matching the requested schema."),
        (
            "human",
            (
                """
                Create a comprehensive IT-focused PRD for:
                Project: {project_name}
                Feature: {feature_name}

                Context from requirements analysis:
                {last_message}
                {document_context}
                {it_context}

                Return JSON with fields:
                ```json
                {{
                  "overview": "...",
                  "personas": [{{"name": "...", "goals": ["..."], "pain_points": ["..."], "technical_skills": "..."}}],
                  "business_goals": ["..."],
                  "success_metrics": ["..."],
                  "risks": ["..."],
                  "document_insights": ["Additional insights from uploaded BRD documents"],
                  "technical_requirements": {{
                    "performance": "...",
                    "security": "...",
                    "scalability": "...",
                    "compatibility": "..."
                  }},
                  "compliance_requirements": ["..."],
                  "integration_requirements": ["..."]
                }}
                ```
                """
            ),
        ),
    ])

    last_message = state["messages"][-1]["content"] if state["messages"] else ""
    msg = (prompt | llm).invoke({**state, "last_message": last_message, "document_context": document_context, "it_context": it_context})
    text = getattr(msg, "content", "").strip()

    try:
        if text.startswith("```json") and text.endswith("```"):
            text = text[7:-3]
        elif text.startswith("```") and text.endswith("```"):
            text = text[3:-3]
        prd = json.loads(text)
    except Exception:
        prd = {
            "overview": f"IT system {state['feature_name']} for {state['project_name']}",
            "personas": [{"name": "End User", "goals": ["Access core functionality"], "pain_points": ["Limited functionality"], "technical_skills": "Basic"}],
            "business_goals": ["Improve operational efficiency", "Enhance user experience"],
            "success_metrics": ["System availability > 99%", "User satisfaction > 85%"],
            "risks": ["Technical complexity", "Integration challenges"],
            "document_insights": ["BRD analysis was attempted but parsing failed"],
            "technical_requirements": {
                "performance": "Response time < 2 seconds",
                "security": "Authentication and authorization required",
                "scalability": "Support for concurrent users",
                "compatibility": "Cross-platform compatibility"
            },
            "compliance_requirements": [state.get("compliance_requirements", "Standard security practices")],
            "integration_requirements": ["API integration capabilities"]
        }

    state["prd_draft"] = prd
    state["step"] = "prd_generated"
    return state


def _generate_architecture(state: AgentState) -> AgentState:
    print("🏗️ Generating system architecture...")
    llm = get_llm()
    
    # Get IT context for architecture generation
    it_domain = state.get("it_domain", "")
    technology_stack = state.get("technology_stack", "")
    prd = state.get("prd_draft", {})
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a senior software architect. Generate a basic system architecture based on PRD requirements and IT context. Return only JSON."),
        (
            "human",
            (
                """
                Create a basic system architecture for:
                Project: {project_name}
                Feature: {feature_name}
                IT Domain: {it_domain}
                Technology Stack: {technology_stack}
                
                PRD Context:
                {prd_json}
                
                Return JSON with fields:
                ```json
                {{
                  "overview": "Architecture overview and approach",
                  "technology_stack": {{
                    "frontend": "...",
                    "backend": "...",
                    "database": "...",
                    "infrastructure": "..."
                  }},
                  "components": [
                    {{
                      "name": "Component Name",
                      "description": "Component description",
                      "technology": "Technology used",
                      "responsibility": "What it does"
                    }}
                  ],
                  "data_flow": "Description of how data flows through the system",
                  "deployment": "Deployment strategy and considerations"
                }}
                ```
                """
            ),
        ),
    ])
    
    prd_json = json.dumps(prd, indent=2)
    msg = (prompt | llm).invoke({
        "project_name": state["project_name"],
        "feature_name": state["feature_name"],
        "it_domain": it_domain,
        "technology_stack": technology_stack,
        "prd_json": prd_json
    })
    text = getattr(msg, "content", "").strip()
    
    try:
        if text.startswith("```json") and text.endswith("```"):
            text = text[7:-3]
        elif text.startswith("```") and text.endswith("```"):
            text = text[3:-3]
        architecture = json.loads(text)
    except Exception:
        architecture = {
            "overview": f"Basic architecture for {state['project_name']} - {state['feature_name']}",
            "technology_stack": {
                "frontend": "Web-based interface",
                "backend": "API server",
                "database": "Relational database",
                "infrastructure": "Cloud deployment"
            },
            "components": [
                {
                    "name": "Frontend",
                    "description": "User interface layer",
                    "technology": "Web technologies",
                    "responsibility": "Handle user interactions"
                },
                {
                    "name": "Backend API",
                    "description": "Business logic layer",
                    "technology": "Server-side framework",
                    "responsibility": "Process business logic and data"
                }
            ],
            "data_flow": "Data flows from frontend through API to database and back",
            "deployment": "Cloud-based deployment with scalability considerations"
        }
    
    state["architecture_draft"] = architecture
    state["step"] = "architecture_generated"
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
        "architecture": state["architecture_draft"],
        "frd": state["frd_draft"],
    }
    state["final_output"] = final_output
    state["step"] = "completed"
    return state


def _build_graph() -> StateGraph:
    workflow = StateGraph(AgentState)
    workflow.add_node("gather_requirements", _gather_requirements)
    workflow.add_node("generate_prd", _generate_prd)
    workflow.add_node("generate_architecture", _generate_architecture)
    workflow.add_node("generate_frd", _generate_frd)
    workflow.add_node("refine_and_validate", _refine_and_validate)
    workflow.add_node("finalize_output", _finalize_output)

    workflow.set_entry_point("gather_requirements")
    workflow.add_edge("gather_requirements", "generate_prd")
    workflow.add_edge("generate_prd", "generate_architecture")
    workflow.add_edge("generate_architecture", "generate_frd")
    workflow.add_edge("generate_frd", "refine_and_validate")
    workflow.add_edge("refine_and_validate", "finalize_output")
    workflow.add_edge("finalize_output", END)
    return workflow.compile()


def run_prd_frd(project_name: str = None, feature_name: str = None, industry: str = "", target_users: str = "", business_context: str = "", uploaded_documents: List[Dict[str, Any]] = None, it_domain: str = "", technology_stack: str = "", compliance_requirements: str = "") -> Dict[str, Any]:
    # Extract project details from BRD documents if not provided
    if uploaded_documents and (not project_name or not feature_name):
        print("📄 Extracting project details from uploaded BRD documents...")
        extracted_details = _analyze_brd_for_project_details(uploaded_documents)
        if not project_name:
            project_name = extracted_details["project_name"]
        if not feature_name:
            feature_name = extracted_details["feature_name"]
        print(f"✅ Extracted from BRD: {project_name} - {feature_name}")
    
    # Set defaults if still None
    if not project_name:
        project_name = "Unnamed Project"
    if not feature_name:
        feature_name = "Core Feature"
    
    graph = _build_graph()
    initial_state: AgentState = {
        "project_name": project_name,
        "feature_name": feature_name,
        "industry": industry,
        "target_users": target_users,
        "business_context": business_context,
        "uploaded_documents": uploaded_documents or [],
        "it_domain": it_domain,
        "technology_stack": technology_stack,
        "compliance_requirements": compliance_requirements,
        "messages": [],
        "prd_draft": {},
        "architecture_draft": {},
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

    # Check if we have uploaded documents to extract project details from
    uploaded_documents = req.get("uploaded_documents", [])
    
    project_name = req.get("projectName") or req.get("project")
    feature_name = req.get("featureName") or req.get("feature")
    
    # If we have uploaded documents and no project/feature names provided, or they are placeholders, extract from documents
    if uploaded_documents and (not project_name or not feature_name or 
                              project_name in ["Unnamed Project", "To Be Extracted", "BRD-Based Project"] or 
                              feature_name in ["Core Feature", "To Be Extracted", "BRD Analysis"]):
        print("📄 Extracting project details from uploaded BRD documents...")
        extracted_details = _analyze_brd_for_project_details(uploaded_documents)
        project_name = extracted_details["project_name"]
        feature_name = extracted_details["feature_name"]
        print(f"✅ Extracted from BRD: {project_name} - {feature_name}")
    
    # Fallback if still not set
    if not project_name:
        project_name = "Unnamed Project"
    if not feature_name:
        feature_name = "Core Feature"
    industry = req.get("industry", "")
    target_users = req.get("target_users", req.get("targetUsers", ""))
    business_context = req.get("business_context", req.get("context", ""))
    uploaded_documents = req.get("uploaded_documents", [])
    it_domain = req.get("it_domain", "")
    technology_stack = req.get("technology_stack", "")
    compliance_requirements = req.get("compliance_requirements", "")

    result = run_prd_frd(project_name, feature_name, industry, target_users, business_context, uploaded_documents, it_domain, technology_stack, compliance_requirements)
    return {"prd": result}
