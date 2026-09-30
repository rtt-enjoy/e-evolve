"""
Token‑aware GitHub API client for improved rate limits in code_techs.

Provides a simple wrapper around the GitHub REST API that automatically
adds an Authorization header when a GITHUB_TOKEN secret is present.
"""
import os
from typing import Any, Dict, Optional

import requests

GITHUB_API_BASE = "https://api.github.com"

class GitHubClient:
    def __init__(self, token: Optional[str] = None) -> None:
        self.token = token.strip() if token else None
        self.session = requests.Session()
        if self.token:
            self.session.headers.update({"Authorization": f"token {self.token}"})
        self.session.headers.update({"Accept": "application/vnd.github.v3+json"})

    def get(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform a GET request and return JSON response."""
        resp = self.session.get(url, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def search_repositories(self, query: str, per_page: int = 8) -> Dict[str, Any]:
        """Search GitHub repositories using the search/repositories endpoint."""
        url = f"{GITHUB_API_BASE}/search/repositories"
        return self.get(url, params={"q": query, "per_page": per_page})

    def get_user(self, username: str) -> Dict[str, Any]:
        """Fetch user information."""
        url = f"{GITHUB_API_BASE}/users/{username}"
        return self.get(url)

# Convenience instance using the GITHUB_TOKEN secret if present.
_token = os.getenv("GITHUB_TOKEN")
client = GitHubClient(token=_token)