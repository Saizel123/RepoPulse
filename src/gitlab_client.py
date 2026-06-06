import requests
import pandas as pd


class GitLabClient:
    def __init__(self, base_url, token, project_id):
        self.base_url = base_url
        self.token = token
        self.project_id = project_id
        self.headers = {
            "PRIVATE-TOKEN": self.token
        }

    def _get(self, endpoint, params=None):
        url = f"{self.base_url}{endpoint}"

        response = requests.get(
            url,
            headers=self.headers,
            params=params,
            timeout=20
        )

        response.raise_for_status()
        return response.json()

    def get_project_info(self):
        endpoint = f"/projects/{self.project_id}"
        data = self._get(endpoint)

        return {
            "project_id": data.get("id"),
            "name": data.get("name"),
            "description": data.get("description"),
            "default_branch": data.get("default_branch"),
            "web_url": data.get("web_url"),
            "open_issues_count": data.get("open_issues_count")
        }

    def get_issues(self):
        endpoint = f"/projects/{self.project_id}/issues"
        data = self._get(endpoint, params={"per_page": 100})

        rows = []

        for issue in data:
            rows.append({
                "issue_id": issue.get("iid"),
                "title": issue.get("title"),
                "status": "Open" if issue.get("state") == "opened" else "Closed",
                "created_at": issue.get("created_at"),
                "updated_at": issue.get("updated_at"),
                "assignee": (
                    issue.get("assignee", {}).get("name")
                    if issue.get("assignee")
                    else "Unassigned"
                ),
                "label": ", ".join(issue.get("labels", [])),
                "web_url": issue.get("web_url")
            })

        return pd.DataFrame(
            rows,
            columns=[
                "issue_id",
                "title",
                "status",
                "created_at",
                "updated_at",
                "assignee",
                "label",
                "web_url"
            ]
        )

    def get_merge_requests(self):
        endpoint = f"/projects/{self.project_id}/merge_requests"
        data = self._get(endpoint, params={"per_page": 100})

        rows = []

        for mr in data:
            rows.append({
                "mr_id": mr.get("iid"),
                "title": mr.get("title"),
                "status": "Open" if mr.get("state") == "opened" else "Merged",
                "created_at": mr.get("created_at"),
                "updated_at": mr.get("updated_at"),
                "author": mr.get("author", {}).get("name"),
                "target_branch": mr.get("target_branch"),
                "source_branch": mr.get("source_branch"),
                "web_url": mr.get("web_url")
            })

        return pd.DataFrame(
            rows,
            columns=[
                "mr_id",
                "title",
                "status",
                "created_at",
                "updated_at",
                "author",
                "target_branch",
                "source_branch",
                "web_url"
            ]
        )

    def get_pipelines(self):
        endpoint = f"/projects/{self.project_id}/pipelines"
        data = self._get(endpoint, params={"per_page": 100})

        rows = []

        for pipeline in data:
            rows.append({
                "pipeline_id": pipeline.get("id"),
                "branch": pipeline.get("ref"),
                "status": pipeline.get("status"),
                "created_at": pipeline.get("created_at"),
                "updated_at": pipeline.get("updated_at"),
                "web_url": pipeline.get("web_url")
            })

        return pd.DataFrame(
            rows,
            columns=[
                "pipeline_id",
                "branch",
                "status",
                "created_at",
                "updated_at",
                "web_url"
            ]
        )