import json
import re
import logging
from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel, Field, ValidationError
from langchain_core.tools import tool
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, SystemMessage
from config.settings import get_llm
from prompts.sprint_architect_prompts import TASK_DECOMPOSITION_PROMPT, PRIORITIZATION_PROMPT
from tools.jira_client import jira
import traceback
import requests
import time
from schemas.models import UserStoryInput, TaskDecompositionOutputModel, TaskPrioritizationOutputModel, SprintPlanningOutput, JiraProjectInput, JiraProjectOutput, JiraSprintOutput

# -------------------
# Logging setup
# -------------------
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

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

class TaskExecutionAgent:
    def __init__(self, user_stories, project_prefix="TP", lead_email="jeba.m.ihub@snsgroups.com"):
        self.user_stories = user_stories
        self.project_prefix = project_prefix
        self.lead_email = lead_email
        self.project_key = f"{project_prefix}{datetime.now().strftime('%m%d')}"
        self.project_name = f"Task Planning Project {datetime.now().strftime('%Y-%m-%d')}"

    def task_execution(self):
        """
        Process task execution through task decomposition, prioritization,
        role mapping, sprint planning, and Jira setup.
        """
        try:
            response = agent_executor.invoke({
                "messages": [
                    HumanMessage(content=f"""
                    Process the following user stories through task decomposition, prioritization, 
                    role mapping, sprint planning, and Jira setup:
                    {json.dumps(self.user_stories, indent=2)}
                    
                    For Jira setup, use:
                    - Project key: {self.project_key}
                    - Project name: {self.project_name}
                    - Lead email: {self.lead_email}
                    """)
                ]
            })
            return response.get("output")
        except Exception as e:
            logging.error(f"Unexpected error during execution: {e}")
            return f"An error occurred: {e}"

# -------------------
# JSON Cleaning Tool
# -------------------
@tool
def clean_json_tool(raw_output: str) -> str:
    """
    Cleans and validates JSON output from LLM responses, fixing common issues like code block markers,
    single quotes, escaped quotes, trailing commas, and unescaped newlines in strings.

    Args:
        raw_output: Raw string output from LLM, potentially containing JSON.

    Returns:
        A string containing valid, cleaned JSON or an empty JSON object "{}" if parsing fails.
    """
    if not raw_output:
        logging.warning("Empty raw output received for JSON cleaning")
        return "{}"

    cleaned = re.sub(r"```(json)?", "", raw_output).strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1:
        logging.error("No valid JSON object found in raw output")
        return "{}"
    
    cleaned = cleaned[start:end+1]
    cleaned = cleaned.replace("'", '"')
    cleaned = re.sub(r'"([^"]*)\\"s"', r'"\1\'s"', cleaned)
    cleaned = re.sub(r",\s*([}\]])", r"\1", cleaned)
    cleaned = re.sub(r'(\n|\r\n)\s*', ' ', cleaned)
    cleaned = re.sub(r'"\s*([^"]*?)\s*\n\s*([^"]*?)"', r'"\1 \2"', cleaned)
    
    try:
        parsed = json.loads(cleaned)
        logging.info("Successfully cleaned and parsed JSON")
        return json.dumps(parsed, separators=(",", ":"))
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse cleaned JSON: {e}\nRaw input: {cleaned}")
        cleaned = re.sub(r'\\(["\\])', r'\1', cleaned)
        try:
            parsed = json.loads(cleaned)
            logging.info("Successfully parsed JSON after removing problematic escapes")
            return json.dumps(parsed, separators=(",", ":"))
        except json.JSONDecodeError as e:
            logging.error(f"Secondary cleaning failed: {e}\nRaw input: {cleaned}")
            return "{}"

# -------------------
# LLM-Based JSON Fixer Tool
# -------------------
@tool
def fix_json_with_llm_tool(raw_output: str) -> str:
    """
    Uses the LLM to fix invalid JSON output by prompting it to correct the JSON structure.
    
    Args:
        raw_output: Raw string output that is invalid JSON.

    Returns:
        A string containing valid JSON or an empty JSON object "{}" if fixing fails.
    """
    llm_client = get_llm()
    prompt = f"""
    The following is an invalid JSON string:
    {raw_output}

    Please fix it to make it valid JSON. Remove any code block markers (e.g., ```json or ```) and output only the valid JSON string.
    If it cannot be fixed, output {{}}.
    """
    try:
        response = llm_client.invoke([{"role": "user", "content": prompt}])
        fixed_output = response.content.strip()
        fixed_output = re.sub(r"```(json)?", "", fixed_output).strip()
        parsed = json.loads(fixed_output)
        logging.info("Successfully fixed JSON with LLM")
        return json.dumps(parsed, separators=(",", ":"))
    except (json.JSONDecodeError, Exception) as e:
        logging.error(f"LLM failed to fix JSON: {e}\nFixed output: {fixed_output}")
        return "{}"

# -------------------
# LangChain Tools
# -------------------
@tool
def task_decomposition_tool(user_stories: UserStoryInput) -> TaskDecompositionOutputModel:
    """
    Decomposes user stories into tasks using Gemini LLM.
    
    Args:
        user_stories: UserStoryInput containing user stories with test cases.
    
    Returns:
        TaskDecompositionOutputModel with decomposed tasks.
    """
    llm_client = get_llm()
    input_str = json.dumps(user_stories.model_dump(), separators=(",", ":"))
    prompt = TASK_DECOMPOSITION_PROMPT.format(input_str=input_str)

    try:
        response = llm_client.invoke([{"role": "user", "content": prompt}])
        raw_output = response.content.strip()
        logging.info("Raw Gemini output for task decomposition:\n%s", raw_output)

        if not raw_output:
            logging.error("Empty response from Gemini for decomposition.")
            return TaskDecompositionOutputModel(tasks=[])

        cleaned_output = clean_json_tool.invoke(raw_output)
        if cleaned_output == "{}":
            logging.warning("Initial JSON cleaning failed, attempting LLM-based fix")
            cleaned_output = fix_json_with_llm_tool.invoke(raw_output)
        
        logging.info("Cleaned JSON:\n%s", cleaned_output)
        tasks_json = json.loads(cleaned_output)
        validated = TaskDecompositionOutputModel(**tasks_json)
        return TaskDecompositionOutputModel(tasks=validated.model_dump().get("tasks", []))
    except (json.JSONDecodeError, ValidationError) as e:
        logging.error("Error in task decomposition: %s\nRaw output: %s", e, raw_output)
        try:
            raw_json = json.loads(re.sub(r"```(json)?", "", raw_output).strip())
            validated = TaskDecompositionOutputModel(**raw_json)
            logging.info("Successfully used raw JSON as fallback")
            return TaskDecompositionOutputModel(tasks=validated.model_dump().get("tasks", []))
        except (json.JSONDecodeError, ValidationError) as e:
            logging.error("Fallback raw JSON parsing failed: %s", e)
            return TaskDecompositionOutputModel(tasks=[])

@tool
def prioritize_tasks_tool(tasks: TaskDecompositionOutputModel) -> TaskPrioritizationOutputModel:
    """
    Prioritizes tasks using Gemini LLM.
    
    Args:
        tasks: TaskDecompositionOutputModel containing tasks to prioritize.
    
    Returns:
        TaskPrioritizationOutputModel with prioritized tasks.
    """
    llm_client = get_llm()
    input_str = json.dumps(tasks.model_dump(), separators=(",", ":"))
    prompt = PRIORITIZATION_PROMPT.format(tasks_json=input_str)

    try:
        response = llm_client.invoke([{"role": "user", "content": prompt}])
        raw_output = response.content.strip()

        if not raw_output:
            logging.error("Empty response from Gemini for prioritization.")
            return TaskPrioritizationOutputModel(tasks=[])

        cleaned_output = clean_json_tool.invoke(raw_output)
        if cleaned_output == "{}":
            logging.warning("Initial JSON cleaning failed, attempting LLM-based fix")
            cleaned_output = fix_json_with_llm_tool.invoke(raw_output)

        logging.info("Cleaned JSON:\n%s", cleaned_output)
        prioritized_json = json.loads(cleaned_output)
        validated = TaskPrioritizationOutputModel(**prioritized_json)
        return TaskPrioritizationOutputModel(tasks=validated.model_dump().get("tasks", []))
    except (json.JSONDecodeError, ValidationError) as e:
        logging.error("Error in task prioritization: %s\nRaw output: %s", e, raw_output)
        try:
            raw_json = json.loads(re.sub(r"```(json)?", "", raw_output).strip())
            validated = TaskPrioritizationOutputModel(**raw_json)
            logging.info("Successfully used raw JSON as fallback")
            return TaskPrioritizationOutputModel(tasks=validated.model_dump().get("tasks", []))
        except (json.JSONDecodeError, ValidationError) as e:
            logging.error("Fallback raw JSON parsing failed: %s", e)
            return TaskPrioritizationOutputModel(tasks=[])

@tool
def map_roles_tool(tasks: TaskPrioritizationOutputModel) -> TaskPrioritizationOutputModel:
    """
    Maps tasks to employee roles based on task type.
    
    Args:
        tasks: TaskPrioritizationOutputModel containing tasks to map.
    
    Returns:
        TaskPrioritizationOutputModel with tasks assigned to employees.
    """
    tasks_json = tasks.model_dump()
    role_map = {e["role"].lower(): e for e in employees}

    for task in tasks_json.get("tasks", []):
        task_type_key = task["type"].lower()
        task["assignee"] = role_map.get(task_type_key, employees[0])
        for sub in task.get("subtasks", []):
            sub_type_key = sub["type"].lower()
            sub["assignee"] = role_map.get(sub_type_key, employees[0])

    return TaskPrioritizationOutputModel(tasks=tasks_json.get("tasks", []))

@tool
def calculate_sprints_tool(tasks: TaskPrioritizationOutputModel, hours_per_day: int = 8, sprint_days: int = 5) -> SprintPlanningOutput:
    """
    Calculates sprint planning based on task hours and employee capacity.
    
    Args:
        tasks: TaskPrioritizationOutputModel containing tasks to plan.
        hours_per_day: Hours each employee can work per day (default: 8).
        sprint_days: Number of days per sprint (default: 5).
    
    Returns:
        SprintPlanningOutput with first sprint tasks and total sprints required.
    """
    tasks_json = tasks.model_dump()
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

    return SprintPlanningOutput(
        first_sprint_tasks=first_sprint_tasks,
        total_sprints_required=int(total_sprints)
    )

@tool
def setup_jira_project_tool(input: JiraProjectInput) -> JiraProjectOutput:
    """
    Sets up a Jira project, filter, and board.
    
    Args:
        input: JiraProjectInput with project key, name, and lead email.
    
    Returns:
        JiraProjectOutput with project, filter, and board details.
    """
    project = None
    jira_filter = None
    board = None
    
    if not jira.test_connection():
        logging.error("Failed to connect to Jira. Check your credentials and URL.")
        return JiraProjectOutput(project=None, jira_filter=None, board=None)
    
    try:
        logging.info(f"Getting Jira account ID for lead: {input.lead_email}")
        lead_account_id = jira.get_account_id_by_email(input.lead_email)
        logging.info(f"Lead account ID: {lead_account_id}")
    except Exception as e:
        logging.error(f"Error getting lead account ID: {e}")
        return JiraProjectOutput(project=None, jira_filter=None, board=None)
    
    try:
        logging.info(f"Creating/Getting Jira project: {input.project_name}")
        project = jira.create_project(
            key=input.project_key,
            name=input.project_name,
            lead_account_id=lead_account_id
        )
        logging.info(f"Project ready: {project.get('key', input.project_key)}")
    except Exception as e:
        logging.error(f"Error with project setup: {e}")
        try:
            if jira.project_exists(input.project_key):
                logging.info(f"Project {input.project_key} already exists, using existing project")
                url = f"{jira.base_url}/rest/api/3/project/{input.project_key}"
                response = requests.get(url, auth=jira.auth, headers=jira.headers)
                response.raise_for_status()
                project = response.json()
            else:
                return JiraProjectOutput(project=None, jira_filter=None, board=None)
        except Exception as e:
            logging.error(f"Failed to retrieve existing project: {e}")
            return JiraProjectOutput(project=None, jira_filter=None, board=None)

    try:
        jql = f'project = "{project["key"]}" ORDER BY priority DESC'
        filter_name = f"{input.project_key} Filter"
        logging.info(f"Checking for existing Jira filter: {filter_name}")

        existing_filters = jira.get_filters(filter_name)

        for f in existing_filters.get('values', []):
            if f['name'] == filter_name:
                logging.info(f"Found existing filter: {filter_name} (ID: {f['id']})")
                jira_filter = f
                break
        
        if not jira_filter:
            logging.info(f"Creating Jira filter with JQL: {jql}")
            jira_filter = jira.create_filter(
                name=filter_name,
                jql=jql,
                description="Auto-generated filter for sprint tasks"
            )
            logging.info(f"Filter created with ID: {jira_filter['id']}")
    except Exception as e:
        logging.error(f"Error creating or retrieving filter: {e}")
        return JiraProjectOutput(project=project, jira_filter=None, board=None)

    try:
        existing_boards = jira.get_boards(project["key"])
        if existing_boards.get("values"):
            board = existing_boards["values"][0]
            logging.info(f"Using existing board: {board['name']} (ID: {board['id']})")
        else:
            board_name = f"{input.project_key} Scrum Board"
            logging.info(f"Creating Jira board: {board_name} using filter ID: {jira_filter['id']}")
            board = jira.create_board(name=board_name, filter_id=jira_filter["id"])
            logging.info(f"Board created with ID: {board['id']}")
    except Exception as e:
        logging.error(f"Error creating or retrieving board: {e}")
        return JiraProjectOutput(project=project, jira_filter=jira_filter, board=None)
    
    return JiraProjectOutput(project=project, jira_filter=jira_filter, board=board)


@tool
def create_jira_sprint_tool(board: Dict, sprint_name: str = "Sprint 1") -> JiraSprintOutput:
    """
    Creates a Jira sprint for a given board.
    
    Args:
        board: Dictionary containing Jira board details.
        sprint_name: Name of the sprint (default: Sprint 1).
    
    Returns:
        JiraSprintOutput with sprint details.
    """
    if not isinstance(board, dict) or 'id' not in board:
        logging.error(f"Invalid board input: {board}. Expected a dictionary with 'id'.")
        return JiraSprintOutput(sprint=None)
    
    try:
        logging.info(f"Creating Sprint '{sprint_name}' on board ID {board['id']}")
        sprint = jira.create_sprint(
            name=sprint_name,
            board_id=int(board["id"])
        )
        logging.info(f"Sprint created with ID: {sprint['id']}")
        return JiraSprintOutput(sprint=sprint)
    except Exception as e:
        logging.error(f"Error creating sprint: {e}")
        return JiraSprintOutput(sprint=None)

@tool
def create_jira_issues_tool(sprint_plan: SprintPlanningOutput, project: Dict, sprint: Dict) -> Dict:
    """
    Creates Jira issues and subtasks for the first sprint tasks.
    
    Args:
        sprint_plan: SprintPlanningOutput with tasks for the first sprint.
        project: Dictionary containing Jira project details.
        sprint: Dictionary containing Jira sprint details.
    
    Returns:
        Dictionary with created issue keys.
    """
    created_issue_keys = []
    if not project or not sprint_plan.first_sprint_tasks:
        logging.warning("No project or tasks available for issue creation.")
        return {"issue_keys": []}

    for i, task in enumerate(sprint_plan.first_sprint_tasks, start=1):
        try:
            assignee_email = task.get("assignee", {}).get("email")
            assignee_id = None
            if assignee_email:
                try:
                    assignee_id = jira.get_account_id_by_email(assignee_email)
                    logging.info(f"Assignee resolved: {assignee_email} -> {assignee_id}")
                except Exception as e:
                    logging.warning(f"Could not resolve assignee for {assignee_email}: {e}")

            logging.info(f"Creating issue {i}: {task['summary']}")
            issue = jira.create_issue_with_auto_type(
                project_key=project["key"],
                summary=task["summary"],
                description=task.get("description", ""),
                assignee_id=assignee_id,
                preferred_types=['Story', 'Task', 'User Story', 'Feature']
            )
            
            if not issue:
                logging.error(f"Failed to create issue: {task['summary']}")
                continue
                
            logging.info(f"Issue created: {issue['key']}")
            created_issue_keys.append(issue['key'])

            for j, sub in enumerate(task.get("subtasks", []), start=1):
                try:
                    sub_assignee_email = sub.get("assignee", {}).get("email")
                    sub_assignee_id = None
                    if sub_assignee_email:
                        try:
                            sub_assignee_id = jira.get_account_id_by_email(sub_assignee_email)
                        except Exception as e:
                            logging.warning(f"Could not resolve subtask assignee: {e}")

                    logging.info(f"   Creating subtask {j} for {issue['key']}: {sub['summary']}")
                    sub_issue = jira.create_issue_with_auto_type(
                        project_key=project["key"],
                        summary=sub["summary"],
                        description=sub.get("description", ""),
                        assignee_id=sub_assignee_id,
                        parent_key=issue["key"],
                        preferred_types=['Sub-task', 'Subtask', 'Sub Task']
                    )
                    
                    if sub_issue:
                        logging.info(f"   Subtask created: {sub_issue['key']}")
                        created_issue_keys.append(sub_issue['key'])
                        time.sleep(1)
                    else:
                        logging.error(f"   Failed to create subtask: {sub['summary']}")

                except Exception as e:
                    logging.error(f"Failed to create subtask '{sub['summary']}': {e}")
                    continue

        except Exception as e:
            logging.error(f"Failed to create issue '{task['summary']}': {e}")
            continue

    if sprint and isinstance(sprint, dict) and 'id' in sprint and created_issue_keys:
        time.sleep(2)
        try:
            logging.info(f"Moving {len(created_issue_keys)} issues into sprint {sprint['id']}...")
            jira.move_issue_to_sprint(sprint["id"], created_issue_keys)
            logging.info("All issues moved into sprint successfully!")
        except Exception as e:
            logging.warning(f"Could not move issues into sprint: {e}")

    return {"issue_keys": created_issue_keys}

# -------------------
# Agent Setup
# -------------------
tools = [
    clean_json_tool,
    fix_json_with_llm_tool,
    task_decomposition_tool,
    prioritize_tasks_tool,
    map_roles_tool,
    calculate_sprints_tool,
    setup_jira_project_tool,
    create_jira_sprint_tool,
    create_jira_issues_tool
]

prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content="You are a sprint planning assistant. Use the provided tools to decompose user stories, prioritize tasks, map roles, plan sprints, and set up Jira projects and sprints. Follow the steps in order: 1) Decompose user stories, 2) Prioritize tasks, 3) Map roles, 4) Plan sprints, 5) Set up Jira project, 6) Create sprint, 7) Create issues. Use clean_json_tool to parse JSON outputs from the LLM. If clean_json_tool returns '{}', use fix_json_with_llm_tool to attempt a fix. If both fail, attempt to parse the raw JSON output (after removing code block markers) as a fallback. Ensure inputs to tools are correctly formatted (e.g., pass TaskDecompositionOutputModel to prioritize_tasks_tool). Provide a summary of the results, including any errors encountered, and continue processing with any valid tasks if possible."),
    MessagesPlaceholder(variable_name="messages"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

llm = get_llm() 
agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

if __name__ == "__main__":
    test_cases_input ={
  "userStories": [
    {
      "storyId": "US-1",
      "description": "As a Project Manager, I want a customizable dashboard to view project health and performance metrics so that I can track progress and make informed decisions.",
      "testCases": [
        {
          "testCaseId": "TC-1.1",
          "description": "Verify that the dashboard displays project health status for individual projects.",
          "steps": [
            "Log in as a Project Manager.",
            "Navigate to the Smart Project Analytics dashboard.",
            "Observe the 'Project Health' section."
          ],
          "expectedResult": "The dashboard displays the health status (e.g., 'On Track', 'At Risk', 'Delayed') for each individual project.",
          "type": "Positive"
        },
        {
          "testCaseId": "TC-1.2",
          "description": "Verify that the dashboard displays key performance indicators (KPIs).",
          "steps": [
            "Log in as a Project Manager.",
            "Navigate to the Smart Project Analytics dashboard.",
            "Observe the KPI section."
          ],
          "expectedResult": "The dashboard displays KPIs such as budget adherence, task completion rate, and resource utilization.",
          "type": "Positive"
        },
        {
          "testCaseId": "TC-1.3",
          "description": "Verify that users can filter dashboard views by project, team, and time period.",
          "steps": [
            "Log in as a Project Manager.",
            "Navigate to the Smart Project Analytics dashboard.",
            "Locate the filter options.",
            "Apply filters for a specific project, team, and time period."
          ],
          "expectedResult": "The dashboard view updates to reflect the applied filters for project, team, and time period.",
          "type": "Positive"
        },
        {
          "testCaseId": "TC-1.4",
          "description": "Verify drill-down capabilities from high-level summaries to detailed project data.",
          "steps": [
            "Log in as a Project Manager.",
            "Navigate to the Smart Project Analytics dashboard.",
            "Click on a high-level project summary or KPI."
          ],
          "expectedResult": "The system navigates to a detailed view of the selected project's data or the specific KPI's breakdown.",
          "type": "Positive"
        }
      ]
    },
    {
      "storyId": "US-2",
      "description": "As a Project Manager, I want the system to proactively identify potential project risks and alert me so that I can take timely corrective actions.",
      "testCases": [
        {
          "testCaseId": "TC-2.1",
          "description": "Verify the system identifies and flags projects at risk of schedule delays.",
          "steps": [
            "Log in as a Project Manager.",
            "Access a project with simulated conditions leading to schedule delays (e.g., tasks behind schedule, critical path impacted).",
            "Navigate to the Smart Project Analytics dashboard or risk section."
          ],
          "expectedResult": "The system identifies and flags the project as 'at risk' of schedule delays, visible on the dashboard or in a dedicated risk report.",
          "type": "Positive"
        },
        {
          "testCaseId": "TC-2.2",
          "description": "Verify the system identifies and flags projects at risk of budget overruns.",
          "steps": [
            "Log in as a Project Manager.",
            "Access a project with simulated conditions leading to budget overruns (e.g., actual expenditure exceeding planned, high forecasted costs).",
            "Navigate to the Smart Project Analytics dashboard or risk section."
          ],
          "expectedResult": "The system identifies and flags the project as 'at risk' of budget overruns, visible on the dashboard or in a dedicated risk report.",
          "type": "Positive"
        },
        {
          "testCaseId": "TC-2.3",
          "description": "Verify users receive configurable in-app alerts for new or escalating risks.",
          "steps": [
            "Log in as a Project Manager.",
            "Configure in-app alerts for risk identification.",
            "Simulate a new risk being identified for a project."
          ],
          "expectedResult": "An in-app notification or alert is displayed to the Project Manager regarding the new risk.",
          "type": "Positive"
        },
        {
          "testCaseId": "TC-2.4",
          "description": "Verify users receive configurable email alerts for new or escalating risks.",
          "steps": [
            "Log in as a Project Manager.",
            "Configure email alerts for risk identification.",
            "Simulate an existing risk escalating for a project."
          ],
          "expectedResult": "An email notification is sent to the Project Manager regarding the escalating risk.",
          "type": "Positive"
        },
        {
          "testCaseId": "TC-2.5",
          "description": "Verify each identified risk includes an AI-generated explanation of contributing factors.",
          "steps": [
            "Log in as a Project Manager.",
            "View an identified risk on the dashboard or risk report.",
            "Examine the details of the risk."
          ],
          "expectedResult": "The identified risk includes a brief, AI-generated explanation detailing the contributing factors (e.g., 'Task X is delayed by 5 days, impacting critical path').",
          "type": "Positive"
        }
      ]
    },
    {
      "storyId": "US-3",
      "description": "As a Team Lead, I want detailed analytics on resource workload and bottlenecks so that I can optimize task distribution and prevent burnout.",
      "testCases": [
        {
          "testCaseId": "TC-3.1",
          "description": "Verify users can view a visual breakdown of resource utilization.",
          "steps": [
            "Log in as a Team Lead.",
            "Navigate to the Resource Workload Analysis section.",
            "Observe the resource utilization display."
          ],
          "expectedResult": "A visual breakdown (e.g., charts, graphs) of resource utilization across projects, tasks, and teams is displayed.",
          "type": "Positive"
        },
        {
          "testCaseId": "TC-3.2",
          "description": "Verify the system highlights over-allocated individuals or teams.",
          "steps": [
            "Log in as a Team Lead.",
            "Navigate to the Resource Workload Analysis section.",
            "Simulate a scenario where an individual or team is significantly over-allocated.",
            "Observe the display."
          ],
          "expectedResult": "The system clearly highlights or flags individuals or teams with significantly over-allocated workloads based on defined thresholds.",
          "type": "Positive"
        },
        {
          "testCaseId": "TC-3.3",
          "description": "Verify the system highlights under-allocated individuals or teams.",
          "steps": [
            "Log in as a Team Lead.",
            "Navigate to the Resource Workload Analysis section.",
            "Simulate a scenario where an individual or team is significantly under-allocated.",
            "Observe the display."
          ],
          "expectedResult": "The system clearly highlights or flags individuals or teams with significantly under-allocated workloads based on defined thresholds.",
          "type": "Positive"
        },
        {
          "testCaseId": "TC-3.4",
          "description": "Verify the system identifies potential bottlenecks in task dependencies.",
          "steps": [
            "Log in as a Team Lead.",
            "Navigate to the Resource Workload Analysis section.",
            "Simulate a project with a critical task dependency causing a bottleneck.",
            "Observe the analysis results."
          ],
          "expectedResult": "The system identifies and highlights potential bottlenecks related to task dependencies impacting project progress.",
          "type": "Positive"
        },
        {
          "testCaseId": "TC-3.5",
          "description": "Verify the system identifies potential bottlenecks in resource availability.",
          "steps": [
            "Log in as a Team Lead.",
            "Navigate to the Resource Workload Analysis section.",
            "Simulate a project where a key resource is unavailable, causing a bottleneck.",
            "Observe the analysis results."
          ],
          "expectedResult": "The system identifies and highlights potential bottlenecks related to resource availability impacting project progress.",
          "type": "Positive"
        },
        {
          "testCaseId": "TC-3.6",
          "description": "Verify users can view historical workload trends.",
          "steps": [
            "Log in as a Team Lead.",
            "Navigate to the Resource Workload Analysis section.",
            "Locate the historical data view."
          ],
          "expectedResult": "The system displays historical workload trends for individuals and teams over a configurable period.",
          "type": "Positive"
        },
        {
          "testCaseId": "TC-3.7",
          "description": "Verify users can forecast future resource needs.",
          "steps": [
            "Log in as a Team Lead.",
            "Navigate to the Resource Workload Analysis section.",
            "Locate the forecasting tool/section."
          ],
          "expectedResult": "The system provides a forecast of future resource needs based on current project plans and historical data.",
          "type": "Positive"
        }
      ]
    },
    {
      "storyId": "US-4",
      "description": "As an Executive, I want to view aggregated performance trends across my project portfolio so that I can make informed strategic investments.",
      "testCases": [
        {
          "testCaseId": "TC-4.1",
          "description": "Verify users can view aggregated performance metrics across all projects.",
          "steps": [
            "Log in as an Executive.",
            "Navigate to the Portfolio Analytics dashboard.",
            "Observe the aggregated metrics section."
          ],
          "expectedResult": "The dashboard displays aggregated performance metrics (e.g., average project completion rate, overall budget variance) across all projects in the portfolio.",
          "type": "Positive"
        },
        {
          "testCaseId": "TC-4.2",
          "description": "Verify the system displays historical trends for key portfolio metrics.",
          "steps": [
            "Log in as an Executive.",
            "Navigate to the Portfolio Analytics dashboard.",
            "Locate the historical trends section."
          ],
          "expectedResult": "The system displays historical trends over time for key portfolio metrics, allowing for performance comparison.",
          "type": "Positive"
        },
        {
          "testCaseId": "TC-4.3",
          "description": "Verify users can compare performance across different departments.",
          "steps": [
            "Log in as an Executive.",
            "Navigate to the Portfolio Analytics dashboard.",
            "Apply filters or use comparison tools to view performance by department."
          ],
          "expectedResult": "The system allows users to compare performance metrics across different departments within the portfolio.",
          "type": "Positive"
        },
        {
          "testCaseId": "TC-4.4",
          "description": "Verify users can compare performance across different project types.",
          "steps": [
            "Log in as an Executive.",
            "Navigate to the Portfolio Analytics dashboard.",
            "Apply filters or use comparison tools to view performance by project type."
          ],
          "expectedResult": "The system allows users to compare performance metrics across different project types within the portfolio.",
          "type": "Positive"
        },
        {
          "testCaseId": "TC-4.5",
          "description": "Verify users can compare performance across different business units.",
          "steps": [
            "Log in as an Executive.",
            "Navigate to the Portfolio Analytics dashboard.",
            "Apply filters or use comparison tools to view performance by business unit."
          ],
          "expectedResult": "The system allows users to compare performance metrics across different business units within the portfolio.",
          "type": "Positive"
        },
        {
          "testCaseId": "TC-4.6",
          "description": "Verify the system provides a summary of top-performing projects.",
          "steps": [
            "Log in as an Executive.",
            "Navigate to the Portfolio Analytics dashboard.",
            "Locate the summary section for project performance."
          ],
          "expectedResult": "The system displays a summary of top-performing projects based on configurable criteria (e.g., on-time, under budget).",
          "type": "Positive"
        },
        {
          "testCaseId": "TC-4.7",
          "description": "Verify the system provides a summary of under-performing projects.",
          "steps": [
            "Log in as an Executive.",
            "Navigate to the Portfolio Analytics dashboard.",
            "Locate the summary section for project performance."
          ],
          "expectedResult": "The system displays a summary of under-performing projects based on configurable criteria (e.g., delayed, over budget).",
          "type": "Positive"
        }
      ]
    },
    {
      "storyId": "US-5",
      "description": "As a Project Manager, I want AI-driven actionable recommendations for identified risks and bottlenecks so that I can improve project performance.",
      "testCases": [
        {
          "testCaseId": "TC-5.1",
          "description": "Verify the system suggests potential actions for identified risks.",
          "steps": [
            "Log in as a Project Manager.",
            "Navigate to a project with an identified risk (e.g., schedule delay).",
            "View the risk details or a dedicated recommendations section."
          ],
          "expectedResult": "The system suggests potential actions to address the identified risk (e.g., 'Reallocate resources from Project B to Project A', 'Adjust deadline for Task X').",
          "type": "Positive"
        },
        {
          "testCaseId": "TC-5.2",
          "description": "Verify the system suggests potential actions for identified bottlenecks.",
          "steps": [
            "Log in as a Project Manager.",
            "Navigate to a project with an identified bottleneck (e.g., resource contention).",
            "View the bottleneck details or a dedicated recommendations section."
          ],
          "expectedResult": "The system suggests potential actions to address the identified bottleneck (e.g., 'Initiate a review of Task Y dependencies', 'Provide additional training for Resource Z').",
          "type": "Positive"
        },
        {
          "testCaseId": "TC-5.3",
          "description": "Verify recommendations are presented with a clear rationale.",
          "steps": [
            "Log in as a Project Manager.",
            "View an AI-driven recommendation."
          ],
          "expectedResult": "Each recommendation is accompanied by a clear, concise rationale explaining why it is suggested.",
          "type": "Positive"
        },
        {
          "testCaseId": "TC-5.4",
          "description": "Verify recommendations are presented with a predicted impact.",
          "steps": [
            "Log in as a Project Manager.",
            "View an AI-driven recommendation."
          ],
          "expectedResult": "Each recommendation includes a predicted impact if the action is taken (e.g., 'Reduces delay by 3 days', 'Improves resource utilization by 10%').",
          "type": "Positive"
        },
        {
          "testCaseId": "TC-5.5",
          "description": "Verify users can accept recommendations.",
          "steps": [
            "Log in as a Project Manager.",
            "View an AI-driven recommendation.",
            "Click the 'Accept' button/option for the recommendation."
          ],
          "expectedResult": "The system registers the recommendation as 'Accepted' and potentially initiates relevant actions or updates.",
          "type": "Positive"
        },
        {
          "testCaseId": "TC-5.6",
          "description": "Verify users can dismiss recommendations.",
          "steps": [
            "Log in as a Project Manager.",
            "View an AI-driven recommendation.",
            "Click the 'Dismiss' button/option for the recommendation."
          ],
          "expectedResult": "The system removes the recommendation from the active list and registers it as 'Dismissed'.",
          "type": "Positive"
        },
        {
          "testCaseId": "TC-5.7",
          "description": "Verify users can mark recommendations as acted upon.",
          "steps": [
            "Log in as a Project Manager.",
            "View an AI-driven recommendation.",
            "Manually perform the suggested action outside the system.",
            "Click the 'Mark as Acted Upon' button/option for the recommendation."
          ],
          "expectedResult": "The system registers the recommendation as 'Acted Upon' and potentially prompts for feedback.",
          "type": "Positive"
        },
        {
          "testCaseId": "TC-5.8",
          "description": "Verify recommendations are tailored to the user's role (Project Manager).",
          "steps": [
            "Log in as a Project Manager.",
            "View AI-driven recommendations for a project risk."
          ],
          "expectedResult": "Recommendations are relevant and actionable from a Project Manager's perspective (e.g., resource reallocation, deadline adjustments).",
          "type": "Positive"
        },
        {
          "testCaseId": "TC-5.9",
          "description": "Verify recommendations are tailored to the user's role (Team Lead).",
          "steps": [
            "Log in as a Team Lead.",
            "View AI-driven recommendations for a team bottleneck."
          ],
          "expectedResult": "Recommendations are relevant and actionable from a Team Lead's perspective (e.g., task re-assignment, skill development).",
          "type": "Positive"
        },
        {
          "testCaseId": "TC-5.10",
          "description": "Verify recommendations are tailored to the specific context of the insight.",
          "steps": [
            "Log in as a Project Manager.",
            "View recommendations for a budget overrun risk.",
            "View recommendations for a schedule delay risk."
          ],
          "expectedResult": "Recommendations for a budget overrun are different and specific to financial adjustments, while recommendations for a schedule delay are specific to timeline and task management.",
          "type": "Positive"
        }
      ]
    }
  ]
}

    processor = TaskExecutionAgent(user_stories=test_cases_input)
    output = processor.task_execution()
    print(output)