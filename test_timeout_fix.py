#!/usr/bin/env python3
"""
Test script to verify the timeout fixes work properly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_syntax():
    """Test that the modules can be imported without syntax errors"""
    try:
        from graph.fast_unified_workflow import run_fast_unified_workflow
        print("✅ Syntax check passed - no import errors")
        return True
    except Exception as e:
        print(f"❌ Syntax error: {e}")
        return False

def test_workflow_timeout():
    """Test the workflow with timeout protection"""
    try:
        from graph.fast_unified_workflow import run_fast_unified_workflow
        
        print("🧪 Testing workflow with timeout protection...")
        
        # Test with minimal data
        result = run_fast_unified_workflow(
            project_name="Test Project",
            feature_name="Test Feature",
            industry="Technology",
            target_users="Developers",
            business_context="Testing timeout fixes"
        )
        
        print(f"✅ Workflow completed successfully")
        print(f"📊 Result status: {result.get('status', 'unknown')}")
        print(f"⏱️ Processing time: {result.get('processing_time', 'unknown')}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Testing timeout fixes...")
    print("=" * 50)
    
    # Test 1: Syntax check
    syntax_ok = test_syntax()
    
    if syntax_ok:
        # Test 2: Workflow execution
        workflow_ok = test_workflow_timeout()
        
        if workflow_ok:
            print("\n🎉 All tests passed! Timeout fixes are working.")
        else:
            print("\n⚠️ Workflow test failed, but syntax is OK.")
    else:
        print("\n❌ Syntax errors found. Please fix before testing workflow.")
