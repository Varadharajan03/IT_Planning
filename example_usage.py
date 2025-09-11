#!/usr/bin/env python3
"""
Example usage of the unified IT Planning Workflow API
"""
import requests
import json
import time

# API Configuration
API_BASE_URL = "http://localhost:8000"

def call_unified_workflow():
    """Example of calling the unified workflow API"""
    
    # Example project data
    project_data = {
        "project_name": "AI-Powered Customer Support System",
        "feature_name": "Automated Ticket Classification",
        "industry": "Technology",
        "target_users": "Customer support agents and managers",
        "business_context": "An AI system that automatically classifies and routes customer support tickets to appropriate departments"
    }
    
    print("🚀 Starting unified workflow...")
    print(f"Project: {project_data['project_name']}")
    print(f"Feature: {project_data['feature_name']}")
    print("-" * 50)
    
    try:
        # Make API call
        response = requests.post(
            f"{API_BASE_URL}/unified-workflow",
            json=project_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("success"):
                print("✅ Workflow completed successfully!")
                
                data = result.get("data", {})
                
                # Display summary
                summary = data.get("summary", {})
                print(f"\n📊 Project Summary:")
                print(f"   Project: {summary.get('project_name')}")
                print(f"   Feature: {summary.get('feature_name')}")
                print(f"   Risks Identified: {summary.get('total_risks')}")
                print(f"   User Stories: {summary.get('total_user_stories')}")
                print(f"   Test Cases: {summary.get('total_test_cases')}")
                
                # Display markdown file location
                markdown_file = data.get("markdown_file")
                if markdown_file:
                    print(f"\n📄 Complete documentation saved to: {markdown_file}")
                
                # Display sample outputs
                print(f"\n📋 PRD Overview:")
                prd_output = data.get("prd_output", {})
                prd = prd_output.get("prd", {})
                print(f"   {prd.get('overview', 'N/A')}")
                
                print(f"\n⚠️ Sample Risks:")
                risks = data.get("risk_analysis", [])
                for i, risk in enumerate(risks[:3], 1):  # Show first 3 risks
                    print(f"   {i}. {risk.get('risk_type', 'Unknown')} - {risk.get('severity', 'Unknown')}")
                
                print(f"\n🧪 Sample Test Cases:")
                test_artifacts = data.get("test_artifacts", {})
                user_stories = test_artifacts.get("userStories", [])
                for i, story in enumerate(user_stories[:2], 1):  # Show first 2 stories
                    print(f"   {i}. {story.get('storyId', 'Unknown')}: {story.get('description', 'N/A')}")
                    test_cases = story.get("testCases", [])
                    for j, tc in enumerate(test_cases[:1], 1):  # Show first test case
                        print(f"      - {tc.get('testCaseId', 'Unknown')}: {tc.get('description', 'N/A')}")
                
            else:
                print(f"❌ Workflow failed: {result.get('message')}")
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the API server is running on http://localhost:8000")
        print("   Run: python main.py")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def check_api_status():
    """Check if the API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code == 200:
            result = response.json()
            print("✅ API is running!")
            print(f"   {result.get('message')} v{result.get('version')}")
            return True
        else:
            print(f"❌ API returned status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ API is not running. Please start it with: python main.py")
        return False

if __name__ == "__main__":
    print("🔧 IT Planning Workflow API Example")
    print("=" * 40)
    
    # Check API status first
    if check_api_status():
        print("\n" + "=" * 40)
        call_unified_workflow()
    
    print("\n✨ Example completed!")
    print("\nTo run the API server:")
    print("   python main.py")
    print("\nTo test the workflow:")
    print("   python test_unified_workflow.py")
