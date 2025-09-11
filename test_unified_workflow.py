 #!/usr/bin/env python3
"""
Test script for the unified workflow
"""
import asyncio
import json
from main import app
from fastapi.testclient import TestClient

def test_unified_workflow():
    """Test the unified workflow endpoint"""
    client = TestClient(app)
    
    # Test data
    test_data = {
        "project_name": "E-Commerce Platform",
        "feature_name": "Shopping Cart Management",
        "industry": "Retail",
        "target_users": "Online shoppers and merchants",
        "business_context": "A modern e-commerce platform with advanced cart functionality"
    }
    
    print("🧪 Testing unified workflow...")
    print(f"Test data: {json.dumps(test_data, indent=2)}")
    
    try:
        # Test the unified workflow endpoint
        response = client.post("/unified-workflow", json=test_data)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Workflow completed successfully!")
            print(f"Success: {result.get('success')}")
            print(f"Message: {result.get('message')}")
            
            if result.get('data'):
                data = result['data']
                print(f"📄 Markdown file: {data.get('markdown_file')}")
                print(f"📊 Summary: {json.dumps(data.get('summary', {}), indent=2)}")
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

if __name__ == "__main__":
    print("🚀 Starting unified workflow tests...\n")
    
    # Test root endpoint first
    test_root_endpoint()
    
    # Test unified workflow
    test_unified_workflow()
    
    print("\n✨ Test completed!")
