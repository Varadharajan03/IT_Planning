import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv
from schemas.models import InputRequirements, OutputArtifacts
from graph.workflow import app as test_case_graph_app

# Initialize the FastAPI app
app = FastAPI(
    title="QA Agent API",
    description="This agent receives PRD/FRD documents and generates comprehensive test cases.",
    version="2.0.0",
)

@app.post("/generate-test-cases", response_model=OutputArtifacts)
async def generate_test_cases(requirements: InputRequirements):
    """
    Receives project requirements and returns AI-generated user stories and test cases.
    """
    inputs = {"requirements": requirements.dict()}
    
    final_state = test_case_graph_app.invoke(inputs)
    
    return final_state['artifacts']

# Uvicorn entry point
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

