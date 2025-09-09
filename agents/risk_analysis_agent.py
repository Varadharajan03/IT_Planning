from config.settings import get_llm
import json
import re

def analyze_risks(prd, web_data):
    # Convert prd dictionary to string if it's a dict
    if isinstance(prd, dict):
        prd = json.dumps(prd, indent=2)  # Pretty-print the dictionary
    elif not isinstance(prd, str):
        return "Error: PRD must be a string or dictionary", []

    # Convert web_data to string if it's a list or dict
    if isinstance(web_data, (list, dict)):
        web_data = json.dumps(web_data, indent=2)
        print(web_data)
    elif not isinstance(web_data, str):
        return "Error: Web data must be a string, list, or dictionary", []

    prompt = f"""
    You are an experienced sophisticated risk analysis AI agent who is always keen on analyzing risks with extensive experience in evaluating potential risks associated with various projects. Your task is to analyze a Product Requirements Document (PRD) and recent risk insights to identify and categorize potential risks.

    Here are the inputs you will need to consider:

    Product Requirements Document: {prd}
    Recent Risk Insights: {web_data}

    Your output should be structured as follows:
    1. Begin with a detailed explanation of the potential risks identified from the provided documents.
    2. Then, create a JSON array that captures each risk with the following attributes:

    - risk_type
    - severity
    - description
    - law (DDPA (if applicable))

    Make sure to provide clear and concise explanations that are easy to understand. The JSON structure should be correctly formatted, ensuring that it adheres to JSON standards for proper parsing.

    Example of expected output format:
    THINKING: [Detailed explanation of potential risks here...]
    RISKS_JSON: [{{
        "risk_type": "Example Risk Type",
        "severity": "High",
        "description": "Detailed description of the risk.",
        "law": "DDPA for Data Protection related risks(if applicable) else say null"
    }}]

    Please be mindful of the following constraints:
    - Ensure that the severity levels are clearly defined (e.g., Low, Medium, High).
    - Provide descriptions that are specific and actionable.
    - Avoid any technical jargon that may confuse the audience unless necessary for clarity.
    - Your analysis should be thorough, yet accessible to stakeholders who may not have a technical background.
    """

    try:
        llm = get_llm()  # Get the LLM client
        llm_response = llm.invoke(prompt)  # Use .invoke() for chat models

        # Debugging: Log the LLM response structure
        print("LLM Response:", llm_response)

        # Extract the content string
        if hasattr(llm_response, 'content'):
            # Handle case where content is a list of strings
            if isinstance(llm_response.content, list):
                # Use the first string if the list contains multiple, or join if needed
                output = llm_response.content[0] if llm_response.content else ""
            else:
                output = llm_response.content
        else:
            return "Error: LLM response missing content attribute", []

    except Exception as e:
        return f"Error calling LLM: {str(e)}", []

    try:
        # Split the output into THINKING and RISKS_JSON sections
        parts = output.split("RISKS_JSON:")
        thinking = parts[0].replace("THINKING:", "").strip() if parts[0] else ""
        risks_json = parts[1].strip() if len(parts) > 1 else "[]"

        # Clean up markdown code block markers
        risks_json = re.sub(r'```json\n|```', '', risks_json).strip()

        # Parse the RISKS_JSON part
        parsed_risks = json.loads(risks_json)
        if not isinstance(parsed_risks, list):
            parsed_risks = []
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {str(e)}")
        thinking = output
        parsed_risks = []
    except Exception as e:
        print(f"Error processing LLM output: {str(e)}")
        thinking = output
        parsed_risks = []

    return thinking, parsed_risks