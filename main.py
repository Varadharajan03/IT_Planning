import uvicorn
from pydantic import BaseModel
from schemas.models import InputRequirements, OutputArtifacts
from graph.workflow import app as test_case_graph_app, run_risk_workflow
from graph.unified_workflow import run_unified_workflow
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from typing import Dict, Optional
from tools.json_reader import classify_prd
from tools.web_search import search_duckduckgo

# Initialize the FastAPI app
app = FastAPI(
    title="IT Planning Workflow API",
    description="Unified workflow for PRD/FRD generation, risk analysis, test case generation, and task execution with Jira integration.",
    version="4.0.0",
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
        "version": "3.0.0",
        "endpoints": {
            "unified_workflow": "/unified-workflow",
            "analyze_risk": "/analyze-risk", 
            "generate_test_cases": "/generate-test-cases"
        }
    }

@app.post("/unified-workflow")
async def unified_workflow(request: UnifiedWorkflowRequest):
    """
    Complete workflow: PRD/FRD Generation → Risk Analysis → Test Case Generation → Task Execution → Markdown Output
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

@app.post("/analyze-risk")
async def analyze_risk(request: Request):
    """Legacy endpoint for risk analysis only"""
    prd_json = await request.json()  # no fixed schema here
    sector, category, enriched_prd = classify_prd(prd_json)
    # Use the new DuckDuckGo search function
    search_results = search_duckduckgo(f"{sector} {category} employee engagement platform risks 2025")
    
    result = run_risk_workflow(enriched_prd, sector, category, search_results)
    return result

@app.post("/generate-test-cases", response_model=OutputArtifacts)
async def generate_test_cases(requirements: InputRequirements):
    """
    Legacy endpoint for test case generation only
    """
    inputs = {"requirements": requirements.dict()}
    
    final_state = test_case_graph_app.invoke(inputs)
    
    return final_state['artifacts']


# Uvicorn entry point
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)