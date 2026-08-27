import logging
from dataclasses import dataclass

from django.conf import settings

from projects.models import Project
from projects.services.github import GitHubRepo, fetch_user_repositories

logger = logging.getLogger(__name__)


@dataclass
class SyncResult:
    created: int = 0
    updated: int = 0
    total: int = 0


def sync_projects_from_github(
    username: str | None = None,
    token: str | None = None,
    include_forks: bool = False,
) -> SyncResult:
    """
    Fetches repositories from GitHub and syncs them into the Project database model.
    """
    target_username = username or getattr(settings, "GITHUB_USERNAME", None)
    target_token = token if token is not None else getattr(settings, "GITHUB_TOKEN", None)

    if not target_username:
        raise ValueError("GitHub username not configured.")

    repos: list[GitHubRepo] = fetch_user_repositories(
        username=target_username,
        token=target_token,
        include_forks=include_forks,
    )

    result = SyncResult(total=len(repos))

    for repo in repos:
        defaults = {
            "description": repo.description or "",
            "github_url": repo.html_url,
            "homepage_url": repo.homepage,
            "language": repo.language or "",
            "topics": repo.topics,
            "stars_count": repo.stars_count,
            "forks_count": repo.forks_count,
            "pushed_at": repo.pushed_at,
        }

        _, created = Project.objects.update_or_create(
            name=repo.name,
            defaults=defaults,
        )

        if created:
            result.created += 1
            logger.info("Created new project: %s", repo.name)
        else:
            result.updated += 1
            logger.debug("Updated existing project: %s", repo.name)

    return result

