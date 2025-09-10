from urllib import response
import requests
import logging
from typing import Dict, Any, Optional
from config.settings import JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN

# -------------------
# Logging
# -------------------
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# -------------------
# Jira Client Config
# -------------------
class JiraClient:
    def __init__(self, base_url: str, email: str, api_token: str):
        self.base_url = base_url.rstrip("/")
        self.auth = (email, api_token)
        self.headers = {"Accept": "application/json", "Content-Type": "application/json"}

    def _handle_error_response(self, response: requests.Response, operation: str):
        """Enhanced error handling with detailed response information"""
        try:
            error_details = response.json()
            logging.error(f"{operation} failed with status {response.status_code}")
            logging.error(f"Error details: {error_details}")
            
            # Common Jira error patterns
            if "errorMessages" in error_details:
                for msg in error_details["errorMessages"]:
                    logging.error(f"Error message: {msg}")
            
            if "errors" in error_details:
                for field, msg in error_details["errors"].items():
                    logging.error(f"Field '{field}': {msg}")
                    
        except Exception as e:
            logging.error(f"{operation} failed with status {response.status_code}")
            logging.error(f"Response text: {response.text}")
        
        response.raise_for_status()

    # -------------------
    # Get Available Project Types and Templates
    # -------------------
    def get_project_types(self) -> Dict[str, Any]:
        """Get available project types"""
        url = f"{self.base_url}/rest/api/3/project/type"
        response = requests.get(url, auth=self.auth, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        return []

    def get_project_templates(self) -> Dict[str, Any]:
        """Get available project templates"""
        url = f"{self.base_url}/rest/api/3/project/templates"
        response = requests.get(url, auth=self.auth, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        return []

    # -------------------
    # Check if project exists
    # -------------------
    def project_exists(self, project_key: str) -> bool:
        """Check if a project with the given key already exists"""
        url = f"{self.base_url}/rest/api/3/project/{project_key}"
        response = requests.get(url, auth=self.auth, headers=self.headers)
        return response.status_code == 200

    # -------------------
    # Create Project (Enhanced)
    # -------------------
    def create_project(self, key: str, name: str, lead_account_id: str, description: str = "Auto-created project") -> Dict[str, Any]:
        """
        Create a new Jira project with enhanced error handling and validation.
        """
        # Check if project already exists
        if self.project_exists(key):
            logging.warning(f"Project with key '{key}' already exists")
            url = f"{self.base_url}/rest/api/3/project/{key}"
            response = requests.get(url, auth=self.auth, headers=self.headers)
            return response.json()

        url = f"{self.base_url}/rest/api/3/project"
        
        # Simplified payload - start with basic project creation
        payload = {
            "key": key,
            "name": name,
            "projectTypeKey": "software",
            "description": description,
            "leadAccountId": lead_account_id,
            "assigneeType": "PROJECT_LEAD"
        }

        logging.info(f"Creating project with payload: {payload}")
        response = requests.post(url, json=payload, auth=self.auth, headers=self.headers)
        
        if response.status_code != 201:
            self._handle_error_response(response, "Project creation")
        
        return response.json()

    # -------------------
    # Create Filter (Enhanced)
    # -------------------
    def create_filter(self, name: str, jql: str, description: str = "") -> Dict[str, Any]:
        """Create a filter with enhanced error handling"""
        url = f"{self.base_url}/rest/api/3/filter"
        
        # Simplified payload
        payload = {
            "name": name,
            "jql": jql,
            "description": description,
            "favourite": True
        }
        
        logging.info(f"Creating filter with payload: {payload}")
        response = requests.post(url, json=payload, auth=self.auth, headers=self.headers)
        
        if response.status_code != 200:
            self._handle_error_response(response, "Filter creation")
        
        return response.json()

    # -------------------
    # Create Board (Enhanced)
    # -------------------
    def create_board(self, name: str, filter_id: int, board_type: str = "scrum") -> Dict[str, Any]:
        """Create a board with enhanced error handling"""
        url = f"{self.base_url}/rest/agile/1.0/board"
        
        payload = {
            "name": name,
            "type": board_type,
            "filterId": filter_id
        }
        
        logging.info(f"Creating board with payload: {payload}")
        response = requests.post(url, json=payload, auth=self.auth, headers=self.headers)
        
        if response.status_code != 201:
            self._handle_error_response(response, "Board creation")
        
        return response.json()

    # -------------------
    # Get Existing Board
    # -------------------
    def get_boards(self, project_key: str = None) -> Dict[str, Any]:
        """Get existing boards, optionally filtered by project"""
        url = f"{self.base_url}/rest/agile/1.0/board"
        if project_key:
            url += f"?projectKeyOrId={project_key}"
        
        response = requests.get(url, auth=self.auth, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        return {"values": []}

    # -------------------
    # Create Sprint (Enhanced)
    # -------------------
    def create_sprint(self, name: str, board_id: int, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Create a sprint with enhanced error handling"""
        url = f"{self.base_url}/rest/agile/1.0/sprint"
        
        # Basic payload - dates are optional
        payload = {
            "name": name,
            "originBoardId": board_id
        }
        
        # Add dates only if provided
        if start_date:
            payload["startDate"] = start_date
        if end_date:
            payload["endDate"] = end_date
        
        logging.info(f"Creating sprint with payload: {payload}")
        response = requests.post(url, json=payload, auth=self.auth, headers=self.headers)
        
        if response.status_code != 201:
            self._handle_error_response(response, "Sprint creation")
        
        return response.json()

    # -------------------
    # NEW: Issue Type Detection Methods
    # -------------------
    def get_project_issue_types(self, project_key: str):
        """Get available issue types for a specific project"""
        try:
            url = f"{self.base_url}/rest/api/3/project/{project_key}/issuetypescheme"
            response = requests.get(url, auth=self.auth, headers=self.headers)
            
            if response.status_code == 200:
                scheme_data = response.json()
                issue_types = []
                
                # Extract issue types from the scheme
                for scheme in scheme_data.get('values', []):
                    for issue_type in scheme.get('issueTypes', []):
                        issue_types.append({
                            'id': issue_type['id'],
                            'name': issue_type['name'],
                            'description': issue_type.get('description', ''),
                            'subtask': issue_type.get('subtask', False)
                        })
                
                return issue_types
            else:
                # Fallback: try to get issue types via create metadata
                return self._get_issue_types_fallback(project_key)
        
        except Exception as e:
            logging.error(f"Error getting project issue types: {e}")
            return self._get_issue_types_fallback(project_key)

    def _get_issue_types_fallback(self, project_key: str):
        """Fallback method to get issue types via create metadata"""
        try:
            url = f"{self.base_url}/rest/api/3/issue/createmeta"
            params = {
                'projectKeys': project_key,
                'expand': 'projects.issuetypes'
            }
            response = requests.get(url, auth=self.auth, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                issue_types = []
                
                for project in data.get('projects', []):
                    if project['key'] == project_key:
                        for issue_type in project.get('issuetypes', []):
                            issue_types.append({
                                'id': issue_type['id'],
                                'name': issue_type['name'],
                                'description': issue_type.get('description', ''),
                                'subtask': issue_type.get('subtask', False)
                            })
                        break
                
                return issue_types
            else:
                logging.error(f"Failed to get issue types via fallback: {response.status_code}")
                return []
        
        except Exception as e:
            logging.error(f"Error in fallback issue types: {e}")
            return []

    def find_best_issue_type(self, project_key: str, preferred_names: list):
        """Find the best matching issue type from preferred names"""
        available_types = self.get_project_issue_types(project_key)
        
        if not available_types:
            logging.error("No issue types available for project")
            return None
        
        # Log available types for debugging
        logging.info("Available issue types:")
        for itype in available_types:
            logging.info(f"  - {itype['name']} (ID: {itype['id']}, Subtask: {itype['subtask']})")
        
        # Try to find preferred types in order
        for preferred in preferred_names:
            for available in available_types:
                if available['name'].lower() == preferred.lower():
                    return available
        
        # If no preferred type found, return the first non-subtask type
        for available in available_types:
            if not available['subtask']:
                logging.warning(f"Using fallback issue type: {available['name']}")
                return available
        
        # Last resort: return first available type
        if available_types:
            logging.warning(f"Using first available issue type: {available_types[0]['name']}")
            return available_types[0]
        
        return None

    def create_issue_with_auto_type(self, project_key: str, summary: str, description: str = "", 
                                   assignee_id: str = None, parent_key: str = None, 
                                   preferred_types: list = None):
        """Create issue with automatic issue type detection"""
        
        if parent_key:
            # For subtasks, look for subtask types
            if not preferred_types:
                preferred_types = ['Sub-task', 'Subtask', 'Sub Task']
            
            # Get subtask types only
            available_types = self.get_project_issue_types(project_key)
            subtask_types = [t for t in available_types if t.get('subtask', False)]
            
            if subtask_types:
                issue_type = subtask_types[0]
            else:
                logging.error("No subtask types available")
                return None
        else:
            # For regular issues
            if not preferred_types:
                preferred_types = ['Story', 'Task', 'Bug', 'Epic']
            
            issue_type = self.find_best_issue_type(project_key, preferred_types)
            
            if not issue_type:
                logging.error("No suitable issue type found")
                return None
        
        # Create the issue with the found type (without assignee first)
        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": summary,
                "issuetype": {"id": issue_type['id']},
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": description
                                }
                            ]
                        }
                    ]
                } if description else None
            }
        }
        
        # Add parent if this is a subtask
        if parent_key:
            payload["fields"]["parent"] = {"key": parent_key}
        
        # Remove None values
        if not description:
            payload["fields"].pop("description", None)
        
        logging.info(f"Creating issue with type '{issue_type['name']}' (ID: {issue_type['id']})")
        logging.info(f"Payload: {payload}")
        
        try:
            url = f"{self.base_url}/rest/api/3/issue"
            response = requests.post(url, json=payload, auth=self.auth, headers=self.headers)
            
            if response.status_code == 201:
                issue_data = response.json()
                logging.info(f"Issue created successfully: {issue_data['key']}")
                
                # Try to assign after creation if assignee_id provided
                if assignee_id:
                    try:
                        self.assign_issue(issue_data['key'], assignee_id)
                        logging.info(f"Issue {issue_data['key']} assigned successfully")
                    except Exception as e:
                        logging.warning(f"Could not assign issue {issue_data['key']}: {e}")
                
                return issue_data
            else:
                self._handle_error_response(response, "Issue creation")
                return None
                
        except Exception as e:
            logging.error(f"Exception during issue creation: {e}")
            return None

    # -------------------
    # Create Issue (Enhanced - keeping original method for backward compatibility)
    # -------------------
    def create_issue(
        self,
        project_key: str,
        summary: str,
        issue_type: str = "Task",
        assignee_id: Optional[str] = None,
        parent_key: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create an issue with enhanced error handling"""
        url = f"{self.base_url}/rest/api/3/issue"
        
        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": summary,
                "issuetype": {"name": issue_type},
            }
        }

        if description:
            payload["fields"]["description"] = {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": description
                            }
                        ]
                    }
                ]
            }

        if parent_key:
            payload["fields"]["parent"] = {"key": parent_key}

        logging.info(f"Creating issue with payload: {payload}")
        response = requests.post(url, json=payload, auth=self.auth, headers=self.headers)
        
        if response.status_code != 201:
            self._handle_error_response(response, "Issue creation")
        
        return response.json()
    
    # -------------------
    # Assign Issue
    # -------------------
    def assign_issue(self, issue_key: str, assignee_id: str) -> Dict[str, Any]:
        """Assign an issue to a user"""
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}/assignee"
        payload = {"accountId": assignee_id}
        
        response = requests.put(url, json=payload, auth=self.auth, headers=self.headers)
        
        if response.status_code != 204:
            self._handle_error_response(response, f"Assign issue {issue_key}")
        
        return {"success": True}

    # -------------------
    # Move Issue to Sprint
    # -------------------
    def move_issue_to_sprint(self, sprint_id: int, issue_keys: list) -> Dict[str, Any]:
        """Move issues to a sprint"""
        url = f"{self.base_url}/rest/agile/1.0/sprint/{sprint_id}/issue"
        payload = {"issues": issue_keys}
        
        response = requests.post(url, json=payload, auth=self.auth, headers=self.headers)
        
        if response.status_code != 204:
            self._handle_error_response(response, f"Move issues to sprint {sprint_id}")
        
        return {"success": True}

    # -------------------
    # Get Account ID by Email
    # -------------------
    def get_account_id_by_email(self, email: str) -> str:
        url = f"{self.base_url}/rest/api/3/user/search?query={email}"
        response = requests.get(url, auth=self.auth, headers=self.headers)
        
        if response.status_code != 200:
            self._handle_error_response(response, f"User search for {email}")
        
        users = response.json()
        if not users:
            raise ValueError(f"No Jira user found for email: {email}")
        return users[0]["accountId"]

    # -------------------
    # Get own account ID (current user)
    # -------------------
    def get_my_account_id(self) -> str:
        url = f"{self.base_url}/rest/api/3/myself"
        response = requests.get(url, auth=self.auth, headers=self.headers)
        
        if response.status_code != 200:
            self._handle_error_response(response, "Get current user")
        
        return response.json()["accountId"]
    
    # -------------------
    # Diagnostic Methods
    # -------------------
    def test_connection(self) -> bool:
        """Test the connection to Jira"""
        try:
            url = f"{self.base_url}/rest/api/3/myself"
            response = requests.get(url, auth=self.auth, headers=self.headers)
            if response.status_code == 200:
                user_info = response.json()
                logging.info(f"Connected to Jira as: {user_info.get('displayName')} ({user_info.get('emailAddress')})")
                return True
            else:
                logging.error(f"Connection test failed with status: {response.status_code}")
                return False
        except Exception as e:
            logging.error(f"Connection test failed with exception: {e}")
            return False

    def get_permissions(self) -> Dict[str, Any]:
        """Get current user permissions"""
        url = f"{self.base_url}/rest/api/3/mypermissions"
        response = requests.get(url, auth=self.auth, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        return {}

jira = JiraClient(
    base_url=JIRA_BASE_URL,
    email=JIRA_EMAIL,
    api_token=JIRA_API_TOKEN
)