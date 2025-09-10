import uvicorn
from fastapi import FastAPI
from graph.workflow import app as jira_graph_app,test_case_graph_app
from fastapi import FastAPI
from graph.resource_optimizer import run_workflow
from tools.gmail_utils import check_leave_mail

from schemas.models import JiraTask, ReallocationResult,InputRequirements, OutputArtifacts

app = FastAPI(
    title="Jira Resource Optimization Agent",
    description="Automates task reallocation and overdue notifications in Jira.",
    version="1.0.0",
)

@app.post("/optimize-resources")
async def optimize_resources():
    """
    Runs the workflow: leave mail → verification → fetch tasks → reallocation → notifications.
    """
    inputs = {"email_data": {}, "team_csv": []}  # Initial empty state
    final_state = jira_graph_app.invoke(inputs)
    return final_state

@app.get("/check-mail")
def check_mail_and_run():
    leave_email = check_leave_mail()
    if not leave_email:
        return {"status": "No leave mails found"}
    
    # Run workflow
    result = run_workflow(project_key="TEST", leave_email=leave_email)
    return result

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