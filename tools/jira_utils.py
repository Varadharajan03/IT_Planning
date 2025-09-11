import os
import requests
import re
import base64
from dotenv import load_dotenv
from urllib3.exceptions import NameResolutionError

# Load environment variables
load_dotenv()

# Jira configuration
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL", "").rstrip("/")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

# Validate Jira domain
if not JIRA_BASE_URL:
    raise ValueError("JIRA_BASE_URL environment variable is not set")
if not JIRA_BASE_URL.startswith("https://"):
    JIRA_BASE_URL = f"{JIRA_BASE_URL}"
if not re.match(r'^https://[a-zA-Z0-9-]+\.atlassian\.net$', JIRA_BASE_URL):
    raise ValueError(f"Invalid JIRA_BASE_URL format: {JIRA_BASE_URL}")

def get_jira_headers():
    """Generate headers for Jira API requests."""
    if not JIRA_EMAIL or not JIRA_API_TOKEN:
        raise ValueError("JIRA_EMAIL or JIRA_API_TOKEN not set")
    auth_str = base64.b64encode(f"{JIRA_EMAIL}:{JIRA_API_TOKEN}".encode()).decode()
    return {
        "Authorization": f"Basic {auth_str}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

def get_user_account_id(user_email: str):
    """
    Fetch Jira user's accountId by email or displayName fallback.
    """
    url = f"{JIRA_BASE_URL}/rest/api/3/user/search"
    params = {"query": user_email}
    try:
        response = requests.get(url, headers=get_jira_headers(), params=params)
        response.raise_for_status()
        users = response.json()

        if not users:
            # Fallback: Search by name part (e.g., "rohit.a.cse.2021")
            name_part = user_email.split("@")[0]
            params = {"query": name_part}
            response = requests.get(url, headers=get_jira_headers(), params=params)
            response.raise_for_status()
            users = response.json()

        if users:
            print(f"[DEBUG] Matched Jira user: {users[0]['displayName']} (accountId: {users[0]['accountId']})")
            return users[0]["accountId"]

        raise ValueError(f"No Jira account found for {user_email}")
    except NameResolutionError as e:
        print(f"[ERROR] DNS resolution failed for {JIRA_BASE_URL}: {e}")
        raise
    except requests.exceptions.HTTPError as e:
        print(f"[ERROR] HTTP error while fetching user account: {e}")
        raise
    except Exception as e:
        print(f"[ERROR] Failed to fetch user account: {e}")
        raise

def extract_email(user_string: str) -> str:
    """
    Extract email from a string like 'ROHIT A S SNSCT - CSE <rohit.a.cse.2021@snsct.org>'.
    """
    match = re.search(r'<(.+?)>', user_string)
    if match:
        return match.group(1).strip()
    return user_string.strip()

def fetch_user_tasks(project_key: str, user_email: str):
    """Fetch all tasks assigned to a user in a project."""
    try:
        clean_email = extract_email(user_email)
        account_id = get_user_account_id(clean_email)

        jql = f'project={project_key} AND assignee="{account_id}"'
        url = f"{JIRA_BASE_URL}/rest/api/3/search"
        print(f"[DEBUG] Using JQL: {jql}")

        response = requests.get(url, headers=get_jira_headers(), params={"jql": jql})
        response.raise_for_status()
        issues = response.json().get("issues", [])

        print(f"[DEBUG] Found {len(issues)} tasks for {clean_email}")
        return [
            {
                "key": issue["key"],
                "summary": issue["fields"]["summary"],
                "priority": issue["fields"]["priority"]["name"] if issue["fields"]["priority"] else "None",
                "assignee": issue["fields"]["assignee"]["displayName"] if issue["fields"]["assignee"] else "Unassigned",
                "status": issue["fields"]["status"]["name"],
                "dueDate": issue["fields"].get("duedate")
            }
            for issue in issues
        ]
    except NameResolutionError as e:
        print(f"[ERROR] DNS resolution failed for {JIRA_BASE_URL}. Check JIRA_BASE_URL configuration: {e}")
        return []
    except requests.exceptions.HTTPError as e:
        print(f"[ERROR] HTTP error while fetching tasks: {e}")
        return []
    except Exception as e:
        print(f"[ERROR] fetch_user_tasks failed: {e}")
        return []

def count_user_tasks(project_key: str, user_email: str) -> int:
    """Count the number of tasks assigned to a user in a project."""
    try:
        clean_email = extract_email(user_email)
        account_id = get_user_account_id(clean_email)

        jql = f'project={project_key} AND assignee="{account_id}"'
        url = f"{JIRA_BASE_URL}/rest/api/3/search"
        print(f"[DEBUG] Counting tasks with JQL: {jql}")

        response = requests.get(url, headers=get_jira_headers(), params={"jql": jql})
        response.raise_for_status()
        issues = response.json().get("issues", [])
        print(f"[DEBUG] Total tasks for {clean_email}: {len(issues)}")
        return len(issues)
    except NameResolutionError as e:
        print(f"[ERROR] DNS resolution failed for {JIRA_BASE_URL}: {e}")
        return 0
    except requests.exceptions.HTTPError as e:
        print(f"[ERROR] Failed to count tasks: {e}")
        return 0
    except Exception as e:
        print(f"[ERROR] Connection error: {e}")
        return 0

def reassign_task(task_key: str, new_assignee_account_id: str):
    """Reassign a Jira task to a new user by accountId."""
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{task_key}/assignee"
    payload = {"accountId": new_assignee_account_id}  # must be accountId, not email
    try:
        response = requests.put(url, headers=get_jira_headers(), json=payload)
        response.raise_for_status()
        print(f"[DEBUG] Task {task_key} reassigned to {new_assignee_account_id}")
        return response.json() if response.text else {"message": "Task reassigned successfully"}
    except requests.exceptions.HTTPError as e:
        print(f"[ERROR] Failed to reassign task {task_key}: {e.response.text}")
        return {"error": str(e)}
    except Exception as e:
        print(f"[ERROR] Connection error: {e}")
        return {"error": str(e)}

