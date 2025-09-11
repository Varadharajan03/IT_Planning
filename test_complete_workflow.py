#!/usr/bin/env python3
"""
Test script for the complete unified workflow with task execution
"""
import asyncio
import json
from main import app
from fastapi.testclient import TestClient

def test_complete_workflow():
    """Test the complete unified workflow with task execution"""
    client = TestClient(app)
    
    # Test data
    test_data = {
        "project_name": "Smart Project Analytics Platform",
        "feature_name": "Dashboard Management System",
        "industry": "Technology",
        "target_users": "Project managers, team leads, and executives",
        "business_context": "An AI-powered project management platform with advanced analytics and reporting capabilities"
    }
    
    print("🚀 Testing complete unified workflow with task execution...")
    print(f"Test data: {json.dumps(test_data, indent=2)}")
    
    try:
        # Test the unified workflow endpoint
        response = client.post("/unified-workflow", json=test_data)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Complete workflow executed successfully!")
            print(f"Success: {result.get('success')}")
            print(f"Message: {result.get('message')}")
            
            if result.get('data'):
                data = result['data']
                print(f"📄 Markdown file: {data.get('markdown_file')}")
                
                # Display summary
                summary = data.get('summary', {})
                print(f"\n📊 Project Summary:")
                print(f"   Project: {summary.get('project_name')}")
                print(f"   Feature: {summary.get('feature_name')}")
                print(f"   Risks Identified: {summary.get('total_risks')}")
                print(f"   User Stories: {summary.get('total_user_stories')}")
                print(f"   Test Cases: {summary.get('total_test_cases')}")
                print(f"   Task Execution Status: {summary.get('task_execution_status')}")
                
                # Display task execution results
                task_execution = data.get('task_execution', {})
                if task_execution:
                    print(f"\n⚙️ Task Execution Results:")
                    print(f"   Status: {task_execution.get('status', 'Unknown')}")
                    result_text = task_execution.get('result', 'No result available')
                    if len(result_text) > 200:
                        print(f"   Result: {result_text[:200]}...")
                    else:
                        print(f"   Result: {result_text}")
                
                # Display sample outputs
                print(f"\n📋 PRD Overview:")
                prd_output = data.get('prd_output', {})
                prd = prd_output.get('prd', {})
                print(f"   {prd.get('overview', 'N/A')}")
                
                print(f"\n⚠️ Sample Risks:")
                risks = data.get('risk_analysis', [])
                for i, risk in enumerate(risks[:3], 1):  # Show first 3 risks
                    print(f"   {i}. {risk.get('risk_type', 'Unknown')} - {risk.get('severity', 'Unknown')}")
                
                print(f"\n🧪 Sample Test Cases:")
                test_artifacts = data.get('test_artifacts', {})
                user_stories = test_artifacts.get('userStories', [])
                for i, story in enumerate(user_stories[:2], 1):  # Show first 2 stories
                    print(f"   {i}. {story.get('storyId', 'Unknown')}: {story.get('description', 'N/A')}")
                    test_cases = story.get('testCases', [])
                    for j, tc in enumerate(test_cases[:1], 1):  # Show first test case
                        print(f"      - {tc.get('testCaseId', 'Unknown')}: {tc.get('description', 'N/A')}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception during test: {str(e)}")

def test_root_endpoint():
    """Test the root endpoint"""
    client = TestClient(app)
    
    print("\n🌐 Testing root endpoint...")
    response = client.get("/")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Root endpoint working!")
        print(f"API Info: {json.dumps(result, indent=2)}")
    else:
        print(f"❌ Root endpoint error: {response.status_code}")

def check_environment_variables():
    """Check if required environment variables are set"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    print("\n🔧 Checking environment variables...")
    
    required_vars = {
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
        "JIRA_BASE_URL": os.getenv("JIRA_BASE_URL"),
        "JIRA_EMAIL": os.getenv("JIRA_EMAIL"),
        "JIRA_API_TOKEN": os.getenv("JIRA_API_TOKEN")
    }
    
    all_set = True
    for var, value in required_vars.items():
        if value:
            print(f"✅ {var}: Set")
        else:
            print(f"❌ {var}: Not set")
            all_set = False
    
    if not all_set:
        print("\n⚠️  Some environment variables are missing. Please set them in your .env file:")
        print("   GOOGLE_API_KEY=your_google_api_key")
        print("   JIRA_BASE_URL=https://your-domain.atlassian.net")
        print("   JIRA_EMAIL=your-email@domain.com")
        print("   JIRA_API_TOKEN=your_jira_api_token")
        print("\n   Note: Jira variables are optional but required for task execution features.")
    else:
        print("\n✅ All environment variables are set!")
    
    return all_set

if __name__ == "__main__":
    print("🚀 Starting complete unified workflow tests...\n")
    
    # Check environment variables first
    env_ok = check_environment_variables()
    
    # Test root endpoint
    test_root_endpoint()
    
    # Test complete workflow
    test_complete_workflow()
    
    print("\n✨ Test completed!")
    print("\nTo run the API server:")
    print("   python main.py")
    print("\nTo test individual components:")
    print("   python test_unified_workflow.py")
