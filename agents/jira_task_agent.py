from tools.jira_utils import fetch_user_tasks

def fetch_tasks_node(state):
    """
    Node: Fetch tasks of the member from Jira.
    """
    if not state.get("member_verified"):
        state["tasks"] = []
        return state

    project_key = state.get("project_key")
    person_email = state.get("email_data", {}).get("person_email")

    if not project_key or not person_email:
        state["tasks"] = []
        return state

    tasks = fetch_user_tasks(project_key, person_email)
    state["tasks"] = tasks
    return state
