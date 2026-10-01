import json
import logging
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class GitHubAPIError(Exception):
    """Base exception for GitHub API communication failures."""


class GitHubRateLimitError(GitHubAPIError):
    """Raised when GitHub API rate limit is exceeded (HTTP 403 or 429)."""


@dataclass(slots=True)
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
                return datetime.fromisoformat(val)
            except ValueError:
                return None

        raw_topics = data.get("topics")
        topics = [str(t) for t in raw_topics] if isinstance(raw_topics, list) else []

        return cls(
            name=data.get("name") or "",
            full_name=data.get("full_name") or "",
            description=data.get("description") or "",
            html_url=data.get("html_url") or "",
            homepage=data.get("homepage") or "",
            language=data.get("language") or "",
            topics=topics,
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
        repos: list[GitHubRepo] = []
        page = 1
        per_page = 100

        while True:
            params = urllib.parse.urlencode(
                {
                    "sort": sort,
                    "direction": direction,
                    "per_page": per_page,
                    "page": page,
                }
            )
            encoded_username = urllib.parse.quote(self.username)
            url = f"{self.BASE_URL}/users/{encoded_username}/repos?{params}"
            req = urllib.request.Request(url, headers=self._get_headers())

            try:
                with urllib.request.urlopen(req, timeout=15) as response:
                    payload = json.loads(response.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                if exc.code in (403, 429):
                    logger.error("GitHub API rate limit exceeded: %s", exc)
                    raise GitHubRateLimitError("GitHub API rate limit exceeded.") from exc
                logger.error("GitHub API error: %s (status %s)", exc.reason, exc.code)
                raise GitHubAPIError(
                    f"GitHub API returned status {exc.code}: {exc.reason}"
                ) from exc
            except urllib.error.URLError as exc:
                logger.error("GitHub connection error: %s", exc.reason)
                raise GitHubAPIError(f"GitHub connection error: {exc.reason}") from exc

            if not isinstance(payload, list) or not payload:
                break

            for item in payload:
                if not isinstance(item, dict):
                    continue
                repo = GitHubRepo.from_dict(item)
                if not include_forks and repo.is_fork:
                    continue
                repos.append(repo)

            if len(payload) < per_page:
                break

            page += 1

        return repos


def fetch_user_repositories(
    username: str,
    token: str | None = None,
    include_forks: bool = False,
) -> list[GitHubRepo]:
    client = GitHubClient(username=username, token=token)
    return client.get_user_repos(include_forks=include_forks)
