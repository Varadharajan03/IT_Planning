from tools.gemini_client import gemini_call

def analyze_risks(prd, web_data):
    prompt = f"""
You are an experienced sophisticated risk analysis AI agent who is always keen on analyzing risks with extensive experience in evaluating potential risks associated with various projects. Your task is to analyze a Product Requirements Document (PRD) and recent risk insights to identify and categorize potential risks.

Here are the inputs you will need to consider:

Product Requirements Document: {prd}
Recent Risk Insights: {web_data}
Your output should be structured as follows: 1. Begin with a detailed explanation of the potential risks identified from the provided documents. 2. Then, create a JSON array that captures each risk with the following attributes:

risk_type
severity
description
law (optional)
Make sure to provide clear and concise explanations that are easy to understand. The JSON structure should be correctly formatted, ensuring that it adheres to JSON standards for proper parsing.

Example of expected output format:
THINKING: [Detailed explanation of potential risks here...]
RISKS_JSON: [ { "risk_type": "Example Risk Type", "severity": "High", "description": "Detailed description of the risk.", "law": "Optional legal reference" } ]

Please be mindful of the following constraints:

Ensure that the severity levels are clearly defined (e.g., Low, Medium, High).
Provide descriptions that are specific and actionable.
Avoid any technical jargon that may confuse the audience unless necessary for clarity.
Your analysis should be thorough, yet accessible to stakeholders who may not have a technical background.
"""

    output = gemini_call(prompt)

    try:
        thinking = output.split("RISKS_JSON:")[0].replace("THINKING:", "").strip()
        risks_json = output.split("RISKS_JSON:")[1].strip()
    except:
        thinking = output
        risks_json = "[]"

    import json
    try:
        parsed_risks = json.loads(risks_json)
    except:
        parsed_risks = []

    return thinking, parsed_risks
