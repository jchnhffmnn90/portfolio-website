import io
import json
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.urls import reverse

from projects.models import Project
from projects.services.github import GitHubClient, GitHubRepo, fetch_user_repositories
from projects.services.sync import sync_projects_from_github


@pytest.mark.django_db
def test_project_creation_and_auto_slug():
    project = Project.objects.create(
        name="Awesome Portfolio",
        github_url="https://github.com/testuser/awesome-portfolio",
        language="Python",
        stars_count=10,
    )

    assert str(project) == "Awesome Portfolio"
    assert project.slug == "awesome-portfolio"
    assert project.stars_count == 10
    assert project.is_visible is True
    assert project.is_featured is False


@pytest.mark.django_db
def test_project_custom_slug_preserved():
    project = Project.objects.create(
        name="Awesome Portfolio",
        slug="custom-slug",
        github_url="https://github.com/testuser/awesome-portfolio",
    )

    assert project.slug == "custom-slug"


@pytest.mark.django_db
def test_sync_projects_from_github_creates_and_updates():
    fake_repos = [
        GitHubRepo(
            name="repo-one",
            full_name="testuser/repo-one",
            description="First repo",
            html_url="https://github.com/testuser/repo-one",
            homepage="",
            language="Python",
            topics=["django"],
            stars_count=3,
            forks_count=0,
            pushed_at=datetime(2024, 1, 1, tzinfo=UTC),
        ),
        GitHubRepo(
            name="repo-two",
            full_name="testuser/repo-two",
            description="Second repo",
            html_url="https://github.com/testuser/repo-two",
            homepage="https://two.example.com",
            language="TypeScript",
            topics=["vue"],
            stars_count=8,
            forks_count=2,
            pushed_at=datetime(2024, 1, 2, tzinfo=UTC),
        ),
    ]

    with patch("projects.services.sync.fetch_user_repositories", return_value=fake_repos):
        result = sync_projects_from_github(username="testuser")

    assert result.total == 2
    assert result.created == 2
    assert result.updated == 0
    assert Project.objects.count() == 2

    # Second sync with updated stars count
    fake_repos[0].stars_count = 15
    with patch("projects.services.sync.fetch_user_repositories", return_value=fake_repos):
        result_update = sync_projects_from_github(username="testuser")

    assert result_update.total == 2
    assert result_update.created == 0
    assert result_update.updated == 2
    assert Project.objects.get(name="repo-one").stars_count == 15


@pytest.mark.django_db
def test_sync_projects_missing_username_raises():
    with patch("projects.services.sync.settings") as mock_settings:
        mock_settings.GITHUB_USERNAME = None
        mock_settings.GITHUB_TOKEN = None
        with pytest.raises(ValueError, match="GitHub username"):
            sync_projects_from_github(username=None)


@pytest.mark.django_db
def test_sync_projects_management_command():
    fake_repos = [
        GitHubRepo(
            name="command-repo",
            full_name="testuser/command-repo",
            description="Command test repo",
            html_url="https://github.com/testuser/command-repo",
            homepage="",
            language="Python",
            topics=[],
            stars_count=1,
            forks_count=0,
        )
    ]

    out = io.StringIO()
    with patch("projects.services.sync.fetch_user_repositories", return_value=fake_repos):
        call_command("sync_projects", username="testuser", stdout=out)

    output = out.getvalue()
    assert "Successfully synced projects" in output
    assert Project.objects.filter(name="command-repo").exists()


@pytest.mark.django_db
def test_sync_projects_management_command_error():
    with patch(
        "projects.management.commands.sync_projects.sync_projects_from_github",
        side_effect=ValueError("Invalid user"),
    ):
        with pytest.raises(CommandError, match="Invalid user"):
            call_command("sync_projects", username="baduser")


@pytest.mark.django_db
def test_project_list_view_renders(client):
    Project.objects.create(
        name="visible-proj",
        github_url="https://github.com/testuser/visible-proj",
        is_visible=True,
    )
    Project.objects.create(
        name="hidden-proj",
        github_url="https://github.com/testuser/hidden-proj",
        is_visible=False,
    )

    response = client.get(reverse("projects:list"))
    assert response.status_code == 200
    assert len(response.context["projects"]) == 1
    assert response.context["projects"][0].name == "visible-proj"


@pytest.mark.django_db
def test_project_list_view_search_and_filter(client):
    Project.objects.create(
        name="django-starter",
        description="A template for Django apps",
        language="Python",
        topics=["django"],
        stars_count=5,
        is_visible=True,
    )
    Project.objects.create(
        name="vue-frontend",
        description="Frontend components",
        language="TypeScript",
        topics=["vue"],
        stars_count=10,
        is_visible=True,
    )

    # Search query
    res_search = client.get(reverse("projects:list"), {"q": "django"})
    assert len(res_search.context["projects"]) == 1
    assert res_search.context["projects"][0].name == "django-starter"

    # Language filter
    res_lang = client.get(reverse("projects:list"), {"language": "TypeScript"})
    assert len(res_lang.context["projects"]) == 1
    assert res_lang.context["projects"][0].name == "vue-frontend"

    # Sort option
    res_sort = client.get(reverse("projects:list"), {"sort": "stars"})
    assert res_sort.context["projects"][0].name == "vue-frontend"


def test_github_repo_from_dict():
    sample_data = {
        "name": "my-cool-project",
        "full_name": "jchnhffmnn/my-cool-project",
        "description": "A demo project",
        "html_url": "https://github.com/jchnhffmnn/my-cool-project",
        "homepage": "https://demo.example.com",
        "language": "Python",
        "topics": ["django", "python"],
        "stargazers_count": 5,
        "forks_count": 1,
        "fork": False,
        "pushed_at": "2024-01-15T12:00:00Z",
        "created_at": "2023-01-01T10:00:00Z",
    }

    repo = GitHubRepo.from_dict(sample_data)

    assert repo.name == "my-cool-project"
    assert repo.language == "Python"
    assert repo.stars_count == 5
    assert repo.forks_count == 1
    assert repo.is_fork is False
    assert repo.topics == ["django", "python"]
    assert repo.pushed_at == datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC)


def test_github_client_filters_forks():
    client = GitHubClient(username="testuser")
    mock_payload = [
        {"name": "repo1", "fork": False, "stargazers_count": 2},
        {"name": "forked-repo", "fork": True, "stargazers_count": 0},
    ]

    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps(mock_payload).encode("utf-8")
    mock_response.__enter__.return_value = mock_response

    with patch("urllib.request.urlopen", return_value=mock_response):
        repos = client.get_user_repos(include_forks=False)

    assert len(repos) == 1
    assert repos[0].name == "repo1"


def test_fetch_user_repositories_helper():
    mock_payload = [{"name": "repo1", "fork": False}]
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps(mock_payload).encode("utf-8")
    mock_response.__enter__.return_value = mock_response

    with patch("urllib.request.urlopen", return_value=mock_response):
        repos = fetch_user_repositories(username="testuser")

    assert len(repos) == 1
    assert repos[0].name == "repo1"
