import json
from langgraph.graph import StateGraph, END
from .state import GraphState
from agents.prd_frd_generator import run_prd_frd
from agents.risk_analysis_agent import analyze_risks
from agents.testcase_generator import generate_test_artifacts_node
from agents.task_execution_agent import TaskExecutionAgent
from tools.json_reader import classify_prd
from tools.web_search import search_duckduckgo
from schemas.models import OutputArtifacts, UserStoryInput
from config.settings import get_llm
from langchain_core.prompts import ChatPromptTemplate
from typing import Dict, Any
import os
from datetime import datetime
from .resource_optimizer import run_workflow as run_resource_optimizer

def prd_frd_generator_node(state: GraphState) -> Dict[str, Any]:
    """Generate PRD and FRD documents"""
    print("📋 Generating PRD and FRD...")
    
    result = run_prd_frd(
        project_name=state["project_name"],
        feature_name=state["feature_name"],
        industry=state.get("industry", ""),
        target_users=state.get("target_users", ""),
        business_context=state.get("business_context", "")
    )
    
    return {"prd_output": result}

def risk_analysis_node(state: GraphState) -> Dict[str, Any]:
    """Analyze risks based on PRD output"""
    print("⚠️ Analyzing risks...")
    
    prd_data = state["prd_output"]
    
    # Classify PRD for sector and category
    sector, category, enriched_prd = classify_prd(prd_data)
    
    # Search for relevant risk information
    search_query = f"{sector} {category} {state['feature_name']} risks 2025"
    search_results = search_duckduckgo(search_query)
    
    # Analyze risks
    thinking, risks = analyze_risks(enriched_prd, search_results)
    
    return {
        "risk_analysis": risks,
        "risk_thinking": thinking
    }

def test_case_generator_node(state: GraphState) -> Dict[str, Any]:
    """Generate test cases based on PRD output"""
    print("🧪 Generating test cases...")
    
    # Prepare requirements for test case generator
    requirements = {
        "projectName": state["project_name"],
        "featureName": state["feature_name"],
        "prd": state["prd_output"]["prd"],
        "frd": state["prd_output"]["frd"]
    }
    
    # Create a temporary state for the test case generator
    temp_state = {"requirements": requirements}
    
    # Generate test artifacts
    result = generate_test_artifacts_node(temp_state)
    
    return {"test_artifacts": result["artifacts"]}

def task_execution_node(state: GraphState) -> Dict[str, Any]:
    """Execute task decomposition, prioritization, and Jira setup"""
    print("⚙️ Executing task decomposition and Jira setup...")
    
    # Prepare user stories input for task execution
    user_stories_data = {
        "userStories": state["test_artifacts"].get("userStories", [])
    }
    
    # Resolve project name for Jira: prefer Agent1 project_name, fallback to PRD output or a safe default
    project_name = (
        state.get('project_name')
        or (state.get('prd_output') or {}).get('projectName')
        or "IT Planning Project"
    )
    
    try:
        # Create task execution agent with resolved project name (deterministic key ensures reuse)
        # Limited to 5 Jira tasks for faster processing and showcasing
        task_agent = TaskExecutionAgent(
            user_stories=user_stories_data,
            project_name=project_name,
            project_prefix="TP",
            lead_email="jeba.m.ihub@snsgroups.com",
            max_jira_tasks=5  # Limit for faster processing
        )
        
        # Execute deterministic pipeline to ensure Jira artifacts are created
        execution_result = task_agent.run_pipeline()
        
        return {"task_execution_output": {"result": execution_result, "status": "completed"}}
        
    except Exception as e:
        print(f"❌ Error in task execution: {str(e)}")
        return {"task_execution_output": {"result": f"Error: {str(e)}", "status": "failed"}}

def resource_optimization_node(state: GraphState) -> Dict[str, Any]:
    """Run resource optimization after Jira setup."""
    print("🧠 Running resource optimization...")
    # Derive project_key from task execution output (deterministic generation used there)
    project_key = None
    try:
        project_key = state.get("task_execution_output", {}).get("result", {}).get("project_key")
    except Exception:
        project_key = None
    if not project_key:
        return {"resource_optimization": {"status": "skipped (no project key)"}}

    # Leave email source (interactive via Gmail OAuth)
    try:
        from tools.gmail_utils import check_leave_mail
        leave_email = state.get("leave_email") or check_leave_mail()
    except Exception:
        leave_email = state.get("leave_email")
    if not leave_email:
        return {"resource_optimization": {"status": "no leave mails found"}}

    result = run_resource_optimizer(project_key=project_key, leave_email=leave_email)
    return {"resource_optimization": result}

def markdown_generator_node(state: GraphState) -> Dict[str, Any]:
    """Generate markdown file with all outputs"""
    print("📄 Generating markdown output...")
    
    # Create markdown content
    markdown_content = f"""# Project Documentation: {state['project_name']}

## Feature: {state['feature_name']}

**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 1. Product Requirements Document (PRD)

### Overview
{state['prd_output']['prd'].get('overview', 'N/A')}

### Personas
"""
    
    # Add personas
    for persona in state['prd_output']['prd'].get('personas', []):
        markdown_content += f"- **{persona.get('name', 'Unknown')}**: {', '.join(persona.get('goals', []))}\n"
    
    markdown_content += f"""
### Business Goals
"""
    for goal in state['prd_output']['prd'].get('business_goals', []):
        markdown_content += f"- {goal}\n"
    
    markdown_content += f"""
### Success Metrics
"""
    for metric in state['prd_output']['prd'].get('success_metrics', []):
        markdown_content += f"- {metric}\n"

    markdown_content += f"""
### Identified Risks
"""
    for risk in state['prd_output']['prd'].get('risks', []):
        markdown_content += f"- {risk}\n"

    markdown_content += f"""
---

## 2. Functional Requirements Document (FRD)

"""
    
    # Add FRD items
    for i, frd_item in enumerate(state['prd_output']['frd'], 1):
        markdown_content += f"""### {frd_item.get('id', f'FR-{i}')}: {frd_item.get('title', 'Untitled')}

**Description:** {frd_item.get('description', 'N/A')}

**Priority:** {frd_item.get('priority', 'N/A')}

**Acceptance Criteria:**
"""
        for criteria in frd_item.get('acceptanceCriteria', []):
            markdown_content += f"- {criteria}\n"
        markdown_content += "\n"

    markdown_content += f"""
---

## 3. Risk Analysis

### Analysis Summary
{state.get('risk_thinking', 'No analysis available')}

### Identified Risks
"""
    
    # Add risk analysis
    for i, risk in enumerate(state.get('risk_analysis', []), 1):
        markdown_content += f"""#### Risk {i}: {risk.get('risk_type', 'Unknown Risk Type')}

- **Severity:** {risk.get('severity', 'Unknown')}
- **Description:** {risk.get('description', 'No description available')}
- **Relevant Law:** {risk.get('law', 'N/A')}

"""

    markdown_content += f"""
---

## 4. Test Cases

### User Stories
"""
    
    # Add user stories and test cases
    for story in state.get('test_artifacts', {}).get('userStories', []):
        markdown_content += f"""#### {story.get('storyId', 'Unknown ID')}: {story.get('description', 'No description')}

**Test Cases:**
"""
        for test_case in story.get('testCases', []):
            markdown_content += f"""##### {test_case.get('testCaseId', 'Unknown ID')}: {test_case.get('description', 'No description')}

- **Type:** {test_case.get('type', 'Unknown')}
- **Steps:**
"""
            for step in test_case.get('steps', []):
                markdown_content += f"  1. {step}\n"
            markdown_content += f"- **Expected Result:** {test_case.get('expectedResult', 'N/A')}\n\n"

    markdown_content += f"""
---

## 5. Task Execution & Sprint Planning

### Project: {state['project_name']} - {state['feature_name']}

### Task Decomposition and Prioritization
{state.get('task_execution_output', {}).get('result', 'Task execution not completed')}

### Sprint Planning Summary
The task execution agent has processed the user stories and created:
- Decomposed tasks with detailed breakdowns
- Task prioritization based on business value and dependencies
- Role mapping to team members
- Sprint planning with capacity calculations
- Jira project setup with issues and subtasks for **{state['project_name']} - {state['feature_name']}**

---

## 6. Summary

This document contains the complete analysis for the **{state['project_name']}** project, specifically the **{state['feature_name']}** feature. The analysis includes:

1. **Product Requirements Document (PRD)** - Defines the product vision, personas, and business goals
2. **Functional Requirements Document (FRD)** - Details the specific functional requirements
3. **Risk Analysis** - Identifies potential risks and their mitigation strategies
4. **Test Cases** - Comprehensive test scenarios for quality assurance
5. **Task Execution** - Decomposed tasks, sprint planning, and Jira project setup

All outputs have been generated using AI-powered analysis and should be reviewed by the development team before implementation.

---

*Generated by IT Planning Workflow System*
"""
    
    # Save markdown file
    filename = f"{state['project_name'].replace(' ', '_')}_{state['feature_name'].replace(' ', '_')}_documentation.md"
    filepath = os.path.join(os.getcwd(), filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"📄 Markdown file saved: {filepath}")
    
    return {
        "final_output": {
            "markdown_file": filepath,
            "prd_output": state["prd_output"],
            "risk_analysis": state["risk_analysis"],
            "test_artifacts": state["test_artifacts"],
            "task_execution": state.get("task_execution_output", {}),
            "resource_optimization": state.get("resource_optimization", {}),
            "summary": {
                "project_name": state["project_name"],
                "feature_name": state["feature_name"],
                "total_risks": len(state.get("risk_analysis", [])),
                "total_user_stories": len(state.get("test_artifacts", {}).get("userStories", [])),
                "total_test_cases": sum(len(story.get("testCases", [])) for story in state.get("test_artifacts", {}).get("userStories", [])),
                "task_execution_status": state.get("task_execution_output", {}).get("status", "not_started")
            }
        }
    }

def create_unified_workflow() -> StateGraph:
    """Create the unified workflow that chains all four agents"""
    workflow = StateGraph(GraphState)
    
    # Add nodes
    workflow.add_node("prd_frd_generator", prd_frd_generator_node)
    workflow.add_node("risk_analysis", risk_analysis_node)
    workflow.add_node("test_case_generator", test_case_generator_node)
    workflow.add_node("task_execution", task_execution_node)
    workflow.add_node("markdown_generator", markdown_generator_node)
    workflow.add_node("resource_optimization", resource_optimization_node)
    
    # Define the flow - sequential to ensure all data is available
    workflow.set_entry_point("prd_frd_generator")
    workflow.add_edge("prd_frd_generator", "risk_analysis")
    workflow.add_edge("risk_analysis", "test_case_generator")
    workflow.add_edge("test_case_generator", "task_execution")
    workflow.add_edge("task_execution", "resource_optimization")
    workflow.add_edge("resource_optimization", "markdown_generator")
    workflow.add_edge("markdown_generator", END)
    
    return workflow.compile()

def run_unified_workflow(
    project_name: str,
    feature_name: str,
    industry: str = "",
    target_users: str = "",
    business_context: str = ""
) -> Dict[str, Any]:
    """Run the complete unified workflow"""
    workflow = create_unified_workflow()
    
    initial_state: GraphState = {
        "project_name": project_name,
        "feature_name": feature_name,
        "industry": industry,
        "target_users": target_users,
        "business_context": business_context,
        "prd_output": {},
        "risk_analysis": [],
        "risk_thinking": "",
        "test_artifacts": {},
        "task_execution_output": {},
        "resource_optimization": {},
        "final_output": {}
    }
    
    final_state = workflow.invoke(initial_state)
    return final_state["final_output"]
