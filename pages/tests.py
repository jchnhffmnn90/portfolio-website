import pytest
from django.urls import reverse

from projects.models import Project


@pytest.mark.django_db
def test_home_page_status_code_and_template(client):
    response = client.get(reverse("pages:home"))
    assert response.status_code == 200
    assert "pages/home.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_home_page_displays_featured_projects(client):
    Project.objects.create(
        name="featured-one",
        github_url="https://github.com/testuser/featured-one",
        is_featured=True,
        is_visible=True,
    )
    Project.objects.create(
        name="normal-one",
        github_url="https://github.com/testuser/normal-one",
        is_featured=False,
        is_visible=True,
    )

    response = client.get(reverse("pages:home"))
    assert response.status_code == 200
    assert len(response.context["featured_projects"]) == 1
    assert response.context["featured_projects"][0].name == "featured-one"
    assert response.context["total_projects_count"] == 2


@pytest.mark.django_db
def test_home_page_fallback_top_starred(client):
    Project.objects.create(
        name="repo-star-5",
        github_url="https://github.com/testuser/repo-star-5",
        stars_count=5,
        is_featured=False,
        is_visible=True,
    )
    Project.objects.create(
        name="repo-star-10",
        github_url="https://github.com/testuser/repo-star-10",
        stars_count=10,
        is_featured=False,
        is_visible=True,
    )

    response = client.get(reverse("pages:home"))
    assert response.status_code == 200
    assert len(response.context["featured_projects"]) == 2
    assert response.context["featured_projects"][0].name == "repo-star-10"
