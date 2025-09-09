from config.settings import get_llm
import json
import re

def robust_parse_risks_json(raw_output):
    """
    Robustly parse the RISKS_JSON section from LLM output, handling common hallucinations and format errors.
    Uses regex and logical fixes for edge cases like mismatched braces, extra characters, missing quotes, etc.
    Returns (thinking_text, parsed_risks_list)
    """
    # Step 1: Split the output into THINKING and RISKS_JSON sections
    parts = raw_output.split("RISKS_JSON:", 1)  # Split only once to avoid multiple if present
    thinking = ""
    risks_json_str = "[]"
    
    if len(parts) > 1:
        thinking = parts[0].replace("THINKING:", "").strip()
        risks_json_str = parts[1].strip()
    
    if not thinking:
        thinking = raw_output.strip()
    
    # Step 2: Clean up markdown code blocks and common wrappers
    risks_json_str = re.sub(r'```json\s*|\s*```|```|\n', '', risks_json_str).strip()
    risks_json_str = re.sub(r'^\s*RISKS_JSON:\s*', '', risks_json_str).strip()
    
    # Step 3: Handle empty or non-JSON cases early
    if not risks_json_str or risks_json_str.lower() in ['[]', 'null', 'none', 'empty']:
        return thinking, []
    
    # Step 4: Extract the JSON array-like content using regex
    # Look for the outermost [ ... ] structure, allowing for some noise
    array_match = re.search(r'\[\s*\{.*\}\s*\]', risks_json_str, re.DOTALL)
    if array_match:
        risks_json_str = array_match.group(0)
    else:
        # If no array found, try to find any list-like structure starting with [
        start_idx = risks_json_str.find('[')
        end_idx = risks_json_str.rfind(']')
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            risks_json_str = risks_json_str[start_idx:end_idx + 1]
        else:
            # Fallback: assume the whole string is the array if it starts with [
            if not risks_json_str.startswith('['):
                risks_json_str = '[' + risks_json_str + ']'
    
    # Step 5: Logical fixes for common hallucinations using regex
    # Fix 1: Double braces like {{ or }} -> { or }
    risks_json_str = re.sub(r'\{\{', '{', risks_json_str)
    risks_json_str = re.sub(r'\}\}', '}', risks_json_str)
    
    # Fix 2: Triple or more braces (e.g., {{{ -> {{ but since we did double, iteratively
    risks_json_str = re.sub(r'\{+', '{', risks_json_str)
    risks_json_str = re.sub(r'\}+', '}', risks_json_str)
    
    # Fix 3: Mismatched braces - simple balance check and fix (basic approximation)
    # Count open and close braces
    open_count = risks_json_str.count('{')
    close_count = risks_json_str.count('}')
    bracket_open = risks_json_str.count('[')
    bracket_close = risks_json_str.count(']')
    
    # Add missing closing if needed (append to end)
    if open_count > close_count:
        risks_json_str += '}' * (open_count - close_count)
    if bracket_open > bracket_close:
        risks_json_str += ']' * (bracket_open - bracket_close)
    
    # Add missing opening if needed (prepend, but less common)
    if close_count > open_count:
        risks_json_str = '{' * (close_count - open_count) + risks_json_str
    if bracket_close > bracket_open:
        risks_json_str = '[' * (bracket_close - bracket_open) + risks_json_str
    
    # Fix 4: Remove trailing commas before } or ]
    risks_json_str = re.sub(r',(\s*[}\]])', r'\1', risks_json_str)
    
    # Fix 5: Handle unquoted strings that look like keys/values (basic: add quotes around words not in quotes)
    # This is tricky; use regex to find unquoted strings in object contexts
    # Pattern for unquoted key: after { or , followed by word not in quotes
    def add_quotes_to_unquoted(match):
        return f'"{match.group(1)}"'
    
    # Add quotes to potential unquoted keys (e.g., risk_type: -> "risk_type":
    risks_json_str = re.sub(r'([,{]\s*)(\w+)(?=\s*:)', add_quotes_to_unquoted, risks_json_str)
    
    # Add quotes to unquoted string values (after : , if not number/boolean/null)
    def add_quotes_to_value(match):
        val = match.group(1).strip()
        if val.lower() in ['true', 'false', 'null'] or val.replace('.', '').isdigit():
            return f': {val}'
        else:
            return f': "{val}"'
    
    risks_json_str = re.sub(r':\s*([^{}[\],":]+?)(?=[,{}\]\s]|$)', add_quotes_to_value, risks_json_str)
    
    # Fix 6: Remove extra commas at end of objects/arrays
    risks_json_str = re.sub(r',\s*([}\]])', r'\1', risks_json_str)
    
    # Fix 7: Handle escaped quotes or other common escapes if needed (but LLM usually handles)
    risks_json_str = risks_json_str.replace('\\"', '"')  # Unescape if double
    
    # Step 6: Strip whitespace and normalize
    risks_json_str = re.sub(r'\s+', ' ', risks_json_str).strip()
    
    # Step 7: Try to parse the fixed string
    parsed_risks = []
    try:
        parsed = json.loads(risks_json_str)
        if isinstance(parsed, list):
            parsed_risks = parsed
        elif isinstance(parsed, dict):
            parsed_risks = [parsed]  # If single object, wrap in list
    except json.JSONDecodeError as e:
        # If still fails, log the error (in code, print for debugging)
        print(f"Final JSON parsing error after fixes: {str(e)}")
        print(f"Attempted JSON: {risks_json_str}")
        # Fallback: try to extract individual objects if it's a broken array
        obj_matches = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', risks_json_str, re.DOTALL)
        for obj_str in obj_matches:
            try:
                parsed_risks.append(json.loads(obj_str))
            except json.JSONDecodeError:
                pass  # Skip broken objects
        if not parsed_risks:
            parsed_risks = []  # Empty list as ultimate fallback
    
    # Step 8: Validate each risk item has required fields (optional: add defaults if missing)
    for risk in parsed_risks:
        if not isinstance(risk, dict):
            continue
        required_fields = ['risk_type', 'severity', 'description', 'law']
        for field in required_fields:
            if field not in risk:
                if field == 'law':
                    risk[field] = 'null'  # Default as per example
                else:
                    risk[field] = 'Unknown'  # Or handle appropriately
    
    return thinking, parsed_risks

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
    You are an experienced sophisticated risk analysis AI agent who is always keen on analyzing risks like Requirement Risk, Scope Creep Risk, Project Management Risk, Stakeholder Risk, Technical Risk, Quality Risk, Market/Strategic Risk, and Communication Risk with extensive experience in evaluating potential risks associated with various projects. Your task is to analyze a Product Requirements Document (PRD) and recent risk insights to identify and categorize potential risks.

    Here are the inputs you will need to consider:

    Product Requirements Document: {prd}
    Recent Risk Insights: {web_data}

    Your output should be structured as follows:
    1. Begin with a detailed explanation of the potential risks identified from the provided documents.
    2. Then, create a JSON array that captures each risk with the following attributes:

    - risk_type
    - severity
    - description
    - law 

    Make sure to provide clear and concise explanations that are easy to understand. The JSON structure should be correctly formatted, ensuring that it adheres to JSON standards for proper parsing.

    Example of expected output format:
    THINKING: [Detailed explanation of potential risks here...]
    RISKS_JSON: [{{
        "risk_type": "Example Risk Type",
        "severity": "High",
        "description": "Detailed description of the risk.",
        "law": "DDPA for Data Protection related risks,  else say null"
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

    # Use the robust parser instead of manual splitting
    return robust_parse_risks_json(output)