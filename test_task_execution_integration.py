#!/usr/bin/env python3
"""
Test script to verify task execution agent integration with project name
"""
from agents.task_execution_agent import TaskExecutionAgent

def test_task_execution_agent():
    """Test the task execution agent with project name from workflow"""
    
    # Sample user stories (simulating output from test case generator)
    sample_user_stories = {
        "userStories": [
            {
                "storyId": "US-1",
                "description": "As a user, I want to view project dashboard so that I can track progress",
                "testCases": [
                    {
                        "testCaseId": "TC-1.1",
                        "description": "Verify dashboard displays project status",
                        "steps": ["Login", "Navigate to dashboard", "View status"],
                        "expectedResult": "Dashboard shows project status",
                        "type": "Positive"
                    }
                ]
            }
        ]
    }
    
    # Test with project name from first agent
    project_name = "E-Commerce Platform - Shopping Cart Management"
    
    print(f"🧪 Testing TaskExecutionAgent with project name: {project_name}")
    
    try:
        # Create task execution agent
        task_agent = TaskExecutionAgent(
            user_stories=sample_user_stories,
            project_name=project_name,
            project_prefix="TP",
            lead_email="jeba.m.ihub@snsgroups.com"
        )
        
        print(f"✅ TaskExecutionAgent created successfully")
        print(f"   Project Name: {task_agent.project_name}")
        print(f"   Project Key: {task_agent.project_key}")
        print(f"   User Stories Count: {len(sample_user_stories['userStories'])}")
        
        # Note: We're not running the full execution here to avoid Jira API calls
        # In the actual workflow, this will be called by the unified workflow
        print(f"✅ Integration test passed - agent is ready for workflow")
        
    except Exception as e:
        print(f"❌ Error in task execution agent: {str(e)}")

if __name__ == "__main__":
    print("🚀 Testing Task Execution Agent Integration\n")
    test_task_execution_agent()
    print("\n✨ Test completed!")
