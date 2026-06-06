# RepoPulse — Engineering Workflow Analytics Dashboard

RepoPulse is a Streamlit dashboard for monitoring GitLab repository health using issues, merge requests, and CI/CD pipeline data.

## Project Overview

Software teams often manage tasks, code reviews, and pipeline results across different GitLab pages. RepoPulse combines this information into one analytics dashboard to identify workflow bottlenecks such as stale issues, delayed merge requests, failed pipelines, and unassigned tasks.

## Features

- GitLab-style workflow analytics dashboard
- Sample data mode for public demo
- Live GitLab API mode for real repository monitoring
- Issue, merge request, and pipeline tracking
- Repository health score
- Risk flags for stale issues, delayed reviews, and failed pipelines
- Interactive filters
- Automated workflow summary
- Downloadable CSV and TXT reports

## Tech Stack

- Python
- Streamlit
- pandas
- Plotly
- GitLab API
- requests
- YAML / CI-CD concepts

## Dashboard Sections

- Repository health overview
- Issue analytics
- Pipeline analytics
- Merge request analytics
- Workflow risk flags
- Automated summary
- Downloadable reports

## How to Run Locally

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

## Live demo
Please check it out!
{Live demo}[https://repopulse-k5dhfqx7its2kyufgfrzgs.streamlit.app/]
