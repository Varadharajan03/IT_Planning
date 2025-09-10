from langgraph.graph import StateGraph, END
from .state import GraphState

# Agents
from agents.leave_mail_agent import check_leave_mail_node
from agents.team_verification_agent import verify_team_member_node
from agents.jira_task_agent import fetch_tasks_node
from agents.task_reallocation_agent import reallocate_tasks_node
from agents.notification_agent import send_overdue_notification_node

workflow = StateGraph(GraphState)

# Step 1: Detect leave mail
workflow.add_node("check_leave_mail", check_leave_mail_node)

# Step 2: Verify member in team
workflow.add_node("verify_team_member", verify_team_member_node)

# Step 3: Fetch tasks from Jira
workflow.add_node("fetch_tasks", fetch_tasks_node)

# Step 4: Reallocate if needed
workflow.add_node("reallocate_tasks", reallocate_tasks_node)

# Step 5: Overdue task notifications
workflow.add_node("send_notifications", send_overdue_notification_node)

# Flow connections
workflow.set_entry_point("check_leave_mail")
workflow.add_edge("check_leave_mail", "verify_team_member")
workflow.add_edge("verify_team_member", "fetch_tasks")
workflow.add_edge("fetch_tasks", "reallocate_tasks")
workflow.add_edge("reallocate_tasks", "send_notifications")
workflow.add_edge("send_notifications", END)

# Compile
app = workflow.compile()
