import sys
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.metrics import add_risk_flags, calculate_kpis, add_age_days
from src.summary_generator import generate_summary
from src.gitlab_client import GitLabClient

st.set_page_config(
    page_title="RepoPulse",
    page_icon="📊",
    layout="wide"
)

# -----------------------------
# App Title
# -----------------------------
st.title("RepoPulse — Engineering Workflow Analytics Dashboard")

st.write(
    """
    Monitor GitLab repository health, open issues, merge requests,
    and CI/CD pipeline status in one place.
    """
)

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("RepoPulse Settings")

project_name = st.sidebar.selectbox(
    "Select Project",
    ["repopulse-demo-project", "analytics-dashboard", "ml-experiment-repo"]
)

date_range = st.sidebar.selectbox(
    "Date Range",
    ["Last 7 days", "Last 30 days", "Last 90 days"]
)

data_mode = st.sidebar.radio(
    "Data Mode",
    ["Sample Data", "Live GitLab API"]
)

if data_mode == "Sample Data":
    st.sidebar.info("Currently using sample dashboard data.")
else:
    st.sidebar.info("Currently using live GitLab API data.")
st.sidebar.markdown("---")
st.sidebar.subheader("Filters")

issue_status_filter = st.sidebar.multiselect(
    "Issue Status",
    ["Open", "Closed"],
    default=["Open", "Closed"]
)

pipeline_status_filter = st.sidebar.multiselect(
    "Pipeline Status",
    ["success", "failed", "canceled"],
    default=["success", "failed", "canceled"]
)

mr_status_filter = st.sidebar.multiselect(
    "Merge Request Status",
    ["Open", "Merged"],
    default=["Open", "Merged"]
)

min_age_filter = st.sidebar.slider(
    "Minimum Age Days",
    min_value=0,
    max_value=30,
    value=0
)
# -----------------------------
# Load data
# -----------------------------
if data_mode == "Sample Data":
    issues_df = pd.read_csv("data/sample_issues.csv")
    pipelines_df = pd.read_csv("data/sample_pipelines.csv")
    mrs_df = pd.read_csv("data/sample_merge_requests.csv")

else:
    try:
        base_url = st.secrets["GITLAB_BASE_URL"]
        token = st.secrets["GITLAB_TOKEN"]
        project_id = st.secrets["GITLAB_PROJECT_ID"]

        client = GitLabClient(
            base_url=base_url,
            token=token,
            project_id=project_id
        )
        project_info = client.get_project_info()

        issues_df = client.get_issues()
        pipelines_df = client.get_pipelines()
        mrs_df = client.get_merge_requests()

        st.sidebar.success("Connected to GitLab API")

    except Exception as e:
        st.sidebar.error("Could not connect to GitLab API")
        st.error(f"GitLab API error: {e}")
        st.stop()

        
if data_mode == "Live GitLab API":
    st.subheader("GitLab Project Information")

    info_col1, info_col2, info_col3 = st.columns(3)

    info_col1.metric("Project", project_info["name"])
    info_col2.metric("Default Branch", project_info["default_branch"])
    info_col3.metric("Open Issues", project_info["open_issues_count"])

    st.markdown(f"[Open project in GitLab]({project_info['web_url']})")        

# -----------------------------
# Add age in days for live API data
# -----------------------------
issues_df = add_age_days(issues_df, date_column="created_at")
mrs_df = add_age_days(mrs_df, date_column="created_at")
pipelines_df = add_age_days(pipelines_df, date_column="created_at")


# -----------------------------
# Apply filters
# -----------------------------
filtered_issues_df = issues_df[
    (issues_df["status"].isin(issue_status_filter)) &
    (issues_df["age_days"] >= min_age_filter)
]

filtered_pipelines_df = pipelines_df[
    pipelines_df["status"].isin(pipeline_status_filter)
]

filtered_mrs_df = mrs_df[
    (mrs_df["status"].isin(mr_status_filter)) &
    (mrs_df["age_days"] >= min_age_filter)
]

# -----------------------------
# Add workflow health flags
# -----------------------------
filtered_issues_df, filtered_mrs_df, filtered_pipelines_df = add_risk_flags(
    filtered_issues_df,
    filtered_mrs_df,
    filtered_pipelines_df
)

# -----------------------------
# Calculate KPIs
# -----------------------------
kpis = calculate_kpis(
    filtered_issues_df,
    filtered_mrs_df,
    filtered_pipelines_df
)

open_issues = kpis["open_issues"]
stale_issues = kpis["stale_issues"]
unassigned_issues = kpis["unassigned_issues"]
open_merge_requests = kpis["open_merge_requests"]
delayed_reviews = kpis["delayed_reviews"]
failed_pipelines = kpis["failed_pipelines"]
health_score = kpis["health_score"]
# -----------------------------
# KPI Cards
# -----------------------------
st.subheader("Repository Health Overview")

col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric("Health Score", f"{health_score}/100")
col2.metric("Open Issues", open_issues)
col3.metric("Stale Issues", stale_issues)
col4.metric("Open MRs", open_merge_requests)
col5.metric("Delayed Reviews", delayed_reviews)
col6.metric("Failed Pipelines", failed_pipelines)
# -----------------------------
# Health Status
# -----------------------------
if health_score >= 80:
    st.success("Repository status: Healthy")
elif health_score >= 60:
    st.warning("Repository status: Needs attention")
else:
    st.error("Repository status: Critical")

# -----------------------------
# Tables
# -----------------------------
st.subheader("Recent Issues")
st.dataframe(filtered_issues_df, use_container_width=True)

st.subheader("Recent Pipelines")
st.dataframe(filtered_pipelines_df, use_container_width=True)

# -----------------------------
# Charts
# -----------------------------
st.subheader("Workflow Analytics")

chart_col1, chart_col2 = st.columns(2)

# Issue status chart
issue_status_counts = filtered_issues_df["status"].value_counts().reset_index()
issue_status_counts.columns = ["status", "Count"]

fig_issues = px.bar(
    issue_status_counts,
    x="status",
    y="Count",
    title="Issue Status Distribution",
    text="Count"
)

chart_col1.plotly_chart(fig_issues, use_container_width=True)
issue_risk_counts = filtered_issues_df["risk_flag"].value_counts().reset_index()
issue_risk_counts.columns = ["risk_flag", "Count"]

fig_issue_risk = px.bar(
    issue_risk_counts,
    x="risk_flag",
    y="Count",
    title="Issue Risk Flags",
    text="Count"
)

chart_col1.plotly_chart(fig_issue_risk, use_container_width=True)

# Pipeline status chart
pipeline_status_counts = filtered_pipelines_df["status"].value_counts().reset_index()
pipeline_status_counts.columns = ["status", "Count"]

fig_pipelines = px.pie(
    pipeline_status_counts,
    names="status",
    values="Count",
    title="Pipeline Status Distribution"
)

chart_col2.plotly_chart(fig_pipelines, use_container_width=True)

# -----------------------------
# Merge Request Activity
# -----------------------------
st.subheader("Merge Request Activity")

st.dataframe(filtered_mrs_df, use_container_width=True)

mr_col1, mr_col2 = st.columns(2)

fig_mr_age = px.bar(
    filtered_mrs_df,
    x="title",
    y="age_days",
    color="status",
    title="Merge Request Age by Status"
)

mr_col1.plotly_chart(fig_mr_age, use_container_width=True)

mr_status_counts = filtered_mrs_df["status"].value_counts().reset_index()
mr_status_counts.columns = ["status", "Count"]

fig_mr_status = px.bar(
    mr_status_counts,
    x="status",
    y="Count",
    title="Merge Request Status Distribution",
    text="Count"
)

mr_col2.plotly_chart(fig_mr_status, use_container_width=True)
mr_risk_counts = filtered_mrs_df["risk_flag"].value_counts().reset_index()
mr_risk_counts.columns = ["risk_flag", "Count"]

fig_mr_risk = px.bar(
    mr_risk_counts,
    x="risk_flag",
    y="Count",
    title="Merge Request Risk Flags",
    text="Count"
)

st.plotly_chart(fig_mr_risk, use_container_width=True)
# -----------------------------
# Automated summary
# -----------------------------
st.subheader("Automated Workflow Summary")

summary = generate_summary(project_name, kpis)

st.info(summary)
# -----------------------------
# Downloadable Reports
# -----------------------------
st.subheader("Download Reports")

download_col1, download_col2, download_col3, download_col4 = st.columns(4)

download_col1.download_button(
    label="Download Issues CSV",
    data=filtered_issues_df.to_csv(index=False),
    file_name="repopulse_issues_report.csv",
    mime="text/csv"
)

download_col2.download_button(
    label="Download Merge Requests CSV",
    data=filtered_mrs_df.to_csv(index=False),
    file_name="repopulse_merge_requests_report.csv",
    mime="text/csv"
)

download_col3.download_button(
    label="Download Pipelines CSV",
    data=filtered_pipelines_df.to_csv(index=False),
    file_name="repopulse_pipelines_report.csv",
    mime="text/csv"
)

download_col4.download_button(
    label="Download Summary TXT",
    data=summary,
    file_name="repopulse_workflow_summary.txt",
    mime="text/plain"
)

# -----------------------------
# About Section
# -----------------------------
with st.expander("About RepoPulse"):
    st.write(
        """
        RepoPulse is an engineering workflow analytics dashboard built with Python,
        Streamlit, pandas, Plotly, and GitLab-style project data.

        The dashboard monitors repository health using issue activity, merge request
        bottlenecks, and CI/CD pipeline status. It calculates workflow risk flags,
        generates a repository health score, and creates an automated summary to
        support repository maintenance and QA follow-up.

        This version uses sample data. A later version can connect directly to the
        GitLab API for live project monitoring.
        """
    )