import pandas as pd
from tools.gmail_utils import check_leave_mail
from tools.jira_utils import fetch_user_tasks, reassign_task, get_user_account_id
import re




# Path to your uploaded team CSV (portable)
import os
TEAM_CSV = os.path.join(os.getcwd(), "data", "team.csv")

def load_team():
    """
    Load the project team CSV and normalize emails and names.
    """
    df = pd.read_csv(TEAM_CSV)

    # Strip spaces, remove extra characters, lowercase emails
    df['email'] = df['email'].astype(str).str.strip().str.lower()

    # Optional: normalize names
    df['name'] = df['name'].astype(str).str.strip()

    return df

def normalize_email(email_str):
    """
    Extracts email from string like 'Name <email@example.com>'
    and lowercases it.
    """
    match = re.search(r'[\w\.-]+@[\w\.-]+', email_str)
    if match:
        return match.group(0).strip().lower()
    return email_str.strip().lower()

def run_workflow(project_key: str, leave_email: str):
    """
    Main resource optimization workflow.
    Triggered when a leave mail is detected.
    """

    # 1️⃣ Normalize the leave email
    leave_email_normalized = normalize_email(leave_email)

    # 2️⃣ Load team CSV and verify member exists
    team_df = load_team()

    matched_emails = [e for e in team_df['email'].tolist() if e in leave_email_normalized]

    if not matched_emails:
        return {"status": f"{leave_email} not in project team"}

    leave_email_normalized = matched_emails[0]

    # 3️⃣ Fetch Jira tasks for this member
    tasks = fetch_user_tasks(project_key, leave_email_normalized)
    if not tasks:
        return {"status": f"No tasks for {leave_email}"}

    # 4️⃣ Check workloads of others and reassign
    workload = {}
    for _, row in team_df.iterrows():
        email = row['email']
        if email == leave_email_normalized:
            continue
        user_tasks = fetch_user_tasks(project_key, email)
        workload[email] = len(user_tasks)

    if not workload:
        return {"status": "No alternate members found"}

    target_email = min(workload, key=workload.get)
    target_account_id = get_user_account_id(target_email)  # 🔑 use accountId for reassignment

    reassigned = []
    for task in tasks:
        reassign_task(task["key"], target_account_id)  # ✅ reassign ALL tasks
        reassigned.append(task["key"])

    return {
        "status": "Workflow completed",
        "leave_email": leave_email_normalized,
        "reassigned_to": target_email,
        "tasks_reassigned": reassigned
    }
