import uvicorn
from fastapi import FastAPI
from graph.workflow import app as jira_graph_app
from fastapi import FastAPI
from graph.resource_optimizer import run_workflow
from tools.gmail_utils import check_leave_mail

from schemas.models import JiraTask, ReallocationResult

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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
