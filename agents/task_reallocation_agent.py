from tools.jira_utils import reassign_task, get_user_account_id, count_user_tasks

def reallocate_tasks_node(state):
    """
    Node: Reassign high-priority tasks from leave person to least-loaded member.
    """
    tasks = state.get("tasks", [])
    team_csv = state.get("team_csv", [])
    project_key = state.get("project_key")

    if not tasks or not project_key:
        state["reallocation"] = {"reassignedTasks": [], "targetUser": None}
        return state

    # Dynamically calculate workload from Jira
    workload = {}
    for member in team_csv:
        email = member["email"]
        workload[email] = count_user_tasks(project_key, email)

    # Find least loaded member
    target_user_email = min(workload, key=workload.get)
    target_account_id = get_user_account_id(target_user_email)

    reassigned = []
    for task in tasks:
        if task["priority"].lower() in ["high", "urgent"]:
            result = reassign_task(task["key"], target_account_id)
            reassigned.append({
                "task": task["key"],
                "to": target_user_email,
                "result": result
            })

    state["reallocation"] = {
        "reassignedTasks": reassigned,
        "targetUser": target_user_email
    }

    return state
