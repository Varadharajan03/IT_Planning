import json
from agents.prd_frd_generator import generate_prd_frd_node

state = {"requirements": {
  "projectName": "TaskFlow Pro",
  "featureName": "Smart Project Analytics",
  "industry": "Project Management Software",
  "target_users": "Project managers, team leads, executives",
  "business_context": "SaaS platform adding AI-powered analytics"
}}

print("===== Running PRD/FRD Generator =====")
out = generate_prd_frd_node(state)

final_obj = out.get("prd", {})
print("\n===== Summary =====")
print("Project:", final_obj.get("projectName"))
print("Feature:", final_obj.get("featureName"))
print("PRD keys:", list(final_obj.get("prd", {}).keys()))
print("FRD count:", len(final_obj.get("frd", [])))

print("\n===== Full Output (JSON) =====")
print(json.dumps(final_obj, indent=2, ensure_ascii=False))