import streamlit as st
import requests
import json
import time
from datetime import datetime
import os
import threading
import queue

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
    # Company logo on the left sidebar
    logo_path = os.path.join("data", "sns-square-logo.png")
    if os.path.exists(logo_path):
        st.image(logo_path, width="stretch")
    
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
    1. 📋 Generate PRD & FRD documents (with BRD analysis)
    2. 🗏 Generate basic system architecture
    3. ⚠️ Perform risk analysis
    4. 🧪 Generate test cases
    5. ⚙️ Execute task decomposition
    6. 🧠 Run resource optimization (Fast Mode: skipped)
    7. 📄 Generate markdown output
    
    **BRD Support**: Upload Business Requirement Documents (PDF, Word, text files)
    **IT Industry Focus**: Specialized for IT projects and system development
    **Fast Mode**: Optimized for speed and demonstration (2-3 minutes)
    **Full Mode**: Complete analysis with all features (5-15 minutes)
    """)

# Initialize session state for document management
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []

# Main content area
tab1, tab2, tab3 = st.tabs(["🚀 Run Workflow", "📊 View Results", "📚 Documentation"])

with tab1:
    st.markdown('<h2 class="section-header">IT Project Configuration</h2>', unsafe_allow_html=True)
    
    # Workflow Mode Selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info("""
        📋 **Instructions**: Upload your Business Requirement Document (BRD) containing all project details.
        
        **Required Field**: BRD Upload (all project details should be in the BRD)
        **Optional Fields**: Technical metrics and team information to enhance analysis
        **Template Available**: Download BRD template above to structure your requirements
        """)
    
    with col2:
        workflow_mode = st.selectbox(
            "Workflow Mode",
            ["Fast Mode (Recommended)", "Full Mode"],
            help="Fast Mode: Optimized for speed and demonstration (2-3 minutes)\nFull Mode: Complete analysis with all features (5-15 minutes)"
        )
    
    # BRD template download (outside form)
    st.markdown("### 📥 Download BRD Template")
    st.info("Download the comprehensive Business Requirement Document template to structure your requirements before uploading.")
    try:
        with open("data/BRD_Template.docx", "rb") as f:
            template_content = f.read()
        st.download_button(
            label="📥 Download BRD Template",
            data=template_content,
            file_name="BRD_Template.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            help="Download the BRD template to structure your requirements"
        )
    except FileNotFoundError:
        st.warning("BRD template file not found. Please ensure the template file exists in the data folder.")
    
    st.markdown("---")
    
    # Document upload section (outside the form)
    st.markdown("### 📄 Business Requirement Document (BRD) Upload")
    st.info("Upload your Business Requirement Document to generate comprehensive PRD and FRD. The AI will analyze your BRD to create detailed technical requirements and system architecture.")
    
    uploaded_documents = st.file_uploader(
        "Upload BRD and Supporting Documents",
        accept_multiple_files=True,
        type=['pdf', 'docx', 'txt', 'doc'],
        help="Upload your BRD and any supporting documents (PDF, Word, text files)",
        key="doc_uploader"
    )
    
    # Update session state when files are uploaded
    if uploaded_documents:
        st.session_state.uploaded_files = uploaded_documents
    
    # Display uploaded files with remove functionality (outside form)
    if st.session_state.uploaded_files:
        st.markdown("**Uploaded Documents:**")
        files_to_remove = []
        
        for i, doc in enumerate(st.session_state.uploaded_files):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"📄 {doc.name} ({doc.size} bytes)")
            with col2:
                if st.button("Remove", key=f"remove_{i}"):
                    files_to_remove.append(i)
            with col3:
                # Show file type
                file_extension = doc.name.split('.')[-1].lower()
                st.write(f"Type: {file_extension.upper()}")
        
        # Remove files that were marked for removal
        if files_to_remove:
            # Create new list without removed files
            remaining_files = [doc for i, doc in enumerate(st.session_state.uploaded_files) if i not in files_to_remove]
            st.session_state.uploaded_files = remaining_files
            st.rerun()
    
    # Create form for workflow inputs
    with st.form("workflow_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            number_of_users = st.number_input(
                "Expected Number of Users",
                min_value=0,
                value=1000,
                step=100,
                help="Expected number of users on the platform (optional)"
            )
            
            it_domain = st.selectbox(
                "IT Domain",
                ["Web Application", "Mobile Application", "Desktop Application", "API/Backend Service", 
                 "Data Analytics Platform", "Cloud Infrastructure", "DevOps Pipeline", "Security System", 
                 "Agentic AI System", "Other"],
                help="Type of IT system being developed (optional)"
            )
            
            team_size = st.number_input(
                "Team Size",
                min_value=0,
                value=5,
                step=1,
                help="Size of the development team (optional)"
            )
            
            technology_stack = st.text_input(
                "Preferred Technology Stack",
                placeholder="e.g., React, Node.js, PostgreSQL, AWS",
                help="Preferred technologies, frameworks, or platforms (optional)"
            )
        
        with col2:
            ui_ux_preferences = st.selectbox(
                "UI/UX Preferences",
                ["Modern & Clean", "Corporate & Professional", "Mobile-First", "Accessibility-Focused", 
                 "Data-Heavy Dashboard", "Consumer-Friendly", "Enterprise", "Minimalist", "AI-Focused", "Other"],
                help="Preferred UI/UX style and approach (optional)"
            )
            
            compliance_requirements = st.text_input(
                "Compliance Requirements",
                placeholder="e.g., GDPR, HIPAA, SOX, PCI-DSS",
                help="Regulatory or compliance requirements (optional)"
            )
            
            timeline = st.text_input(
                "Timeline",
                placeholder="e.g., 6 months, Q1 2024, 12 weeks",
                help="Project timeline and delivery expectations (optional)"
            )
            
            budget = st.text_input(
                "Budget",
                placeholder="e.g., $50,000, €100K, £75,000",
                help="Project budget or budget range (optional)"
            )
        
        # Form status indicator
        if st.session_state.uploaded_files:
            st.success("✅ BRD uploaded. Ready to start workflow! Optional fields can enhance the analysis.")
        else:
            st.warning("⚠️ Please upload a BRD document containing all project details.")
        
        # Submit button
        submitted = st.form_submit_button(
            "🚀 Start Unified Workflow",
            type="primary",
            use_container_width=True
        )
    
    # Process workflow when form is submitted
    if submitted:
        if not st.session_state.uploaded_files:
            st.error("⚠️ Please upload a BRD document containing all project details!")
        else:
            # Process uploaded documents
            documents_data = []
            if st.session_state.uploaded_files:
                for doc in st.session_state.uploaded_files:
                    try:
                        # Read document content based on file type
                        if doc.type == "text/plain":
                            content = str(doc.read(), "utf-8")
                        elif doc.type == "application/pdf":
                            # For PDF files, we'll store metadata and let the backend handle processing
                            content = f"PDF Document: {doc.name}"
                        elif doc.type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
                            # For Word documents, we'll store metadata and let the backend handle processing
                            content = f"Word Document: {doc.name}"
                        else:
                            # Fallback for other types
                            content = f"Document: {doc.name}"
                        
                        documents_data.append({
                            "name": doc.name,
                            "type": doc.type,
                            "size": doc.size,
                            "content": content[:1000] if len(content) > 1000 else content  # Limit content size
                        })
                    except Exception as e:
                        st.warning(f"⚠️ Could not process document {doc.name}: {str(e)}")
            
            # Prepare request payload
            payload = {
                "project_name": "BRD-Based Project",  # Default since project details are in BRD
                "feature_name": "BRD Analysis",  # Default since details are in BRD
                "industry": "IT/Technology",  # Focus on IT industry
                "target_users": f"Expected users: {number_of_users}",  # Use number of users
                "business_context": f"Team size: {team_size}",  # Use team size
                "uploaded_documents": documents_data,
                "it_domain": it_domain,
                "technology_stack": technology_stack or "",
                "compliance_requirements": compliance_requirements or "",
                "timeline": timeline or "",
                "budget": budget or "",
                "ui_ux_preferences": ui_ux_preferences or "",
                "number_of_users": number_of_users,
                "team_size": team_size
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
                ui_timeout = 120  # used only for progress smoothing
                request_timeout = None  # no HTTP read timeout to prevent client-side aborts
                mode_text = "fast unified workflow"
            else:
                endpoint = f"{api_url}/unified-workflow"
                ui_timeout = 300  # used only for progress smoothing
                request_timeout = None  # no HTTP read timeout to prevent client-side aborts
                mode_text = "full unified workflow"
            
            # Workflow steps
            workflow_steps = [
                "📋 Analyzing BRD and generating PRD & FRD...",
                "🗏 Generating basic system architecture...",
                "⚠️ Performing risk analysis...",
                "🧪 Generating test cases...",
                "⚙️ Executing task decomposition...",
                "🧠 Running resource optimization...",
                "📄 Generating markdown output...",
                "✅ Workflow completed!"
            ]
            
            try:
                # Start workflow (run API call in background to allow live UI updates)
                status_text.text(f"🚀 Starting {mode_text}...")
                progress_bar.progress(0.05)

                response_queue: "queue.Queue[requests.Response]" = queue.Queue()
                error_queue: "queue.Queue[Exception]" = queue.Queue()

                def run_request():
                    try:
                        # No timeout so the request won't raise ReadTimeout on long server runs
                        resp = requests.post(endpoint, json=payload, timeout=request_timeout)
                        response_queue.put(resp)
                    except Exception as err:
                        error_queue.put(err)

                t = threading.Thread(target=run_request, daemon=True)
                t.start()

                # Live staged progress while request runs
                step_placeholders = [st.empty() for _ in workflow_steps]
                start_t = time.time()
                last_step = -1
                while t.is_alive():
                    elapsed = time.time() - start_t
                    # Evenly distribute progress across steps using UI timeout hint
                    step_idx = int(min(len(workflow_steps) - 1, (elapsed / max(1, ui_timeout)) * len(workflow_steps)))
                    # Update step states
                    for i, placeholder in enumerate(step_placeholders):
                        if i < step_idx:
                            placeholder.markdown(f"<div class='workflow-step'>✅ {workflow_steps[i]}</div>", unsafe_allow_html=True)
                        elif i == step_idx:
                            placeholder.markdown(f"<div class='workflow-step'>⏳ {workflow_steps[i]}</div>", unsafe_allow_html=True)
                        else:
                            placeholder.markdown(f"<div class='workflow-step'>• {workflow_steps[i]}</div>", unsafe_allow_html=True)
                    # Smooth progress bar; cap below 1.0 while waiting
                    progress_bar.progress(min(0.98, elapsed / max(1, ui_timeout)))
                    time.sleep(0.2)

                # Thread finished; check results
                if not error_queue.empty():
                    err = error_queue.get()
                    st.error(f"❌ Request failed: {str(err)}")
                    progress_bar.progress(0)
                    status_text.text("❌ Request failed")
                else:
                    response = response_queue.get()
                    if response.status_code == 200:
                        result = response.json()
                        if result.get("success"):
                            # Mark all steps complete
                            for i, placeholder in enumerate(step_placeholders):
                                placeholder.markdown(f"<div class='workflow-step'>✅ {workflow_steps[i]}</div>", unsafe_allow_html=True)
                            progress_bar.progress(1.0)
                            status_text.text("✅ Workflow completed successfully!")

                            # Store results
                            st.session_state.workflow_results = result.get("data", {})
                            st.session_state.workflow_payload = payload
                            st.session_state.workflow_timestamp = datetime.now()

                            # Post-process: show per-stage confirmations based on payload
                            results = st.session_state.workflow_results
                            with results_container:
                                st.markdown('<h3 class="section-header">Workflow Summary</h3>', unsafe_allow_html=True)

                                summary = results.get("summary", {})
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric("Project", summary.get("project_name", payload.get("project_name", "N/A")))
                                with col2:
                                    st.metric("Feature", summary.get("feature_name", payload.get("feature_name", "N/A")))
                                with col3:
                                    st.metric("Risks Identified", summary.get("total_risks", len(results.get("risk_analysis", []))))
                                with col4:
                                    total_cases = summary.get("total_test_cases")
                                    if total_cases is None:
                                        total_cases = sum(len(s.get("testCases", [])) for s in results.get("test_artifacts", {}).get("userStories", []))
                                    st.metric("Test Cases", total_cases)

                                # Jira hint if task execution ran
                                if results.get("task_execution_output") or results.get("task_execution"):
                                    st.info("🗷 Jira tasks may have been created/updated. Please check in Jira for the latest task updates.")

                                # Markdown file (fast workflow returns path)
                                markdown_file = results.get("markdown_file", "")
                                if markdown_file and os.path.exists(markdown_file):
                                    st.info(f"📄 Documentation generated: `{markdown_file}`")
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
                # We set no timeout; this is a safety net. Keep UI alive without failing.
                st.warning("⏳ Still processing... keeping connection open. The server is working on your request.")
                status_text.text("⏳ Still processing...")
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
            st.info(f"🕐 Workflow executed at: {st.session_state.workflow_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        
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
            st.markdown("### System Architecture")
            architecture = results.get("system_architecture", {})
            
            if architecture:
                st.markdown("#### Architecture Overview")
                st.write(architecture.get("overview", "No overview available"))
                
                st.markdown("#### Technology Stack")
                tech_stack = architecture.get("technology_stack", {})
                if tech_stack:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Frontend:**")
                        st.write(tech_stack.get("frontend", "Not specified"))
                        st.markdown("**Backend:**")
                        st.write(tech_stack.get("backend", "Not specified"))
                    with col2:
                        st.markdown("**Database:**")
                        st.write(tech_stack.get("database", "Not specified"))
                        st.markdown("**Infrastructure:**")
                        st.write(tech_stack.get("infrastructure", "Not specified"))
                
                st.markdown("#### System Components")
                components = architecture.get("components", [])
                if components:
                    for component in components:
                        with st.expander(f"🗏 {component.get('name', 'Unknown Component')}"):
                            st.write(f"**Description:** {component.get('description', 'No description')}")
                            st.write(f"**Technology:** {component.get('technology', 'Not specified')}")
                            st.write(f"**Responsibility:** {component.get('responsibility', 'Not specified')}")
                
                st.markdown("#### Data Flow")
                data_flow = architecture.get("data_flow", "No data flow information available")
                st.write(data_flow)
            else:
                st.warning("No system architecture data available")
        
        with result_tabs[2]:
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
        
        with result_tabs[3]:
            st.markdown("### Test Cases")
            test_artifacts = results.get("test_artifacts", {})
            user_stories = test_artifacts.get("userStories", [])
            
            if user_stories:
                for story in user_stories:
                    with st.expander(f"📋 {story.get('storyId', 'Unknown ID')}: {story.get('description', 'No description')}"):
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
        
        with result_tabs[4]:
            st.markdown("### Task Execution")
            task_execution = results.get("task_execution", {})
            
            if task_execution:
                st.json(task_execution)
            else:
                st.warning("No task execution data available")
        
        with result_tabs[5]:
            st.markdown("### Resource Optimization")
            resource_optimization = results.get("resource_optimization", {})
            
            if resource_optimization:
                st.json(resource_optimization)
            else:
                st.warning("No resource optimization data available")
        
        with result_tabs[6]:
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
    
    ### Required Field
    
    - **BRD Upload**: Business Requirement Document containing all project details (Project Name, Product Description, Business About, Target Audience, etc.)
    
    ### Optional Fields (Enhance Analysis)
    
    - **Expected Number of Users**: Expected user count on the platform
    - **IT Domain**: Type of system (Web App, Mobile App, API, Agentic AI System, etc.)
    - **Team Size**: Size of the development team
    - **Technology Stack**: Preferred technologies and frameworks
    - **UI/UX Preferences**: Preferred UI/UX style and approach
    - **Compliance Requirements**: Regulatory requirements (GDPR, HIPAA, etc.)
    - **Timeline**: Project timeline and delivery expectations
    - **Budget**: Project budget or budget range
    
    ### BRD Template
    
    Download the comprehensive Business Requirement Document template to structure your requirements:
    - Complete IT industry-focused template
    - Covers all aspects from business context to technical requirements
    - Includes stakeholder analysis, functional/non-functional requirements
    - Provides sections for risk analysis and success metrics
    
    ### Usage
    
    1. Download the BRD template from the Documentation tab
    2. Fill out your Business Requirement Document using the template
    3. Upload your completed BRD and fill in project information
    4. Optionally provide IT-specific details (technology stack, compliance, etc.)
    5. Click "Start Unified Workflow"
    6. Monitor progress in real-time
    7. View detailed results including system architecture in the "View Results" tab
    8. Download the generated documentation
    
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