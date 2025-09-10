import csv

def verify_team_member_node(state):
    """
    Node: Check if the person from leave mail exists in team CSV.
    """
    person = state.get("email_data", {}).get("person")
    team_csv = state.get("team_csv", [])

    member_verified = any(row.get("name") == person for row in team_csv)
    state["member_verified"] = member_verified

    return state
