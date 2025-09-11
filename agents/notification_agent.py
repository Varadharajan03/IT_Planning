from tools.email_utils import send_email

def send_overdue_notification_node(state):
    """
    Node: Send email notification if any task is overdue.
    """
    tasks = state.get("tasks", [])
    notifications = []

    for task in tasks:
        if task["dueDate"] and task["status"].lower() != "done":
            # Example: if due date is past (skipping datetime check here for simplicity)
            subject = f"Overdue Task Reminder: {task['key']}"
            body = f"Task {task['summary']} ({task['key']}) is overdue. Please take action."
            recipient = task["assignee"]

            send_email(recipient, subject, body)
            notifications.append(f"Sent to {recipient} for {task['key']}")

    state["notifications"] = notifications
    return state
