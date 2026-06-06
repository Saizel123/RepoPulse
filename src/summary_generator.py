def generate_summary(project_name, kpis):
    summary = f"""
The selected repository **{project_name}** has a workflow health score of **{kpis["health_score"]}/100**.

Current signals:
- **{kpis["open_issues"]} open issues**
- **{kpis["stale_issues"]} stale issues**
- **{kpis["unassigned_issues"]} unassigned issues**
- **{kpis["open_merge_requests"]} open merge requests**
- **{kpis["delayed_reviews"]} delayed merge request reviews**
- **{kpis["failed_pipelines"]} failed pipelines**

Recommended actions:
1. Review stale issues older than 14 days.
2. Assign owners to unassigned issues.
3. Prioritize merge requests waiting for review.
4. Investigate recent failed pipelines.
"""
    return summary