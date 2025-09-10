import json
import re
import logging
from datetime import datetime, timedelta
from google import genai
from pydantic import ValidationError
from config.settings import get_llm
from schemas.models import TaskDecompositionOutput, TaskPrioritizationOutput
from prompts.sprint_architect_prompts import TASK_DECOMPOSITION_PROMPT, PRIORITIZATION_PROMPT
from tools.jira_client import jira  
import traceback 

# -------------------
# Logging setup
# -------------------
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# -------------------
# Gemini Setup
# -------------------
API_KEY = "AIzaSyA-Pil9BUWhdyNzQsfIHfLC5Qz3o-02M3Q"
client = genai.Client(api_key=API_KEY)

# -------------------
# Employee Role DB
# -------------------
employees = [
    {"name": "Kishor", "email": "kishor.r.ihub@snsgroups.com", "role": "Backend"},
    {"name": "Pradeep", "email": "pradeep.s.ihub@snsgroups.com", "role": "Fullstack"},
    {"name": "Srivarshini", "email": "srivarshini.r.ihub@snsgroups.com", "role": "Frontend"},
    {"name": "Jeba", "email": "jeba.m.ihub@snsgroups.com", "role": "DevOps"},
    {"name": "Rohit", "email": "rohit.a.ihub@snsgroups.com", "role": "QA"}
]

# -------------------
# JSON Cleaning
# -------------------
import re
import json

def clean_json_output(raw_output: str) -> str:
    """
    Clean raw LLM output to produce valid JSON.
    """
    if not raw_output:
        return "{}"

    cleaned = re.sub(r"```(json)?", "", raw_output)
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1:
        return "{}"
    cleaned = cleaned[start:end+1]

    cleaned = cleaned.replace(""", '"').replace(""", '"')
    def replace_inner_single_quotes(match):
        text = match.group(0)
        return text.replace("\\'", "'").replace("'", "'")  

    cleaned = re.sub(r'".*?"', replace_inner_single_quotes, cleaned)
    cleaned = re.sub(r",\s*([}\]])", r"\1", cleaned)

    return cleaned.strip()

# -------------------
# Task Decomposition
# -------------------
def task_decomposition_gemini(user_stories_json, llm):
    input_str = json.dumps(user_stories_json, separators=(",", ":"))
    prompt = TASK_DECOMPOSITION_PROMPT.format(input_str=input_str)

    response = llm.invoke([{"role": "user", "content": prompt}])
    raw_output = response.content.strip()

    logging.info("Raw Gemini output for task decomposition:\n%s", raw_output)

    if not raw_output:
        logging.error("Empty response from Gemini for decomposition.")
        return None

    try:
        cleaned_output = clean_json_output(raw_output)
        logging.info("Cleaned JSON:\n%s", cleaned_output)
        tasks_json = json.loads(cleaned_output)
        validated = TaskDecompositionOutput(**tasks_json)
        return validated.model_dump()
    except json.JSONDecodeError as e:
        logging.error("JSON parsing error: %s", e)
        return None
    except ValidationError as e:
        logging.error("Schema validation error: %s", e)
        return None

# -------------------
# Task Prioritization
# -------------------
def prioritize_tasks_gemini(tasks_json, llm):
    input_str = json.dumps(tasks_json, separators=(",", ":"))
    prompt = PRIORITIZATION_PROMPT.format(tasks_json=input_str)

    response = llm.invoke([{"role": "user", "content": prompt}])
    raw_output = response.content.strip()

    if not raw_output:
        logging.error("Empty response from Gemini for prioritization.")
        return None

    try:
        cleaned_output = clean_json_output(raw_output)
        prioritized_json = json.loads(cleaned_output)
        validated = TaskPrioritizationOutput(**prioritized_json)
        return validated.model_dump()
    except json.JSONDecodeError as e:
        logging.error("JSON parsing error during prioritization: %s", e)
        return None
    except ValidationError as e:
        logging.error("Schema validation error during prioritization: %s", e)
        return None

# -------------------
# Role Mapping
# -------------------
def map_roles(tasks_json, employees):
    role_map = {e["role"].lower(): e for e in employees}

    for task in tasks_json.get("tasks", []):
        task_type_key = task["type"].lower()
        task["assignee"] = role_map.get(task_type_key)

        for sub in task.get("subtasks", []):
            sub_type_key = sub["type"].lower()
            sub["assignee"] = role_map.get(sub_type_key)

    return tasks_json

# -------------------
# Sprint Planning
# -------------------
def calculate_sprints(tasks_json, hours_per_day=8, sprint_days=5):
    sprint_capacity = {e["name"]: hours_per_day * sprint_days for e in employees}
    first_sprint_tasks = []
    remaining_capacity = sprint_capacity.copy()

    for task in tasks_json.get("tasks", []):
        task_hours = task.get("estimated_hours", 0)
        assignee = task.get("assignee", {}).get("name", employees[0]["name"])

        if task_hours <= remaining_capacity[assignee]:
            first_sprint_tasks.append(task)
            remaining_capacity[assignee] -= task_hours
        else:
            break

    total_task_hours = sum(task.get("estimated_hours", 0) for task in tasks_json.get("tasks", []))
    total_capacity_per_sprint = sum(sprint_capacity.values())
    total_sprints = -(-total_task_hours // total_capacity_per_sprint)

    return {
        "first_sprint_tasks": first_sprint_tasks,
        "total_sprints_required": int(total_sprints)
    }

# -------------------
# Jira Integration 
# -------------------
def setup_jira_project_safely(project_key: str, project_name: str, lead_email: str):
    """Safely set up Jira project with fallbacks"""
    project = None
    jira_filter = None
    board = None
    
    if not jira.test_connection():
        logging.error("Failed to connect to Jira. Check your credentials and URL.")
        return None, None, None
    
    try:
        logging.info(f"Getting Jira account ID for lead: {lead_email}")
        lead_account_id = jira.get_account_id_by_email(lead_email)
        logging.info(f"Lead account ID: {lead_account_id}")
    except Exception as e:
        logging.error(f"Error getting lead account ID: {e}")
        return None, None, None
    
    try:
        logging.info(f"Creating/Getting Jira project: {project_name}")
        project = jira.create_project(key=project_key, name=project_name, lead_account_id=lead_account_id)
        logging.info(f"Project ready: {project.get('key', project_key)}")
    except Exception as e:
        logging.error(f"Error with project setup: {e}")
        try:
            if jira.project_exists(project_key):
                logging.info(f"Project {project_key} already exists, using existing project")
                import requests
                url = f"{jira.base_url}/rest/api/3/project/{project_key}"
                response = requests.get(url, auth=jira.auth, headers=jira.headers)
                project = response.json()
            else:
                return None, None, None
        except:
            return None, None, None
    
    try:
        jql = f'project = "{project["key"]}" ORDER BY priority DESC'
        logging.info(f"Creating Jira filter with JQL: {jql}")
        jira_filter = jira.create_filter(
            name=f"{project_key} Filter",
            jql=jql,
            description="Auto-generated filter for sprint tasks"
        )
        logging.info(f"Filter created with ID: {jira_filter['id']}")
    except Exception as e:
        logging.error(f"Error creating filter: {e}")
        return project, None, None
    
    try:
        existing_boards = jira.get_boards(project_key)
        if existing_boards.get("values"):
            board = existing_boards["values"][0]
            logging.info(f"Using existing board: {board['name']} (ID: {board['id']})")
        else:
            board_name = f"{project_key} Scrum Board"
            logging.info(f"Creating Jira board: {board_name} using filter ID: {jira_filter['id']}")
            board = jira.create_board(name=board_name, filter_id=jira_filter["id"])
            logging.info(f"Board created with ID: {board['id']}")
    except Exception as e:
        logging.error(f"Error creating board: {e}")
        return project, jira_filter, None
    
    return project, jira_filter, board

def create_jira_sprint_safely(board, sprint_name="Sprint 1"):
    """Safely create a sprint"""
    if not board:
        logging.warning("No board available, skipping sprint creation")
        return None
    
    try:
        logging.info(f"Creating Sprint '{sprint_name}' on board ID {board['id']}")
        sprint = jira.create_sprint(
            name=sprint_name,
            board_id=board["id"]
        )
        logging.info(f"Sprint created with ID: {sprint['id']}")
        return sprint
    except Exception as e:
        logging.error(f"Error creating sprint: {e}")
        return None

# -------------------
# Main Run
# -------------------

if __name__ == "__main__":
    llm_client = get_llm()
    sprint_plan = None

    test_cases_input = {
        "userStories": [
            {
                "storyId": "US-1",
                "description": "As a registered user, I want to view my profile information.",
                "testCases": [
                    {
                        "testCaseId": "TC-001",
                        "description": "Verify full name display",
                        "steps": [
                            "Log in as a registered user.",
                            "Navigate to the user profile page.",
                            "Observe the displayed full name."
                        ],
                        "expectedResult": "The displayed full name matches the name stored in the database.",
                        "type": "Positive"
                    }
                ]
            }
        ]
    }

    logging.info("🔹 Starting Task Decomposition")
    decomposed_tasks = task_decomposition_gemini(test_cases_input, llm_client)
    if decomposed_tasks:
        logging.info("✅ Step 1: Task Decomposition completed")
    else:
        logging.error("❌ Task decomposition failed, cannot continue.")
        exit(1)

    logging.info("🔹 Starting Task Prioritization")
    prioritized_tasks = prioritize_tasks_gemini(decomposed_tasks, llm_client)
    if prioritized_tasks:
        logging.info("✅ Step 2: Task Prioritization completed")
    else:
        logging.error("❌ Prioritization failed, cannot continue.")
        exit(1)

    logging.info("🔹 Mapping Roles")
    mapped_tasks = map_roles(prioritized_tasks, employees)
    logging.info("✅ Step 3: Role Mapping completed")

    logging.info("🔹 Calculating Sprints")
    sprint_plan = calculate_sprints(mapped_tasks, hours_per_day=8, sprint_days=6)
    logging.info(f"✅ Step 4: Sprint Planning completed")
    logging.info(f"Total sprints required: {sprint_plan['total_sprints_required']}")
    logging.info(f"First sprint tasks: {len(sprint_plan['first_sprint_tasks'])}")

    if sprint_plan and sprint_plan.get("first_sprint_tasks"):
        logging.info("✅ Step 5: Jira Automation starting...")

        project_key = f"TP{datetime.now().strftime('%m%d')}" 
        project_name = f"Task Planning Project {datetime.now().strftime('%Y-%m-%d')}"
        lead_email = "jeba.m.ihub@snsgroups.com"

        project, jira_filter, board = setup_jira_project_safely(project_key, project_name, lead_email)

        if not project:
            logging.error("❌ Failed to create/access Jira project. Stopping automation.")
            exit(1)

        logging.info("🔹 Checking available issue types...")
        available_issue_types = jira.get_project_issue_types(project["key"])
        if not available_issue_types:
            logging.error("❌ No issue types available for project. Cannot create issues.")
            exit(1)

        sprint = create_jira_sprint_safely(board) if board else None
        created_issue_keys = []

        logging.info("🔹 Creating Jira issues and subtasks...")
        for i, task in enumerate(sprint_plan["first_sprint_tasks"], start=1):
            try:
                assignee_email = task.get("assignee", {}).get("email")
                assignee_id = None
                if assignee_email:
                    try:
                        assignee_id = jira.get_account_id_by_email(assignee_email)
                        logging.info(f"Assignee resolved: {assignee_email} -> {assignee_id}")
                    except Exception as e:
                        logging.warning(f"⚠️ Could not resolve assignee for {assignee_email}: {e}")

                logging.info(f"📌 Creating issue {i}: {task['summary']}")
                
                issue = jira.create_issue_with_auto_type(
                    project_key=project["key"],
                    summary=task["summary"],
                    description=task.get("description", ""),
                    assignee_id=assignee_id,
                    preferred_types=['Story', 'Task', 'User Story', 'Feature']
                )
                
                if not issue:
                    logging.error(f"❌ Failed to create issue: {task['summary']}")
                    continue
                    
                logging.info(f"✅ Issue created: {issue['key']}")
                created_issue_keys.append(issue['key'])

                for j, sub in enumerate(task.get("subtasks", []), start=1):
                    try:
                        sub_assignee_email = sub.get("assignee", {}).get("email")
                        sub_assignee_id = None
                        if sub_assignee_email:
                            try:
                                sub_assignee_id = jira.get_account_id_by_email(sub_assignee_email)
                            except Exception as e:
                                logging.warning(f"⚠️ Could not resolve subtask assignee: {e}")

                        logging.info(f"   ↳ Creating subtask {j} for {issue['key']}: {sub['summary']}")
                        
                        sub_issue = jira.create_issue_with_auto_type(
                            project_key=project["key"],
                            summary=sub["summary"],
                            description=sub.get("description", ""),
                            assignee_id=sub_assignee_id,
                            parent_key=issue["key"],
                            preferred_types=['Sub-task', 'Subtask', 'Sub Task']
                        )
                        
                        if sub_issue:
                            logging.info(f"   ✅ Subtask created: {sub_issue['key']}")
                            created_issue_keys.append(sub_issue['key'])
                        else:
                            logging.error(f"   ❌ Failed to create subtask: {sub['summary']}")

                    except Exception as e:
                        logging.error(f"❌ Failed to create subtask '{sub['summary']}': {e}")
                        logging.error(traceback.format_exc())

            except Exception as e:
                logging.error(f"❌ Failed to create issue '{task['summary']}': {e}")
                logging.error(traceback.format_exc())
                continue

        if sprint and created_issue_keys:
            try:
                logging.info(f"📌 Moving {len(created_issue_keys)} issues into sprint {sprint['id']}...")
                jira.move_issue_to_sprint(sprint["id"], created_issue_keys)
                logging.info("✅ All issues moved into sprint successfully!")
            except Exception as e:
                logging.warning(f"⚠️ Could not move issues into sprint: {e}")

        logging.info("✅ Jira automation completed!")
        logging.info(f"🔗 Project URL: {jira.base_url}/projects/{project['key']}")
        if board:
            logging.info(f"🔗 Board URL: {jira.base_url}/jira/software/projects/{project['key']}/boards/{board['id']}")
        if sprint:
            logging.info(f"🔗 Sprint URL: {jira.base_url}/jira/software/projects/{project['key']}/boards/{board['id']}/backlog")

    else:
        logging.warning("⚠️ No tasks available for Jira automation. Skipping issue creation.")