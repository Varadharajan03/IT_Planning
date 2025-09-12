import streamlit as st
import requests
import json
import time
from datetime import datetime
import os

# Page configuration
st.set_page_config(
    page_title="IT Planning Workflow",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.375rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.375rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.375rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .workflow-step {
        background-color: #f8f9fa;
        border-left: 4px solid #007bff;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<h1 class="main-header">🚀 IT Planning Workflow System</h1>', unsafe_allow_html=True)

# Sidebar for configuration
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    
    # API Configuration
    st.markdown("### API Settings")
    api_url = st.text_input(
        "API Base URL",
        value="http://localhost:8000",
        help="Base URL for the IT Planning API"
    )
    
    # Check API connection
    if st.button("🔍 Test API Connection"):
        try:
            response = requests.get(f"{api_url}/", timeout=5)
            if response.status_code == 200:
                st.success("✅ API is running!")
                st.json(response.json())
            else:
                st.error(f"❌ API returned status {response.status_code}")
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Cannot connect to API: {str(e)}")
    
    st.markdown("---")
    
    # Workflow Information
    st.markdown("### Workflow Information")
    st.info("""
    This workflow will:
    1. 📋 Generate PRD & FRD documents
    2. ⚠️ Perform risk analysis
    3. 🧪 Generate test cases
    4. ⚙️ Execute task decomposition
    5. 🧠 Run resource optimization (Fast Mode: skipped)
    6. 📄 Generate markdown output
    
    **Fast Mode**: Optimized for speed and demonstration (2-3 minutes)
    **Full Mode**: Complete analysis with all features (5-15 minutes)
    """)

# Main content area
tab1, tab2, tab3 = st.tabs(["🚀 Run Workflow", "📊 View Results", "📚 Documentation"])

with tab1:
    st.markdown('<h2 class="section-header">Project Configuration</h2>', unsafe_allow_html=True)
    
    # Workflow Mode Selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info("""
        📝 **Instructions**: Fill in the required fields below and click "Start Unified Workflow" to begin the complete project planning process.
        
        **Required Fields**: Project Name and Feature Name  
        **Optional Fields**: Industry, Target Users, and Business Context (help improve the quality of generated documents)
        """)
    
    with col2:
        workflow_mode = st.selectbox(
            "Workflow Mode",
            ["Fast Mode (Recommended)", "Full Mode"],
            help="Fast Mode: Optimized for speed and demonstration (2-3 minutes)\nFull Mode: Complete analysis with all features (5-15 minutes)"
        )
    
    # Create form for workflow inputs
    with st.form("workflow_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            project_name = st.text_input(
                "Project Name *",
                placeholder="e.g., E-Commerce Platform",
                help="Name of the project (Required)",
                key="project_name_input"
            )
            
            feature_name = st.text_input(
                "Feature Name *",
                placeholder="e.g., Shopping Cart Management",
                help="Specific feature to be developed (Required)",
                key="feature_name_input"
            )
            
            industry = st.text_input(
                "Industry",
                placeholder="e.g., E-commerce, Healthcare, Finance",
                help="Industry domain (optional)"
            )
        
        with col2:
            target_users = st.text_area(
                "Target Users",
                placeholder="e.g., Online shoppers, Store managers, Administrators",
                help="Description of target users (optional)",
                height=100
            )
            
            business_context = st.text_area(
                "Business Context",
                placeholder="e.g., Increase online sales by 30%, improve user experience",
                help="Business goals and context (optional)",
                height=100
            )
        
        # Form status indicator
        if project_name and feature_name:
            st.success("✅ All required fields filled. Ready to start workflow!")
        else:
            st.warning("⚠️ Please fill in Project Name and Feature Name to enable workflow start.")
        
        # Submit button
        submitted = st.form_submit_button(
            "🚀 Start Unified Workflow",
            type="primary",
            use_container_width=True
        )
    
    # Process workflow when form is submitted
    if submitted:
        if not project_name or not feature_name:
            st.error("⚠️ Please fill in all required fields! Project Name and Feature Name are mandatory.")
        else:
            # Prepare request payload
            payload = {
                "project_name": project_name,
                "feature_name": feature_name,
                "industry": industry or "",
                "target_users": target_users or "",
                "business_context": business_context or ""
            }
            
            # Display workflow progress
            st.markdown('<h2 class="section-header">Workflow Execution</h2>', unsafe_allow_html=True)
            
            # Create progress containers
            progress_container = st.container()
            status_container = st.container()
            results_container = st.container()
            
            with progress_container:
                progress_bar = st.progress(0)
                status_text = st.empty()
            
            # Select API endpoint based on mode
            if "Fast Mode" in workflow_mode:
                endpoint = f"{api_url}/fast-unified-workflow"
                timeout = 120  # 2 minutes
                mode_text = "fast unified workflow"
            else:
                endpoint = f"{api_url}/unified-workflow"
                timeout = 300  # 5 minutes
                mode_text = "full unified workflow"
            
            # Workflow steps
            workflow_steps = [
                "📋 Generating PRD & FRD documents...",
                "⚠️ Performing risk analysis...",
                "🧪 Generating test cases...",
                "⚙️ Executing task decomposition...",
                "🧠 Running resource optimization...",
                "📄 Generating markdown output...",
                "✅ Workflow completed!"
            ]
            
            try:
                # Start workflow
                status_text.text(f"🚀 Starting {mode_text}...")
                progress_bar.progress(0.1)
                
                # Make API request
                response = requests.post(
                    endpoint,
                    json=payload,
                    timeout=timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get("success"):
                        # Display success message
                        st.markdown('<div class="success-box">', unsafe_allow_html=True)
                        st.success("🎉 Workflow completed successfully!")
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Update progress
                        progress_bar.progress(1.0)
                        status_text.text("✅ Workflow completed successfully!")
                        
                        # Store results in session state
                        st.session_state.workflow_results = result.get("data", {})
                        st.session_state.workflow_payload = payload
                        st.session_state.workflow_timestamp = datetime.now()
                        
                        # Display summary
                        with results_container:
                            st.markdown('<h3 class="section-header">Workflow Summary</h3>', unsafe_allow_html=True)
                            
                            summary = st.session_state.workflow_results.get("summary", {})
                            
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.metric("Project", summary.get("project_name", "N/A"))
                            
                            with col2:
                                st.metric("Feature", summary.get("feature_name", "N/A"))
                            
                            with col3:
                                st.metric("Risks Identified", summary.get("total_risks", 0))
                            
                            with col4:
                                st.metric("Test Cases", summary.get("total_test_cases", 0))
                            
                            # Show markdown file path
                            markdown_file = st.session_state.workflow_results.get("markdown_file", "")
                            if markdown_file and os.path.exists(markdown_file):
                                st.info(f"📄 Documentation generated: `{markdown_file}`")
                                
                                # Download button
                                with open(markdown_file, 'r', encoding='utf-8') as f:
                                    markdown_content = f.read()
                                
                                st.download_button(
                                    label="📥 Download Documentation",
                                    data=markdown_content,
                                    file_name=os.path.basename(markdown_file),
                                    mime="text/markdown"
                                )
                            
                            st.success("✅ Workflow completed! Check the 'View Results' tab for detailed output.")
                    
                    else:
                        st.error(f"❌ Workflow failed: {result.get('message', 'Unknown error')}")
                        progress_bar.progress(0)
                        status_text.text("❌ Workflow failed")
                
                else:
                    st.error(f"❌ API Error: {response.status_code} - {response.text}")
                    progress_bar.progress(0)
                    status_text.text("❌ API Error")
            
            except requests.exceptions.Timeout:
                st.error("⏰ Request timed out. The workflow might still be running. Please check the API logs.")
                progress_bar.progress(0)
                status_text.text("⏰ Request timed out")
            
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Request failed: {str(e)}")
                progress_bar.progress(0)
                status_text.text("❌ Request failed")

with tab2:
    st.markdown('<h2 class="section-header">Workflow Results</h2>', unsafe_allow_html=True)
    
    if 'workflow_results' not in st.session_state:
        st.info("👆 Please run a workflow first using the 'Run Workflow' tab.")
    else:
        results = st.session_state.workflow_results
        
        # Display timestamp
        if 'workflow_timestamp' in st.session_state:
            st.info(f"🕒 Workflow executed at: {st.session_state.workflow_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Tabs for different result sections
        result_tabs = st.tabs(["📋 PRD/FRD", "⚠️ Risk Analysis", "🧪 Test Cases", "⚙️ Task Execution", "🧠 Resource Optimization", "📄 Full Output"])
        
        with result_tabs[0]:
            st.markdown("### Product Requirements Document (PRD)")
            prd_output = results.get("prd_output", {})
            prd = prd_output.get("prd", {})
            
            if prd:
                st.markdown("#### Overview")
                st.write(prd.get("overview", "N/A"))
                
                st.markdown("#### Personas")
                for persona in prd.get("personas", []):
                    with st.expander(f"👤 {persona.get('name', 'Unknown')}"):
                        st.write(f"**Goals:** {', '.join(persona.get('goals', []))}")
                        st.write(f"**Pain Points:** {', '.join(persona.get('pain_points', []))}")
                
                st.markdown("#### Business Goals")
                for goal in prd.get("business_goals", []):
                    st.write(f"• {goal}")
                
                st.markdown("#### Success Metrics")
                for metric in prd.get("success_metrics", []):
                    st.write(f"• {metric}")
            else:
                st.warning("No PRD data available")
            
            st.markdown("### Functional Requirements Document (FRD)")
            frd = prd_output.get("frd", [])
            
            if frd:
                for i, frd_item in enumerate(frd, 1):
                    with st.expander(f"FR-{i}: {frd_item.get('title', 'Untitled')}"):
                        st.write(f"**Description:** {frd_item.get('description', 'N/A')}")
                        st.write(f"**Priority:** {frd_item.get('priority', 'N/A')}")
                        st.write("**Acceptance Criteria:**")
                        for criteria in frd_item.get('acceptanceCriteria', []):
                            st.write(f"• {criteria}")
            else:
                st.warning("No FRD data available")
        
        with result_tabs[1]:
            st.markdown("### Risk Analysis")
            risk_analysis = results.get("risk_analysis", [])
            
            if risk_analysis:
                for i, risk in enumerate(risk_analysis, 1):
                    with st.expander(f"Risk {i}: {risk.get('risk_type', 'Unknown Risk Type')}"):
                        st.write(f"**Severity:** {risk.get('severity', 'Unknown')}")
                        st.write(f"**Description:** {risk.get('description', 'No description available')}")
                        st.write(f"**Relevant Law:** {risk.get('law', 'N/A')}")
            else:
                st.warning("No risk analysis data available")
        
        with result_tabs[2]:
            st.markdown("### Test Cases")
            test_artifacts = results.get("test_artifacts", {})
            user_stories = test_artifacts.get("userStories", [])
            
            if user_stories:
                for story in user_stories:
                    with st.expander(f"📝 {story.get('storyId', 'Unknown ID')}: {story.get('description', 'No description')}"):
                        st.write("**Test Cases:**")
                        for test_case in story.get('testCases', []):
                            st.write(f"**{test_case.get('testCaseId', 'Unknown ID')}:** {test_case.get('description', 'No description')}")
                            st.write(f"**Type:** {test_case.get('type', 'Unknown')}")
                            st.write("**Steps:**")
                            for step in test_case.get('steps', []):
                                st.write(f"1. {step}")
                            st.write(f"**Expected Result:** {test_case.get('expectedResult', 'N/A')}")
                            st.write("---")
            else:
                st.warning("No test cases data available")
        
        with result_tabs[3]:
            st.markdown("### Task Execution")
            task_execution = results.get("task_execution", {})
            
            if task_execution:
                st.json(task_execution)
            else:
                st.warning("No task execution data available")
        
        with result_tabs[4]:
            st.markdown("### Resource Optimization")
            resource_optimization = results.get("resource_optimization", {})
            
            if resource_optimization:
                st.json(resource_optimization)
            else:
                st.warning("No resource optimization data available")
        
        with result_tabs[5]:
            st.markdown("### Complete Workflow Output")
            st.json(results)

with tab3:
    st.markdown('<h2 class="section-header">Documentation</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    ## IT Planning Workflow System
    
    This system provides a comprehensive workflow for IT project planning, including:
    
    ### Workflow Steps
    
    1. **📋 PRD/FRD Generation**
       - Creates Product Requirements Document
       - Generates Functional Requirements Document
       - Defines personas, business goals, and success metrics
    
    2. **⚠️ Risk Analysis**
       - Analyzes potential risks based on PRD
       - Searches for industry-specific risk information
       - Provides risk mitigation strategies
    
    3. **🧪 Test Case Generation**
       - Creates user stories from requirements
       - Generates comprehensive test cases
       - Covers functional and non-functional testing
    
    4. **⚙️ Task Execution**
       - Decomposes tasks from user stories
       - Prioritizes tasks based on business value
       - Sets up Jira project with issues and subtasks
    
    5. **🧠 Resource Optimization**
       - Analyzes team capacity and availability
       - Optimizes task allocation
       - Considers leave schedules and workload
    
    6. **📄 Documentation Generation**
       - Creates comprehensive markdown documentation
       - Includes all workflow outputs
       - Provides downloadable project documentation
    
    ### API Endpoints
    
    - **POST** `/fast-unified-workflow` - Run the fast workflow (recommended, 2-3 minutes)
    - **POST** `/unified-workflow` - Run the complete workflow (5-15 minutes)
    - **POST** `/resource-optimizer-gmail` - Run resource optimization with Gmail integration
    - **GET** `/` - API information and health check
    
    ### Required Fields
    
    - **Project Name**: Name of the project
    - **Feature Name**: Specific feature to be developed
    
    ### Optional Fields
    
    - **Industry**: Industry domain (e.g., E-commerce, Healthcare)
    - **Target Users**: Description of target users
    - **Business Context**: Business goals and context
    
    ### Usage
    
    1. Fill in the required project information
    2. Optionally provide additional context
    3. Click "Start Unified Workflow"
    4. Monitor progress in real-time
    5. View detailed results in the "View Results" tab
    6. Download the generated documentation
    
    ### Troubleshooting
    
    - Ensure the API server is running on the specified URL
    - Check that all required fields are filled
    - Monitor the API logs for detailed error information
    - For timeout issues, check if the workflow is still running on the server
    """)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        IT Planning Workflow System v4.1.0 | Built with Streamlit
    </div>
    """,
    unsafe_allow_html=True
)
