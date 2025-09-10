import uvicorn
from pydantic import BaseModel
from schemas.models import InputRequirements, OutputArtifacts
from graph.workflow import app as test_case_graph_app, run_risk_workflow
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from typing import Dict
from tools.json_reader import classify_prd
from tools.web_search import search_duckduckgo

# Initialize the FastAPI app
app = FastAPI(
    title="QA Agent API",
    description="This agent receives PRD/FRD documents and generates comprehensive test cases.",
    version="2.0.0",
)

@app.post("/generate-test-cases") # No more response_model
async def generate_test_cases(request: Request):
class PRDRequest(BaseModel):
    prd_json: Dict

@app.post("/analyze-risk")
async def analyze_risk(request: Request):
    prd_json = await request.json()  # no fixed schema here
    sector, category, enriched_prd = classify_prd(prd_json)
    # Use the new DuckDuckGo search function
    search_results = search_duckduckgo(f"{sector} {category} employee engagement platform risks 2025")
    
    result = run_risk_workflow(enriched_prd, sector, category, search_results)
    return result

@app.post("/generate-test-cases", response_model=OutputArtifacts)
async def generate_test_cases(requirements: InputRequirements):
    """
    Receives any JSON document and returns an AI-generated, dynamically structured QA plan.
    """
    requirements_data = await request.json()
    
    inputs = {"requirements": requirements_data}
    
    final_state = test_case_graph_app.invoke(inputs)
    
    return final_state['artifacts']


# Uvicorn entry point
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)