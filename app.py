import streamlit as st
from graph.resource_optimizer import run_workflow
from tools.gmail_utils import check_leave_mail

st.set_page_config(page_title="Jira Resource Optimizer", layout="wide")

st.title("📊 Jira Resource Optimization Agent")

st.markdown("This app monitors leave emails and reallocates tasks in Jira automatically.")

# Sidebar config
project_key = st.sidebar.text_input("Jira Project Key", value="TEST")

if st.button("Check for Leave Mail & Run Workflow"):
    with st.spinner("Checking Gmail for leave mail..."):
        leave_email = check_leave_mail()
        if not leave_email:
            st.warning("No new leave mails found 📭")
        else:
            st.success(f"Leave detected for: {leave_email}")
            result = run_workflow(project_key=project_key, leave_email=leave_email)

            st.subheader("Workflow Result")
            st.json(result)

# Option to upload team CSV
st.sidebar.subheader("Upload Project Team CSV")
uploaded_file = st.sidebar.file_uploader("Choose CSV file", type=["csv"])
if uploaded_file is not None:
    with open("team.csv", "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.sidebar.success("✅ Team CSV uploaded successfully")
