import requests
import os
from typing import Optional

class GitHubClient:
    def __init__(self, github_token: Optional[str] = None):
        self.github_token = github_token
        self.base_url = "https://api.github.com"
        
    def _get_auth_headers(self) -> dict:
        """Get authentication headers for GitHub API"""
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "ZenML-LaMetric-App"
        }
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
        return headers
    
    async def get_repo_stars(self, owner: str, repo: str) -> int:
        """Get the number of stars for a GitHub repository"""
        try:
            url = f"{self.base_url}/repos/{owner}/{repo}"
            response = requests.get(url, headers=self._get_auth_headers(), timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                star_count = data.get("stargazers_count", 0)
                print(f"GitHub stars for {owner}/{repo}: {star_count}")
                return star_count
            else:
                print(f"Failed to get GitHub stars: {response.status_code} - {response.text}")
                return 0
                
        except Exception as e:
            print(f"Error fetching GitHub stars: {e}")
            return 0