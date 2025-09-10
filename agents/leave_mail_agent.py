from tools.gmail_utils import check_leave_mail

def check_leave_mail_node(state):
    """
    Node: Fetch leave mails from project head.
    """
    project_head_email = state.get("project_head_email", "")
    leave_mails = check_leave_mail(project_head_email)

    if leave_mails:
        # Take first leave mail for simplicity
        state["email_data"] = leave_mails[0]
    else:
        state["email_data"] = {}

    return state
