# bot/github_api.py
# Minimal GitHub file fetch & update helper using aiohttp.
# Requires config.GITHUB_TOKEN and config.GITHUB_REPO to be set for write operations.

import aiohttp
import base64
import json
from typing import Optional
from .config import config
from .loader import logger

GITHUB_API_BASE = "https://api.github.com"

class GitHubAPI:
    def __init__(self, token: Optional[str], repo: Optional[str], branch: str = "main"):
        self.token = token
        self.repo = repo
        self.branch = branch

    async def _request(self, method: str, path: str, **kwargs):
        url = f"{GITHUB_API_BASE}{path}"
        headers = kwargs.pop("headers", {})
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        headers["Accept"] = "application/vnd.github+json"
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=headers, **kwargs) as resp:
                text = await resp.text()
                try:
                    data = await resp.json()
                except Exception:
                    data = text
                if resp.status >= 400:
                    logger.error("GitHub API error %s %s %s", resp.status, url, text)
                    raise RuntimeError(f"GitHub API error {resp.status}: {text}")
                return data

    async def get_file(self, path: str, ref: Optional[str] = None):
        """
        Get file metadata & content from repo.
        path: path/to/file.json (relative to repo root)
        """
        if not self.repo:
            raise RuntimeError("GITHUB_REPO not configured")
        ref_q = f"?ref={ref or self.branch}"
        api_path = f"/repos/{self.repo}/contents/{path}{ref_q}"
        data = await self._request("GET", api_path)
        # data contains 'content' base64
        content_b64 = data.get("content", "")
        encoding = data.get("encoding", "base64")
        sha = data.get("sha")
        if encoding == "base64":
            raw = base64.b64decode(content_b64).decode("utf-8")
            return {"content": raw, "sha": sha, "path": path}
        else:
            return {"content": content_b64, "sha": sha, "path": path}

    async def update_file(self, path: str, new_content: str, sha: str, message: str = "Update via bot"):
        """
        Update file at given path. new_content is raw string (utf-8).
        """
        if not self.repo:
            raise RuntimeError("GITHUB_REPO not configured")
        if not self.token:
            raise RuntimeError("GITHUB_TOKEN is required to update files")
        api_path = f"/repos/{self.repo}/contents/{path}"
        content_b64 = base64.b64encode(new_content.encode("utf-8")).decode("utf-8")
        body = {
            "message": message,
            "content": content_b64,
            "sha": sha,
            "branch": self.branch
        }
        data = await self._request("PUT", api_path, json=body)
        return data

    async def create_file(self, path: str, new_content: str, message: str = "Create via bot"):
        if not self.repo:
            raise RuntimeError("GITHUB_REPO not configured")
        if not self.token:
            raise RuntimeError("GITHUB_TOKEN is required to create files")
        api_path = f"/repos/{self.repo}/contents/{path}"
        content_b64 = base64.b64encode(new_content.encode("utf-8")).decode("utf-8")
        body = {
            "message": message,
            "content": content_b64,
            "branch": self.branch
        }
        data = await self._request("PUT", api_path, json=body)
        return data

# Convenience instance (import from other modules)
github_api = GitHubAPI(token=config.GITHUB_TOKEN, repo=config.GITHUB_REPO, branch=config.GITHUB_BRANCH)
