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
class Subtask(BaseModel):
    summary: str
    type: str
    estimated_hours: float

class Task(BaseModel):
    summary: str
    type: str
    estimated_hours: float
    subtasks: List[Subtask]

class TaskDecompositionOutput(BaseModel):
    tasks: List[Task]

# -------------------
# Step 2: Prioritization Schema
# -------------------
class SubtaskWithPriority(Subtask):
    priority: str  

class TaskWithPriority(Task):
    priority: str
    subtasks: List[SubtaskWithPriority]

class TaskPrioritizationOutput(BaseModel):
    tasks: List[TaskWithPriority]
