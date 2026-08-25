import json
import logging
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class GitHubRepo:
    name: str
    full_name: str
    description: str
    html_url: str
    homepage: str
    language: str
    topics: list[str] = field(default_factory=list)
    stars_count: int = 0
    forks_count: int = 0
    is_fork: bool = False
    pushed_at: datetime | None = None
    created_at: datetime | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GitHubRepo":
        def parse_iso(val: str | None) -> datetime | None:
            if not val:
                return None
            try:
                return datetime.fromisoformat(val.replace("Z", "+00:00"))
            except ValueError:
                return None

        return cls(
            name=data.get("name") or "",
            full_name=data.get("full_name") or "",
            description=data.get("description") or "",
            html_url=data.get("html_url") or "",
            homepage=data.get("homepage") or "",
            language=data.get("language") or "",
            topics=data.get("topics") or [],
            stars_count=int(data.get("stargazers_count") or 0),
            forks_count=int(data.get("forks_count") or 0),
            is_fork=bool(data.get("fork")),
            pushed_at=parse_iso(data.get("pushed_at")),
            created_at=parse_iso(data.get("created_at")),
        )


class GitHubClient:
    BASE_URL = "https://api.github.com"

    def __init__(self, username: str, token: str | None = None) -> None:
        self.username = username
        self.token = token.strip() if token else None

    def _get_headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": f"portfolio-sync/{self.username}",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def get_user_repos(
        self,
        include_forks: bool = False,
        sort: str = "pushed",
        direction: str = "desc",
    ) -> list[GitHubRepo]:
        url = (
            f"{self.BASE_URL}/users/{self.username}/repos"
            f"?sort={sort}&direction={direction}&per_page=100"
        )
        req = urllib.request.Request(url, headers=self._get_headers())

        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            logger.error("GitHub API error: %s (status %s)", exc.reason, exc.code)
            raise
        except urllib.error.URLError as exc:
            logger.error("GitHub connection error: %s", exc.reason)
            raise

        repos: list[GitHubRepo] = []
        for item in payload:
            repo = GitHubRepo.from_dict(item)
            if not include_forks and repo.is_fork:
                continue
            repos.append(repo)

        return repos


def fetch_user_repositories(
    username: str,
    token: str | None = None,
    include_forks: bool = False,
) -> list[GitHubRepo]:
    client = GitHubClient(username=username, token=token)
    return client.get_user_repos(include_forks=include_forks)
