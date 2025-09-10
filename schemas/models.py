
class JiraTask(BaseModel):
    key: str
    summary: str
    priority: str
    assignee: str
    status: str
    dueDate: str | None

class ReallocationResult(BaseModel):
    reassignedTasks: List[Dict[str, Any]]
    targetUser: str
from pydantic import BaseModel, Field
from typing import List

# --- OUTPUT MODELS (To enforce a strict and predictable output structure) ---

class TestCase(BaseModel):
    """Defines the structure for a single test case."""
    testCaseId: str = Field(description="A unique identifier for the test case, e.g., TC-001.")
    description: str = Field(description="A brief summary of the test case's objective.")
    steps: List[str] = Field(description="The sequence of actions to perform the test.")
    expectedResult: str = Field(description="The expected outcome after executing the steps.")
    type: str = Field(description="The type of test, e.g., 'Positive' or 'Negative'.")

class UserStory(BaseModel):
    """Defines a user story with its corresponding test cases."""
    storyId: str = Field(description="A unique identifier for the user story, e.g., US-1.")
    description: str = Field(description="The user story in the format: 'As a [user], I want [goal] so that [benefit]'.")
    testCases: List[TestCase]

class OutputArtifacts(BaseModel):
    """The final JSON output structure containing all user stories and test cases."""
    userStories: List[UserStory]

class InputRequirements(BaseModel):
    projectName: str
    featureName: str
    prd: Dict[str, Any]
    frd: List[Dict[str, Any]]
