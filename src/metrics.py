from datetime import datetime, timezone

def classify_issue_risk(row):
    if row["status"] == "Open" and row["age_days"] > 14:
        return "Stale Issue"
    elif row["assignee"] == "Unassigned":
        return "Needs Owner"
    else:
        return "Normal"


def classify_mr_risk(row):
    if row["status"] == "Open" and row["age_days"] > 7:
        return "Delayed Review"
    else:
        return "Normal"


def classify_pipeline_risk(row):
    if row["status"] == "failed":
        return "Pipeline Failed"
    elif row["status"] == "canceled":
        return "Canceled"
    else:
        return "Normal"


def add_risk_flags(issues_df, mrs_df, pipelines_df):
    issues_df = issues_df.copy()
    mrs_df = mrs_df.copy()
    pipelines_df = pipelines_df.copy()

    issues_df["risk_flag"] = issues_df.apply(classify_issue_risk, axis=1)
    mrs_df["risk_flag"] = mrs_df.apply(classify_mr_risk, axis=1)
    pipelines_df["risk_flag"] = pipelines_df.apply(classify_pipeline_risk, axis=1)

    return issues_df, mrs_df, pipelines_df


def calculate_kpis(issues_df, mrs_df, pipelines_df):
    open_issues = len(issues_df[issues_df["status"] == "Open"])

    stale_issues = len(
        issues_df[
            (issues_df["status"] == "Open") &
            (issues_df["age_days"] > 14)
        ]
    )

    unassigned_issues = len(
        issues_df[issues_df["assignee"] == "Unassigned"]
    )

    open_merge_requests = len(
        mrs_df[mrs_df["status"] == "Open"]
    )

    delayed_reviews = len(
        mrs_df[mrs_df["risk_flag"] == "Delayed Review"]
    )

    failed_pipelines = len(
        pipelines_df[pipelines_df["status"] == "failed"]
    )

    health_score = 100
    health_score -= stale_issues * 5
    health_score -= unassigned_issues * 3
    health_score -= delayed_reviews * 6
    health_score -= failed_pipelines * 7
    health_score = max(0, health_score)

    return {
        "open_issues": open_issues,
        "stale_issues": stale_issues,
        "unassigned_issues": unassigned_issues,
        "open_merge_requests": open_merge_requests,
        "delayed_reviews": delayed_reviews,
        "failed_pipelines": failed_pipelines,
        "health_score": health_score
    }

def add_age_days(df, date_column="created_at"):
    df = df.copy()

    if date_column not in df.columns:
        return df

    def calculate_age(date_value):
        if not date_value:
            return 0

        created_date = datetime.fromisoformat(
            date_value.replace("Z", "+00:00")
        )

        now = datetime.now(timezone.utc)
        age = now - created_date

        return age.days

    df["age_days"] = df[date_column].apply(calculate_age)

    return df