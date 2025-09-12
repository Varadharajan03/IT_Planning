# IT Planning Workflow - Streamlit UI

A user-friendly web interface for the IT Planning Workflow System that provides a complete project planning solution.

## Features

### 🚀 Unified Workflow Interface
- **Form-based Input**: Easy-to-use form fields for project configuration
- **Real-time Progress**: Live progress tracking during workflow execution
- **Results Visualization**: Comprehensive display of all workflow outputs
- **Documentation Download**: One-click download of generated markdown files

### 📋 Workflow Steps
1. **PRD/FRD Generation** - Product and Functional Requirements Documents
2. **Risk Analysis** - Comprehensive risk assessment and mitigation
3. **Test Case Generation** - User stories and test scenarios
4. **Task Execution** - Task decomposition and Jira integration
5. **Resource Optimization** - Team capacity and workload optimization
6. **Documentation Generation** - Complete project documentation

## Quick Start

### Prerequisites
- Python 3.8+
- All dependencies from `requirements.txt`

### Installation

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**
   
   **Option A: Use the startup script (Recommended)**
   ```bash
   python run_streamlit.py
   ```
   
   **Option B: Manual startup**
   
   Terminal 1 (API Backend):
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```
   
   Terminal 2 (Streamlit UI):
   ```bash
   streamlit run streamlit_app.py --server.port 8501
   ```

3. **Access the Application**
   - **Streamlit UI**: http://localhost:8501
   - **API Documentation**: http://localhost:8000/docs

## Usage Guide

### 1. Project Configuration
Fill in the required fields in the "Run Workflow" tab:

**Required Fields:**
- **Project Name**: Name of your project (e.g., "E-Commerce Platform")
- **Feature Name**: Specific feature to develop (e.g., "Shopping Cart Management")

**Optional Fields:**
- **Industry**: Industry domain (e.g., "E-commerce", "Healthcare")
- **Target Users**: Description of target users
- **Business Context**: Business goals and context

### 2. Workflow Execution
1. Click "🚀 Start Unified Workflow"
2. Monitor real-time progress
3. View completion status and summary

### 3. Results Review
Navigate to the "View Results" tab to explore:
- **PRD/FRD**: Product and functional requirements
- **Risk Analysis**: Identified risks and mitigation strategies
- **Test Cases**: User stories and test scenarios
- **Task Execution**: Decomposed tasks and Jira setup
- **Resource Optimization**: Team allocation and capacity planning
- **Full Output**: Complete JSON output

### 4. Documentation
- Download generated markdown documentation
- View comprehensive project documentation
- Access API documentation and troubleshooting guides

## Configuration

### API Settings
- **Default API URL**: http://localhost:8000
- **Configurable**: Change in the sidebar settings
- **Connection Test**: Built-in API connectivity check

### Workflow Customization
- Adjust timeout settings for long-running workflows
- Configure progress tracking granularity
- Customize result display options

## Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Ensure the FastAPI backend is running on port 8000
   - Check the API URL in sidebar settings
   - Verify firewall settings

2. **Workflow Timeout**
   - Large projects may take longer to process
   - Check API logs for detailed progress
   - Consider breaking down complex features

3. **Missing Dependencies**
   - Run `pip install -r requirements.txt`
   - Ensure Python 3.8+ is installed
   - Check virtual environment activation

4. **Permission Errors**
   - Ensure write permissions for output files
   - Check file system access for markdown generation

### Debug Mode
Enable debug mode by setting environment variable:
```bash
export STREAMLIT_DEBUG=true
streamlit run streamlit_app.py
```

## API Integration

The Streamlit UI communicates with the FastAPI backend through REST API calls:

- **POST** `/unified-workflow` - Execute complete workflow
- **GET** `/` - API health check
- **POST** `/resource-optimizer-gmail` - Resource optimization with Gmail

## File Structure

```
├── streamlit_app.py          # Main Streamlit application
├── run_streamlit.py          # Startup script
├── main.py                   # FastAPI backend
├── requirements.txt          # Python dependencies
├── STREAMLIT_README.md       # This documentation
└── graph/
    └── unified_workflow.py   # Workflow implementation
```

## Advanced Features

### Session State Management
- Workflow results persist across page refreshes
- Form data is preserved during navigation
- Progress tracking maintains state

### Error Handling
- Comprehensive error messages
- Graceful failure handling
- User-friendly error displays

### Responsive Design
- Mobile-friendly interface
- Adaptive layout for different screen sizes
- Optimized for desktop and tablet use

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review API logs
3. Check the documentation tab in the UI
4. Create an issue in the repository

## License

This project is part of the IT Planning Workflow System. See the main project for licensing information.
