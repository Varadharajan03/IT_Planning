# IT Planning Workflow System

A comprehensive AI-powered workflow system that automates the complete project planning process from requirements to task execution and Jira integration.

## 🔄 Complete Workflow

The system now includes **4 integrated agents** in a sequential workflow:

1. **PRD/FRD Generator** → Creates Product Requirements Document and Functional Requirements Document
2. **Risk Analysis Agent** → Analyzes risks based on PRD output with web research
3. **Test Case Generator** → Creates comprehensive test cases based on PRD/FRD
4. **Task Execution Agent** → Decomposes tasks, prioritizes, maps roles, plans sprints, and sets up Jira

## 🚀 API Endpoints

### Main Endpoint
**POST** `/unified-workflow`

**Request Body:**
```json
{
  "project_name": "Your Project Name",
  "feature_name": "Your Feature Name",
  "industry": "Optional Industry",
  "target_users": "Optional Target Users", 
  "business_context": "Optional Business Context"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Unified workflow completed successfully",
  "data": {
    "markdown_file": "path/to/documentation.md",
    "prd_output": { /* PRD data */ },
    "risk_analysis": [ /* Risk analysis data */ ],
    "test_artifacts": { /* Test cases data */ },
    "task_execution": { /* Task execution results */ },
    "summary": {
      "project_name": "Project Name",
      "feature_name": "Feature Name",
      "total_risks": 12,
      "total_user_stories": 22,
      "total_test_cases": 74,
      "task_execution_status": "completed"
    }
  }
}
```

## 🛠️ Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Variables
Create a `.env` file with the following variables:

```env
# Required
GOOGLE_API_KEY=your_google_api_key_here

# Optional (for Jira integration)
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@domain.com
JIRA_API_TOKEN=your_jira_api_token_here
```

### 3. Run the API Server
```bash
python main.py
```

The server will start on `http://localhost:8000`

## 🧪 Testing

### Test Complete Workflow
```bash
python test_complete_workflow.py
```

### Test Basic Workflow (without task execution)
```bash
python test_unified_workflow.py
```

### Example Usage
```bash
python example_usage.py
```

## 📋 What Each Agent Does

### 1. PRD/FRD Generator
- Analyzes project requirements
- Creates comprehensive Product Requirements Document
- Generates detailed Functional Requirements Document
- Includes personas, business goals, success metrics, and risks

### 2. Risk Analysis Agent
- Analyzes PRD for potential risks
- Searches web for relevant risk information
- Categorizes risks by type and severity
- Provides detailed risk descriptions and mitigation strategies

### 3. Test Case Generator
- Creates user stories from requirements
- Generates comprehensive test cases
- Includes positive, negative, and edge-case scenarios
- Provides detailed test steps and expected results

### 4. Task Execution Agent
- Decomposes user stories into detailed tasks
- Prioritizes tasks based on business value
- Maps tasks to team members by role
- Plans sprints with capacity calculations
- Sets up Jira project, board, and issues
- Creates subtasks and assigns them to sprints

## 📄 Output Files

The system generates a comprehensive markdown documentation file containing:

1. **Project Overview** - Project and feature details
2. **PRD Section** - Complete product requirements
3. **FRD Section** - Detailed functional requirements
4. **Risk Analysis** - Identified risks and mitigation strategies
5. **Test Cases** - User stories and test scenarios
6. **Task Execution** - Decomposed tasks and sprint planning
7. **Summary** - Complete project statistics

## 🔧 Configuration

### Team Members (Hardcoded in task_execution_agent.py)
```python
employees = [
    {"name": "Kishor", "email": "kishor.r.ihub@snsgroups.com", "role": "Backend"},
    {"name": "Pradeep", "email": "pradeep.s.ihub@snsgroups.com", "role": "Fullstack"},
    {"name": "Srivarshini", "email": "srivarshini.r.ihub@snsgroups.com", "role": "Frontend"},
    {"name": "Jeba", "email": "jeba.m.ihub@snsgroups.com", "role": "DevOps"},
    {"name": "Rohit", "email": "rohit.a.ihub@snsgroups.com", "role": "QA"}
]
```

### Jira Configuration
- Project prefix: "TP" (configurable)
- Lead email: "jeba.m.ihub@snsgroups.com" (configurable)
- Sprint duration: 5 days (configurable)
- Hours per day: 8 (configurable)

## 🚨 Error Handling

The system includes comprehensive error handling:
- Graceful fallbacks for failed LLM responses
- JSON parsing error recovery
- Jira connection error handling
- Detailed logging for debugging

## 📊 Example Output Summary

```
Project: Smart Project Analytics Platform
Feature: Dashboard Management System
Risks Identified: 12
User Stories: 22
Test Cases: 74
Task Execution Status: completed
```

## 🔄 Workflow Flow

```
Input Requirements
       ↓
PRD/FRD Generator
       ↓
Risk Analysis Agent
       ↓
Test Case Generator
       ↓
Task Execution Agent
       ↓
Markdown Generator
       ↓
Complete Documentation
```

## 🎯 Benefits

1. **Complete Automation** - End-to-end project planning
2. **AI-Powered Analysis** - Intelligent risk assessment and task decomposition
3. **Jira Integration** - Direct project setup in Jira
4. **Comprehensive Documentation** - Single markdown file with all outputs
5. **Team Collaboration** - Role-based task assignment
6. **Sprint Planning** - Automated capacity calculations and sprint organization

## 🚀 Getting Started

1. Set up your environment variables
2. Run `python main.py`
3. Use Postman or curl to test the `/unified-workflow` endpoint
4. Check the generated markdown file for complete documentation
5. Verify Jira project setup (if configured)

The system is now ready to handle complete project planning workflows from requirements to task execution!
