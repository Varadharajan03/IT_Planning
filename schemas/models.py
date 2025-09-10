from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class TestCase(BaseModel):
    testCaseId: str = Field(description="A unique identifier for the test case, e.g., TC-001.")
    description: str = Field(description="A brief summary of the test case's objective.")
    steps: List[str] = Field(description="The sequence of actions to perform the test.")
    expectedResult: str = Field(description="The expected outcome after executing the steps.")
    type: str = Field(description="The type of test, e.g., 'Positive' or 'Negative'.")

class UserStory(BaseModel):
    storyId: str = Field(description="A unique identifier for the user story, e.g., US-1.")
    description: str = Field(description="The user story in the format: 'As a [user], I want [goal] so that [benefit]'.")
    testCases: List[TestCase]

class OutputArtifacts(BaseModel):
    userStories: List[UserStory]

class InputRequirements(BaseModel):
    projectName: str
    featureName: str
    prd: Dict[str, Any]
    frd: List[Dict[str, Any]]

# -------------------
# Task Execution Schema
# -------------------
class UserStoryInput(BaseModel):
    userStories: List[Dict] = Field(description="List of user stories with test cases")

class TaskDecompositionOutputModel(BaseModel):
    tasks: List[Dict] = Field(description="List of decomposed tasks")

class TaskPrioritizationOutputModel(BaseModel):
    tasks: List[Dict] = Field(description="List of prioritized tasks")

class SprintPlanningOutput(BaseModel):
    first_sprint_tasks: List[Dict] = Field(description="Tasks assigned to the first sprint")
    total_sprints_required: int = Field(description="Total number of sprints required")

class JiraProjectInput(BaseModel):
    project_key: str = Field(description="Jira project key")
    project_name: str = Field(description="Jira project name")
    lead_email: str = Field(description="Email of the project lead")

class JiraProjectOutput(BaseModel):
    project: Optional[Dict] = Field(description="Jira project details")
    jira_filter: Optional[Dict] = Field(description="Jira filter details")
    board: Optional[Dict] = Field(description="Jira board details")

class JiraSprintOutput(BaseModel):
    sprint: Optional[Dict] = Field(description="Jira sprint details")