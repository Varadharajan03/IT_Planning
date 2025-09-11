# Postman Configuration for IT Planning Workflow API

## 🚀 Updated API Configuration

### **Base URL:**
```
http://localhost:8000
```

### **1. Start the API Server:**
```bash
python main.py
```

### **2. Main Unified Workflow Endpoint:**

**Method:** `POST`  
**URL:** `http://localhost:8000/unified-workflow`  
**Headers:**
```
Content-Type: application/json
```

**Request Body (JSON):**
```json
{
  "project_name": "E-Commerce Platform",
  "feature_name": "Shopping Cart Management",
  "industry": "Retail",
  "target_users": "Online shoppers and merchants",
  "business_context": "A modern e-commerce platform with advanced cart functionality"
}
```

### **3. Expected Response Format:**

**Success Response (200):**
```json
{
  "success": true,
  "message": "Unified workflow completed successfully",
  "data": {
    "markdown_file": "C:\\Users\\HP\\Documents\\GitHub\\IT_Planning\\E-Commerce_Platform_Shopping_Cart_Management_documentation.md",
    "prd_output": {
      "projectName": "E-Commerce Platform",
      "featureName": "Shopping Cart Management",
      "prd": { /* PRD data */ },
      "frd": [ /* FRD data */ ]
    },
    "risk_analysis": [ /* Risk analysis data */ ],
    "test_artifacts": { /* Test cases data */ },
    "task_execution": {
      "result": "Task execution completed with Jira project: E-Commerce Platform - Shopping Cart Management",
      "status": "completed"
    },
    "summary": {
      "project_name": "E-Commerce Platform",
      "feature_name": "Shopping Cart Management",
      "total_risks": 12,
      "total_user_stories": 22,
      "total_test_cases": 74,
      "task_execution_status": "completed"
    }
  }
}
```

### **4. What's New in v4.0.0:**

✅ **Dynamic Project Names** - Jira projects now use the actual project name from the first agent  
✅ **No Hardcoded Data** - Removed hardcoded user stories from task execution agent  
✅ **Complete Integration** - Task execution agent receives user stories from test case generator  
✅ **Proper Naming** - Jira project will be named: `{project_name} - {feature_name}`  

### **5. Workflow Flow:**

```
Input: Project Name + Feature Name
       ↓
1. PRD/FRD Generator → Creates requirements
       ↓
2. Risk Analysis Agent → Analyzes risks
       ↓
3. Test Case Generator → Creates user stories & test cases
       ↓
4. Task Execution Agent → Uses project name + user stories
       ↓
5. Jira Setup → Creates project: "Project Name - Feature Name"
       ↓
6. Markdown Generator → Complete documentation
```

### **6. Jira Project Creation:**

When Jira credentials are configured, the system will create:
- **Project Name:** `{project_name} - {feature_name}` (e.g., "E-Commerce Platform - Shopping Cart Management")
- **Project Key:** `TP{MMDD}` (e.g., "TP0911")
- **Board:** Scrum board for the project
- **Issues:** Decomposed tasks from user stories
- **Subtasks:** Detailed subtasks for each main task
- **Sprint:** First sprint with assigned tasks

### **7. Environment Variables Required:**

```env
# Required for AI processing
GOOGLE_API_KEY=your_google_api_key_here

# Optional for Jira integration
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@domain.com
JIRA_API_TOKEN=your_jira_api_token_here
```

### **8. Testing Commands:**

```bash
# Test complete workflow
python test_complete_workflow.py

# Test task execution integration
python test_task_execution_integration.py

# Test basic workflow
python test_unified_workflow.py
```

### **9. Key Improvements:**

1. **Dynamic Project Naming** - No more hardcoded "Task Planning Project"
2. **Clean Integration** - Task execution agent receives data from previous agents
3. **Proper Jira Setup** - Projects created with meaningful names
4. **Complete Workflow** - End-to-end automation from requirements to Jira

The system now provides complete project planning automation with proper naming and integration! 🎉
