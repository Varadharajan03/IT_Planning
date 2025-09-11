import uvicorn
from pydantic import BaseModel
from schemas.models import InputRequirements, OutputArtifacts
from graph.workflow import app as test_case_graph_app, run_risk_workflow
from graph.unified_workflow import run_unified_workflow
from graph.resource_optimizer import run_workflow as run_resource_optimizer
from tools.gmail_utils import check_leave_mail
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from typing import Dict, Optional
from tools.json_reader import classify_prd
from tools.web_search import search_duckduckgo

# Initialize the FastAPI app
app = FastAPI(
    title="IT Planning Workflow API",
    description="Unified workflow for PRD/FRD generation, risk analysis, test case generation, task execution with Jira, and resource optimization.",
    version="4.1.0",
)

class PRDRequest(BaseModel):
    prd_json: Dict

class UnifiedWorkflowRequest(BaseModel):
    project_name: str
    feature_name: str
    industry: Optional[str] = ""
    target_users: Optional[str] = ""
    business_context: Optional[str] = ""

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "IT Planning Workflow API",
        "version": "4.1.0",
        "endpoints": {
            "unified_workflow": "/unified-workflow",
            "resource_optimizer_gmail": "/resource-optimizer-gmail"
        }
    }

@app.post("/unified-workflow")
async def unified_workflow(request: UnifiedWorkflowRequest):
    """
    Complete workflow: PRD/FRD Generation → Risk Analysis → Test Case Generation → Task Execution → Markdown Output -> Resource Optimization
    """
    try:
        result = run_unified_workflow(
            project_name=request.project_name,
            feature_name=request.feature_name,
            industry=request.industry,
            target_users=request.target_users,
            business_context=request.business_context
        )
        return {
            "success": True,
            "message": "Unified workflow completed successfully",
            "data": result
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error in unified workflow: {str(e)}",
            "data": None
        }

@app.post("/resource-optimizer-gmail")
async def resource_optimizer_gmail(payload: Dict[str, str]):
    """
    Gmail/OAuth-enabled Resource Optimizer runner.
    Expected JSON:
    {"project_key": "EPS"}
    It will open a Google OAuth consent flow to fetch the leave email.
    """
    project_key = payload.get("project_key")
    if not project_key:
        return {"success": False, "message": "project_key is required"}
    try:
        leave_email = check_leave_mail()
        if not leave_email:
            return {"success": False, "message": "No leave mails found"}
        result = run_resource_optimizer(project_key=project_key, leave_email=leave_email)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "message": str(e)}




# Uvicorn entry point
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)