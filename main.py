import uvicorn
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from graph.workflow import app as test_case_graph_app

# Load environment variables
load_dotenv()

# Initialize the FastAPI app
app = FastAPI(
    title="Fully Flexible QA Agent API",
    description="This agent receives any PRD/FRD JSON, analyzes it, and returns a dynamically structured QA plan.",
    version="4.0.0",
)

@app.post("/generate-test-cases") # No more response_model
async def generate_test_cases(request: Request):
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