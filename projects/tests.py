import json
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from projects.services.github import GitHubClient, GitHubRepo, fetch_user_repositories


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
    assert repo.pushed_at == datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)


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
